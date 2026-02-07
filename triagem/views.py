from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente, FeedbackTriagem, CustomUser, EntradaProntuario, AnexoPaciente, LogAcao, UnidadeSaude
from .forms import PacienteForm, CustomUserCreationForm, FeedbackTriagemForm, EntradaProntuarioForm, ValidacaoTriagemForm, ProfilePictureForm, AnexoPacienteForm, PacienteAdminEditForm, CadastroPeloAdminForm
from collections import Counter
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .ml.predict import predict_from_dict
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import admin_required, medico_required, atendente_required, enfermeiro_required, pode_editar_cadastro, pode_realizar_triagem_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField, Avg, F, DurationField, Count
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
import json
import secrets
import string

@login_required
def index_view(request):
    unidade_atual = request.user.unidade_saude    

    # --- 1. Dados para a Análise ---
    hoje = timezone.now().date()
    
    pacientes_aguardando_hoje = Paciente.objects.filter(
        unidade_saude=unidade_atual,
        status='Aguardando', 
        hora_chegada__date=hoje
    )
    
    # --- 2. Dados para a Análise (Cards de Resumo) ---
    # Métricas baseadas na fila de hoje
    total_aguardando = pacientes_aguardando_hoje.count()
    vermelhos_aguardando = pacientes_aguardando_hoje.filter(classificacao='Vermelho').count()
    laranjas_aguardando = pacientes_aguardando_hoje.filter(classificacao='Laranja').count()

    # Métricas de "snapshot" do sistema (não precisam ser filtradas por "hoje")
    total_em_atendimento = Paciente.objects.filter(status='Em atendimento', unidade_saude=unidade_atual).count()
    chegadas_hoje = Paciente.objects.filter(hora_chegada__date=hoje, unidade_saude=unidade_atual).count()
    concluidos_hoje = Paciente.objects.filter(
        unidade_saude=unidade_atual,
        status='Concluido', 
        hora_fim_atendimento__date=hoje
    ).count()

    # ==============================================================================
    #     NOVA MÉTRICA: CÁLCULO DO TEMPO MÉDIO DE ESPERA (FEITO EM PYTHON)
    # ==============================================================================
    # Primeiro, buscamos todos os pacientes que iniciaram atendimento hoje
    pacientes_atendidos_hoje = Paciente.objects.filter(
        unidade_saude=unidade_atual, # <-- FILTRO ADICIONADO
        hora_inicio_atendimento__date=hoje,
        hora_chegada__isnull=False
    )

    tempo_total_espera = datetime.timedelta(0)
    tempo_medio_timedelta = None

    # Verificamos se há pacientes para calcular a média, para evitar divisão por zero
    if pacientes_atendidos_hoje.exists():
        pacientes_validos_para_calculo = 0
        for p in pacientes_atendidos_hoje:
            # ADICIONAMOS UMA VERIFICAÇÃO PARA GARANTIR QUE AMBOS OS CAMPOS EXISTEM
            if p.hora_inicio_atendimento and p.hora_chegada:
                tempo_espera_paciente = p.hora_inicio_atendimento - p.hora_chegada
                tempo_total_espera += tempo_espera_paciente
                pacientes_validos_para_calculo += 1
        
        # Calculamos a média apenas com base nos pacientes que tinham dados válidos
        if pacientes_validos_para_calculo > 0:
            tempo_medio_timedelta = tempo_total_espera / pacientes_validos_para_calculo
        
        # Calculamos a média
        tempo_medio_timedelta = tempo_total_espera / len(pacientes_atendidos_hoje)

    # Formata o resultado para ficar mais legível (ex: "15 minutos")
    tempo_medio_formatado = "N/A"
    if tempo_medio_timedelta:
        total_seconds = int(tempo_medio_timedelta.total_seconds())
        # Impede a exibição de valores negativos caso haja algum dado inconsistente
        if total_seconds < 0:
            total_seconds = 0
            
        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        segundos = total_seconds % 60

        if horas > 0:
            tempo_medio_formatado = f"{horas} h, {minutos} min e {segundos} s"
        else:
            tempo_medio_formatado = f"{minutos} min e {segundos} s"

    # --- 2. Lógica da Lista de Pacientes Ordenada por Prioridade ---
    prioridade_classificacao = Case(
        When(classificacao='Vermelho', then=Value(1)),
        # ... (resto da sua lógica de ordenação)
        default=Value(6),
        output_field=IntegerField()
    )
    
    lista_pacientes_priorizada = pacientes_aguardando_hoje.annotate(
        prioridade=prioridade_classificacao
    ).order_by('prioridade', 'hora_chegada')

    # --- 3. Enviando tudo para o template ---
    context = {
        'total_aguardando': total_aguardando,
        'total_em_atendimento': total_em_atendimento,
        'concluidos_hoje': concluidos_hoje,
        'chegadas_hoje': chegadas_hoje,
        'vermelhos_aguardando': vermelhos_aguardando,
        'laranjas_aguardando': laranjas_aguardando,
        'tempo_medio_espera': tempo_medio_formatado, # <-- Enviando o valor formatado
        'pacientes': lista_pacientes_priorizada,
        'pagina_ativa': 'home',
    }
    
    return render(request, 'site/index.html', context)

@pode_realizar_triagem_required 
@login_required 
def create_view(request):
    unidade_atual = request.user.unidade_saude

    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)

            print(f"USUÁRIO LOGADO: {request.user}")
            print(f"UNIDADE DO USUÁRIO: {unidade_atual}")

            paciente.atendente = request.user 
            paciente.unidade_saude = unidade_atual

            paciente.save()

            return redirect('hosp:listar')
        else:
            print("Erros de validação:", form.errors)
            # Se der erro, mantemos na mesma página
            context = {
                'form': form,
                'pagina_ativa': 'triagem',
            }
            return render(request, 'site/criar.html', context)

    # Se for GET (primeiro acesso à página)
    else:
        form = PacienteForm()
        context = {
            'form': form,
            'pagina_ativa': 'triagem',
        }
        return render(request, 'site/criar.html', context)
    

@login_required        
def list_view(request):
    unidade_atual = request.user.unidade_saude    
    # A MUDANÇA ESTÁ AQUI: Excluímos os pacientes com status 'Pendente'
    pacientes = Paciente.objects.exclude(status='Pendente').order_by('-id')
    status_contagem = Counter(p.status for p in pacientes)
    return render(request, 'site/listar.html', {
        'pacientes': pacientes,
        'status_contagem': status_contagem,
        'pagina_ativa': 'pacientes'
    })

@login_required
def detail_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Lógica para o botão "Voltar" que já tínhamos
    fallback_url = reverse('hosp:listar')
    voltar_para_url = request.META.get('HTTP_REFERER', fallback_url)

    form_prontuario = EntradaProntuarioForm()
    form_anexo = AnexoPacienteForm()
    
    # Lógica para processar o formulário de nova entrada no prontuário
    # Apenas aceita POST de um usuário Médico
    if request.method == 'POST' and (request.user.tipo_usuario == 'MEDICO' or request.user.is_superuser):
        
        # NOVO: Verificamos qual botão de submit foi clicado
        if 'submit_prontuario' in request.POST:
            form_prontuario = EntradaProntuarioForm(request.POST) # Preenche o form de prontuário
            if form_prontuario.is_valid():
                nova_entrada = form_prontuario.save(commit=False)
                nova_entrada.paciente = paciente
                nova_entrada.autor = request.user
                nova_entrada.save()
                messages.success(request, 'Nova observação adicionada ao prontuário.')
                return redirect('hosp:mostrar', pk=paciente.pk)
            else:
                print("ERRO NO FORMULÁRIO:", form_prontuario.errors)
                # Opcional: mostrar erro na tela
                messages.error(request, f"Erro ao adicionar observação: {form_prontuario.errors}")

        # NOVO: Adicionamos a lógica para o formulário de anexo
        elif 'submit_anexo' in request.POST:
            form_anexo = AnexoPacienteForm(request.POST, request.FILES) # Preenche o form de anexo
            if form_anexo.is_valid():
                novo_anexo = form_anexo.save(commit=False)
                novo_anexo.paciente = paciente
                novo_anexo.autor = request.user
                novo_anexo.save()
                messages.success(request, 'Arquivo anexado com sucesso.')
                return redirect('hosp:mostrar', pk=paciente.pk)

    # Busca o histórico de prontuário do paciente usando o related_name
    historico = paciente.historico_prontuario.all()
    anexos = paciente.anexos.all() # NOVO: Busca os anexos do paciente

    context = {
        'paciente': paciente,
        'voltar_para_url': voltar_para_url,
        'historico': historico,
        'form_prontuario': form_prontuario,
        'pagina_ativa': 'pacientes',
        'anexos': anexos,
        'form_anexo': form_anexo,
    }
    
    return render(request, 'site/detalhes.html', context)
        
@require_POST # Garante que esta view SÓ possa ser acessada via POST
@login_required
@admin_required
def delete_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    paciente_a_deletar = get_object_or_404(Paciente, pk=pk)
    nome_paciente = paciente_a_deletar.nome
    paciente_a_deletar.delete()
    messages.success(request, f'O paciente "{nome_paciente}" foi removido com sucesso.')
    return redirect('hosp:painel_gestao')

@csrf_exempt
def predict_view(request):
    unidade_atual = request.user.unidade_saude 
    if request.method != 'POST':
        return JsonResponse({'error':'Use POST'}, status=405)
    data = json.loads(request.body)
    pred, probs = predict_from_dict(data)
    return JsonResponse({'classificacao': pred, 'probs': probs})

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.tipo_usuario == 'ADMIN') # Ajuste conforme seu model

def gerar_senha_aleatoria(tamanho=8):
    caracteres = string.ascii_letters + string.digits + "!@#$"
    senha = ''.join(secrets.choice(caracteres) for i in range(tamanho))
    return senha

@login_required
@user_passes_test(is_admin)
def registro_view(request):
    unidade_atual = request.user.unidade_saude
    dados_criados = None 
    
    if not unidade_atual and not request.user.is_superuser:
        messages.error(request, 'Você não está vinculado a nenhuma unidade de saúde.')
        return redirect('hosp:home')

    dados_criados = None

    if request.method == 'POST':
        # Usamos o form que herda suas validações
        form = CadastroPeloAdminForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            
            cpf_limpo = user.cpf.replace('.', '').replace('-', '')
            
            # Definimos que o username É o CPF
            user.username = cpf_limpo

            # 1. Gera e Define a Senha Aleatória
            senha_gerada = gerar_senha_aleatoria()
            user.set_password(senha_gerada)
            
            # 2. Define configurações padrão
            user.unidade_saude = unidade_atual
            user.precisa_mudar_senha = True 
            
            user.save()
            
            # 3. Feedback visual com botão de copiar
            dados_criados = {
                'nome': user.nome_completo,
                'usuario': cpf_limpo,
                'email': user.email,
                'senha': senha_gerada,
            }
            
            messages.success(request, f'Usuário criado! Login será pelo CPF: {cpf_limpo}')
            
            # Reseta o form
            form = CadastroPeloAdminForm()
            
    else:
        form = CadastroPeloAdminForm()

    context = {
        'form': form,
        'dados_criados': dados_criados,
        'pagina_ativa': 'gestao'
    }
    return render(request, 'site/registro.html', context)

@login_required
def perfil_view(request):
    """
    Exibe as informações do usuário logado e seu histórico de pacientes.
    """
    usuario_logado = request.user  # Padronizei o nome da variável
    unidade_atual = usuario_logado.unidade_saude 
    
    # --- CORREÇÃO 1: Inicializar os formulários AQUI (para existirem no GET) ---
    # Estado inicial: Carrega os dados atuais do usuário
    form_dados = ProfilePictureForm(instance=usuario_logado) 
    form_senha = PasswordChangeForm(usuario_logado)
    form_foto = ProfilePictureForm(instance=usuario_logado)
    # --------------------------------------------------------------------------

    if request.method == 'POST':
        # Verifica se é uma requisição AJAX (upload de foto)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form_foto = ProfilePictureForm(request.POST, request.FILES, instance=usuario_logado)
            if form_foto.is_valid():
                user_atualizado = form_foto.save()
                return JsonResponse({
                    'success': True,
                    'new_photo_url': user_atualizado.foto_perfil.url
                })
            else:
                return JsonResponse({'success': False, 'error': form_foto.errors.as_json()})
        
        # --- Lógica de Salvar Dados Pessoais ---
        if 'btn_dados_pessoais' in request.POST:
            # Aqui sobrescrevemos a variável form_dados com o que veio do POST
            # ATENÇÃO: Troquei 'user' por 'usuario_logado' para corrigir o outro erro
            form_dados = ProfilePictureForm(request.POST, request.FILES, instance=usuario_logado)
            
            if form_dados.is_valid():
                form_dados.save()
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('hosp:perfil')
            
        # --- Lógica de Mudar Senha ---
        elif 'btn_mudar_senha' in request.POST:
            # Aqui sobrescrevemos a variável form_senha com o que veio do POST
            form_senha = PasswordChangeForm(usuario_logado, request.POST)
            
            if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user) # Mantém logado
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('hosp:perfil')
            else:
                messages.error(request, 'Erro ao mudar senha. Verifique os campos.')
        
        elif 'btn_remover_foto' in request.POST:
            # Verifica se existe foto para não dar erro
            if usuario_logado.foto_perfil:
                # Deleta o arquivo físico (opcional, mas recomendado para não encher o disco)
                usuario_logado.foto_perfil.delete(save=False)
                
                # Limpa o campo no banco
                usuario_logado.foto_perfil = None
                usuario_logado.save()
                
                messages.success(request, 'Foto de perfil removida com sucesso!')
            return redirect('hosp:perfil')

    # --- Lógica GET (Histórico e Paginação) ---
    
    # 1. VERIFICA O TIPO DE USUÁRIO E BUSCA O HISTÓRICO CORRESPONDENTE
    historico_pacientes_qs = None 
    titulo_historico = 'Histórico' # Valor padrão

    if usuario_logado.tipo_usuario == 'MEDICO':
        historico_pacientes_qs = usuario_logado.pacientes_atendidos.all().order_by('-id')
        titulo_historico = 'Histórico de Pacientes Atendidos'
    elif usuario_logado.tipo_usuario == 'ATENDENTE':
        historico_pacientes_qs = usuario_logado.pacientes_criados.all().order_by('-id')
        titulo_historico = 'Pacientes Registrados na Triagem'

    # Paginação do Histórico
    page_obj_historico = None
    if historico_pacientes_qs:
        paginator = Paginator(historico_pacientes_qs, 20)
        page_number = request.GET.get('page')
        page_obj_historico = paginator.get_page(page_number)
        
    # Paginação dos Feedbacks
    feedbacks_do_usuario_qs = FeedbackTriagem.objects.filter(usuario=usuario_logado, unidade_saude=unidade_atual).order_by('-data_criacao')
    paginator_feedbacks = Paginator(feedbacks_do_usuario_qs, 20)
    feedback_page_number = request.GET.get('fpage') 
    page_obj_feedbacks = paginator_feedbacks.get_page(feedback_page_number)

    # --- CORREÇÃO 2: O Contexto agora usa as variáveis que foram criadas lá no topo ---
    context = {
        'form_foto': form_foto,
        'perfil_usuario': usuario_logado,
        'form_dados': form_dados, # Agora essa variável sempre existe!
        'form_senha': form_senha, # Essa também!
        'pagina_ativa': 'perfil',
        'titulo_historico': titulo_historico,
        'page_obj_historico': page_obj_historico,
        'page_obj_feedbacks': page_obj_feedbacks
    }

    return render(request, 'site/perfil.html', context)

# Adicione esta nova view
@login_required
@require_POST
def clear_profile_picture_ajax_view(request):
    user = request.user
    default_photo_path = 'fotos_perfil/default.jpg' # Confirme este caminho

    if user.foto_perfil and user.foto_perfil.name != default_photo_path:
        user.foto_perfil.delete(save=False)
        user.foto_perfil = default_photo_path
        user.save()
        # Retorna a URL da nova foto (a padrão)
        return JsonResponse({'success': True, 'new_photo_url': user.foto_perfil.url})
    else:
        return JsonResponse({'success': False, 'error': 'Nenhuma foto customizada para remover.'})

@medico_required
@require_POST # Garante que esta view só aceite requisições POST
@login_required
# @medico_required # Use seu decorador aqui
def mudar_status_view(request, pk):
    # Encontra o paciente ou retorna erro 404
    paciente = get_object_or_404(Paciente, pk=pk)

    mudanca_realizada = False # Flag para saber se precisamos salvar
    
    # Lógica de transição de status
    if paciente.status == 'Aguardando':
        # Muda o status para "Em atendimento"
        paciente.status = 'Em atendimento'
        # Vincula o médico logado ao paciente
        paciente.medico_responsavel = request.user
        paciente.hora_inicio_atendimento = timezone.now() 

        mudanca_realizada = True  # <--- VOCÊ PRECISAVA ADICIONAR ISSO
        
        messages.success(request, f'Atendimento de {paciente.nome} iniciado!')
    
    elif paciente.status == 'Em atendimento':
        if request.user == paciente.medico_responsavel or request.user.is_superuser:
            # Se for, permite a finalização
            paciente.status = 'Concluido'
            paciente.hora_fim_atendimento = timezone.now()
            mudanca_realizada = True
            messages.success(request, f'Atendimento do paciente "{paciente.nome}" finalizado com sucesso.')
        else:
            # Se NÃO for, mostra um erro e NÃO faz nenhuma alteração
            messages.error(request, 'Apenas o médico responsável ou um administrador pode finalizar este atendimento.')
            # Não definimos mudanca_realizada = True, então nada será salvo.

    
    # Salva as alterações no banco de dados
    if mudanca_realizada:
        paciente.save()
    
    # Redireciona o usuário de volta para a página de detalhes do paciente
    return redirect('hosp:mostrar', pk=paciente.pk)

@login_required
def feedback_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Impede que um feedback seja dado duas vezes para o mesmo paciente
    if FeedbackTriagem.objects.filter(paciente=paciente, usuario=request.user, unidade_saude=unidade_atual).exists():
        messages.error(request, 'Você já enviou um feedback para este paciente.')
        return redirect('hosp:listar')

    if request.method == 'POST':
        form = FeedbackTriagemForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.paciente = paciente
            feedback.usuario = request.user
            feedback.save()
            messages.success(request, 'Feedback enviado com sucesso!')
            return redirect('hosp:listar')
    else:
        form = FeedbackTriagemForm()

    context = {
        'form': form,
        'paciente': paciente
    }
    return render(request, 'site/feedback_form.html', context)


@login_required
def lista_feedback_view(request):
    unidade_atual = request.user.unidade_saude 
    # Otimizamos a consulta E adicionamos a contagem de feedbacks por paciente
    todos_os_feedbacks = FeedbackTriagem.objects.select_related('paciente', 'usuario') \
        .annotate(
            total_feedbacks_paciente=Count('paciente__feedbacktriagem')
        ) \
        .order_by('-data_criacao')
    
    paginator = Paginator(todos_os_feedbacks, 20) # Divide a lista em páginas de 20
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_feedbacks = todos_os_feedbacks.count()
    
    # Filtramos a lista que já temos em memória, sem precisar ir ao banco de novo
    classificacoes_corretas = todos_os_feedbacks.filter(triagem_correta=True).count()
    classificacoes_incorretas = total_feedbacks - classificacoes_corretas
    
    # Lógica para evitar divisão por zero se não houver feedbacks
    if total_feedbacks > 0:
        percentual_corretas = (classificacoes_corretas / total_feedbacks) * 100
        percentual_incorretas = (classificacoes_incorretas / total_feedbacks) * 100
    else:
        percentual_corretas = 0
        percentual_incorretas = 0
    
    context = {
        'feedbacks': todos_os_feedbacks,
        'page_obj': page_obj, # <-- ADICIONE ESTA LINHA EM SEU LUGAR
        
        # ADICIONADO: Enviando a lista de opções de classificação para o template
        'classificacao_choices': Paciente.Risco,
        
        # ADICIONADO: Enviando a lista de tipos de usuário para o template
        'tipo_usuario_choices': CustomUser.TipoUsuario.choices,

        # ADICIONADO: Enviando os novos valores calculados para o template
        'total_feedbacks': total_feedbacks,
        'classificacoes_corretas': classificacoes_corretas,
        'classificacoes_incorretas': classificacoes_incorretas,
        'percentual_corretas': percentual_corretas,
        'percentual_incorretas': percentual_incorretas,
        'pagina_ativa': 'feedbacks',
    }
    
    # Verifique se o nome do seu template é 'lista_feedback.html' ou outro
    return render(request, 'site/lista_feedback.html', context)

@login_required
@admin_required # Garante que apenas usuários Admin possam acessar esta página
def gestao_view(request):
    unidade_atual = request.user.unidade_saude 
    hoje = timezone.now().date()

    # --- Lógica de Estatísticas de Pacientes (já feita) ---
    total_pacientes = Paciente.objects.filter(unidade_saude=unidade_atual).count()
    pacientes_hoje_count = Paciente.objects.filter(hora_chegada__date=hoje, unidade_saude=unidade_atual).count()
    inicio_semana = hoje - datetime.timedelta(days=hoje.weekday())
    pacientes_esta_semana = Paciente.objects.filter(hora_chegada__date__gte=inicio_semana, unidade_saude=unidade_atual).count()

    # --- Lógica para Profissionais (já feita) ---
    todos_pacientes_para_tabela = Paciente.objects.filter(unidade_saude=unidade_atual).order_by('-id')
    todos_medicos = CustomUser.objects.filter(tipo_usuario='MEDICO', unidade_saude=unidade_atual).order_by('nome_completo')
    total_medicos = todos_medicos.count()
    todos_enfermeiros = CustomUser.objects.filter(tipo_usuario='ENFERMEIRO', unidade_saude=unidade_atual).order_by('nome_completo')
    total_enfermeiros = todos_enfermeiros.count()
    todos_atendentes = CustomUser.objects.filter(tipo_usuario='ATENDENTE', unidade_saude=unidade_atual).order_by('nome_completo')
    total_atendentes = todos_atendentes.count()

    paginator = Paginator(todos_pacientes_para_tabela, 20) # Divide a lista em páginas de 20
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # =========================================================
    #  NOVO: LÓGICA PARA ATIVIDADE RECENTE
    # =========================================================
    # 1. Novos usuários nos últimos 7 dias
    data_inicio_ultimos_7_dias = hoje - datetime.timedelta(days=7)
    novos_usuarios_7_dias = CustomUser.objects.filter(date_joined__date__gte=data_inicio_ultimos_7_dias, unidade_saude=unidade_atual).count()

    # 2. Novos usuários no período anterior (de 14 a 8 dias atrás)
    data_fim_periodo_anterior = data_inicio_ultimos_7_dias
    data_inicio_periodo_anterior = hoje - datetime.timedelta(days=14)
    novos_usuarios_periodo_anterior = CustomUser.objects.filter(
        date_joined__date__gte=data_inicio_periodo_anterior,
        date_joined__date__lt=data_fim_periodo_anterior,
        unidade_saude=unidade_atual,
    ).count()

    # 3. Cálculo da Taxa de Crescimento
    taxa_crescimento = 0
    if novos_usuarios_periodo_anterior > 0:
        # Fórmula padrão de variação percentual
        taxa_crescimento = ((novos_usuarios_7_dias - novos_usuarios_periodo_anterior) / novos_usuarios_periodo_anterior) * 100
    elif novos_usuarios_7_dias > 0:
        # Se o período anterior foi 0 e o atual não, o crescimento é total
        taxa_crescimento = 100

    # Formatando para exibição (ex: "+15%" ou "-5%")
    taxa_crescimento_formatada = f"{'+' if taxa_crescimento >= 0 else ''}{taxa_crescimento:.0f}%"

    # --- Contexto Final para o Template ---
    context = {
        # ... (todas as suas outras variáveis de contexto) ...
        'pacientes': todos_pacientes_para_tabela,
        'medicos': todos_medicos,
        'enfermeiros': todos_enfermeiros,
 
        'atendentes': todos_atendentes,
        'total_pacientes_hoje': pacientes_hoje_count,
        'pacientes_esta_semana': pacientes_esta_semana,
        'total_pacientes': total_pacientes,
        'total_medicos': total_medicos,
        'total_enfermeiros': total_enfermeiros,
  
        'total_atendentes': total_atendentes,
        'page_obj': page_obj, # <-- ADICIONE ESTA LINHA EM SEU LUGAR

        # Novas variáveis para Atividade Recente
        'novos_usuarios_7_dias': novos_usuarios_7_dias,
        'taxa_crescimento': taxa_crescimento, # Valor numérico para lógica no template
        'taxa_crescimento_formatada': taxa_crescimento_formatada, # Valor formatado para exibição
        'pagina_ativa': 'gestao',
    }
    
    return render(request, 'site/gestao.html', context)

@login_required
@admin_required # Protege a view, apenas Admins podem acessá-la
def ver_perfil_usuario_view(request, pk):
    """
    Exibe o perfil de um usuário específico para um administrador.
    """
    unidade_atual = request.user.unidade_saude 
    # Busca o usuário pelo ID fornecido na URL ou retorna um erro 404
    usuario_selecionado = get_object_or_404(CustomUser, pk=pk)
    
    context = {
        'perfil_usuario': usuario_selecionado, # Enviamos o usuário selecionado para o template
    }
    
    # Lógica para buscar o histórico de pacientes (igual à da perfil_view)
    if usuario_selecionado.tipo_usuario == 'MEDICO':
        pacientes_do_usuario = usuario_selecionado.pacientes_atendidos.all().order_by('-id')
        context['titulo_historico'] = f'Histórico de Pacientes Atendidos por {usuario_selecionado.nome_completo}'
        context['historico_pacientes'] = pacientes_do_usuario

    elif usuario_selecionado.tipo_usuario == 'ATENDENTE':
        pacientes_do_usuario = usuario_selecionado.pacientes_criados.all().order_by('-id')
        context['titulo_historico'] = f'Pacientes Registrados por {usuario_selecionado.nome_completo}'
        context['historico_pacientes'] = pacientes_do_usuario
        
    # Lógica para buscar os feedbacks feitos pelo usuário
    feedbacks_do_usuario = FeedbackTriagem.objects.filter(usuario=usuario_selecionado, unidade_saude=unidade_atual).order_by('-data_criacao')
    context['feedbacks_do_usuario'] = feedbacks_do_usuario
    
    # Reutilizaremos o template perfil.html para mostrar as informações
    return render(request, 'site/perfil.html', context)

@require_POST # Garante que esta view SÓ possa ser acessada via POST
@login_required
@admin_required
def delete_user_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    usuario_a_deletar = get_object_or_404(CustomUser, pk=pk)
    
    if request.user == usuario_a_deletar:
        messages.error(request, 'Você não pode remover sua própria conta de administrador.')
        return redirect('hosp:painel_gestao')

    nome_usuario = usuario_a_deletar.username
    usuario_a_deletar.delete()
    messages.success(request, f'O usuário "{nome_usuario}" foi removido com sucesso.')
    return redirect('hosp:painel_gestao')

@login_required
def partial_patient_list_view(request):
    """
    Esta view retorna apenas o HTML do corpo da tabela de pacientes,
    para ser usada pela chamada AJAX.
    """
    unidade_atual = request.user.unidade_saude 
    # Reutilizamos EXATAMENTE a mesma lógica de ordenação da index_view
    prioridade_classificacao = Case(
        When(classificacao='Vermelho', then=Value(1)),
        When(classificacao='Laranja', then=Value(2)),
        When(classificacao='Amarelo', then=Value(3)),
        When(classificacao='Verde', then=Value(4)),
        When(classificacao='Azul', then=Value(5)),
        default=Value(6),
        output_field=IntegerField()
    )
    
    lista_pacientes_priorizada = Paciente.objects.exclude(status='Concluido').annotate(
        prioridade=prioridade_classificacao
    ).order_by('prioridade', 'hora_chegada')

    context = {
        'pacientes': lista_pacientes_priorizada,
    }
    
    # Renderiza um novo template "parcial" que só contém as linhas da tabela
    return render(request, 'site/partials/_patient_list_partial.html', context)

@login_required
@enfermeiro_required
def validacao_triagem_view(request):
    unidade_atual = request.user.unidade_saude 

    pacientes_pendentes = Paciente.objects.filter(status='Pendente', unidade_saude=unidade_atual).order_by('hora_chegada')
    
    # 2. Query base para pacientes validados
    validados_query = Paciente.objects.filter(
        status='Aguardando',  # O status que você define ao validar
        unidade_saude=unidade_atual
    )

    # 3. Pega o número total de validados
    total_validados = validados_query.count()

    # 4. Pega os 10 mais recentes para exibir na lista
    #    (Usamos '-hora_chegada' para mostrar os mais novos primeiro)
    pacientes_validados_lista = validados_query.order_by('-hora_chegada')[:10]
    # --- INÍCIO DA MUDANÇA ---
    # Precisamos de uma instância VAZIA do formulário
    # para o template poder renderizar o formulário escondido.
    form = ValidacaoTriagemForm()
    # --- FIM DA MUDANÇA ---

    context = {
        'pacientes_pendentes': pacientes_pendentes,
        'pacientes_validados_lista': pacientes_validados_lista,
        'total_validados': total_validados,
        'form': form,  # <--- ADICIONE ESTA LINHA
        'pagina_ativa': 'validacao'
    }
    return render(request, 'site/validacao_triagem.html', context)

@login_required
@enfermeiro_required
def confirmar_triagem_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = ValidacaoTriagemForm(request.POST, instance=paciente)
        if form.is_valid():
            paciente_validado = form.save(commit=False)
            paciente_validado.status = 'Aguardando' # Move o paciente para a fila oficial
            paciente_validado.save()
            messages.success(request, f'Triagem do paciente "{paciente.nome}" validada com sucesso.')
            return redirect('hosp:validacao_triagem')
    else:
        form = ValidacaoTriagemForm(instance=paciente)
    
    context = {
        'paciente': paciente,
        'form': form
    }
    return render(request, 'site/confirmar_triagem.html', context)

@require_POST # Ação de mudança de estado deve ser sempre POST
@login_required
@admin_required # Apenas Admins podem desativar contas
def desativar_usuario_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    usuario_a_desativar = get_object_or_404(CustomUser, pk=pk)

    # Medida de segurança: impede que um admin desative a si mesmo
    if request.user == usuario_a_desativar:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('hosp:ver_perfil_usuario', pk=pk)

    # Ação principal: desativa o usuário
    usuario_a_desativar.is_active = False
    usuario_a_desativar.save()

    messages.success(request, f'A conta do usuário "{usuario_a_desativar.username}" foi desativada com sucesso.')
    # Redireciona de volta para o perfil que acabou de ser alterado
    return redirect('hosp:ver_perfil_usuario', pk=pk)

@require_POST
@login_required
@admin_required
def reativar_usuario_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    usuario_a_reativar = get_object_or_404(CustomUser, pk=pk)

    # Ação principal: reativa o usuário
    usuario_a_reativar.is_active = True
    usuario_a_reativar.save()

    messages.success(request, f'A conta do usuário "{usuario_a_reativar.username}" foi reativada com sucesso.')
    # Redireciona de volta para o perfil que acabou de ser alterado
    return redirect('hosp:ver_perfil_usuario', pk=pk)

@login_required
@user_passes_test(pode_editar_cadastro)
def edit_prontuario_admin_view(request, pk):
    unidade_atual = request.user.unidade_saude 
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        # Use o NOVO formulário aqui
        form = PacienteAdminEditForm(request.POST, instance=paciente) 
        if form.is_valid():
            form.save()
            messages.success(request, f'Dados cadastrais de "{paciente.nome}" atualizados com sucesso.')
            return redirect('hosp:mostrar', pk=paciente.pk)
    else:
        # Use o NOVO formulário aqui também
        form = PacienteAdminEditForm(instance=paciente) 

    context = {
        'paciente': paciente,
        'form': form
    }
    return render(request, 'site/edit_prontuario_admin.html', context)

@login_required # Garante que apenas usuários logados vejam a ajuda
def ajuda_view(request):
    unidade_atual = request.user.unidade_saude 
    # Opcional: Adiciona 'pagina_ativa' se você usa isso para destacar o menu
    context = {'pagina_ativa': 'ajuda'} 
    return render(request, 'site/ajuda.html', context)

@login_required
@admin_required # Protege a view
def log_auditoria_view(request):
    unidade_atual = request.user.unidade_saude 
    log_list = LogAcao.objects.filter(unidade_saude=unidade_atual) # Pega todos os logs (já ordenados pelo Meta)
    
    # Paginação (igual às outras listas)
    paginator = Paginator(log_list, 50) # Mostra 50 logs por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'pagina_ativa': 'gestao', # Ou crie um 'log' se quiser
    }
    return render(request, 'site/log_auditoria.html', context)

@login_required
def alterar_senha_view(request):
    if request.method == 'POST':
        # O PasswordChangeForm exige o usuário como primeiro argumento
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # --- O PULO DO GATO ---
            # Isso mantém o usuário logado após trocar a senha.
            # Se não usar isso, ele será deslogado automaticamente.
            update_session_auth_hash(request, user) 
            
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('hosp:perfil') # Redireciona de volta para o perfil
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'pagina_ativa': 'perfil' # Para manter o menu lateral ativo se tiver
    }
    return render(request, 'site/alterar_senha.html', context)

def render_pdf_view(request, paciente_id):
    # 1. Busca o paciente no banco
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # 2. Define o template e o contexto
    template_path = 'site/ficha_pdf.html'
    context = {'paciente': paciente}
    
    # 3. Cria a resposta do tipo PDF
    response = HttpResponse(content_type='application/pdf')
    # Se quiser que baixe automaticamente, mude para 'attachment'. 
    # 'inline' abre no navegador.
    response['Content-Disposition'] = f'inline; filename="ficha_{paciente.nome}.pdf"'
    
    # 4. A mágica da conversão
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(
       html, dest=response
    )
    
    if pisa_status.err:
       return HttpResponse('Tivemos alguns erros <pre>' + html + '</pre>')
       
    return response