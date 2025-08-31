from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente, FeedbackTriagem
from .forms import PacienteForm, CustomUserCreationForm, FeedbackTriagemForm
from collections import Counter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .ml.predict import predict_from_dict
from django.contrib.auth.decorators import login_required # Importe o login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField, Avg, F, DurationField
from django.urls import reverse
import datetime


@login_required
def index_view(request):
    
    # --- 1. Dados para a Análise ---
    hoje = timezone.now().date()
    
    pacientes_aguardando = Paciente.objects.filter(status='Aguardando')
    total_aguardando = pacientes_aguardando.count()
    total_em_atendimento = Paciente.objects.filter(status='Em atendimento').count()
    vermelhos_aguardando = pacientes_aguardando.filter(classificacao='Vermelho').count()
    laranjas_aguardando = pacientes_aguardando.filter(classificacao='Laranja').count()
    chegadas_hoje = Paciente.objects.filter(hora_chegada__date=hoje).count()
    concluidos_hoje = Paciente.objects.filter(
        status='Concluido', 
        hora_fim_atendimento__date=hoje
    ).count()

    # ==============================================================================
    #     NOVA MÉTRICA: CÁLCULO DO TEMPO MÉDIO DE ESPERA (FEITO EM PYTHON)
    # ==============================================================================
    # Primeiro, buscamos todos os pacientes que iniciaram atendimento hoje
    pacientes_atendidos_hoje = Paciente.objects.filter(
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
    
    lista_pacientes_priorizada = Paciente.objects.exclude(status='Concluido').annotate(
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
    }
    
    return render(request, 'site/index.html', context)

@login_required
def create_view(request):
    if request.method == 'GET':
        form = PacienteForm()
        return render(request, 'site/criar.html', {'form': form})
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.atendente = request.user 
            form.save()
            return redirect('hosp:listar')
        else:
            print("Erros de validação:", form.errors)
            return render(request, 'site/criar.html', {'form': form})

@login_required        
def list_view(request):
    pacientes = Paciente.objects.all()
    status_contagem = Counter(p.status for p in pacientes)
    return render(request, 'site/listar.html', {
        'pacientes': pacientes,
        'status_contagem': status_contagem
    })

def detail_view(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    # NOVO: Lógica do botão "Voltar"
    # 1. Define uma URL padrão (fallback) caso a página anterior não seja identificada
    fallback_url = reverse('hosp:listar')
    # 2. Tenta pegar a URL de onde o usuário veio (a página anterior)
    voltar_para_url = request.META.get('HTTP_REFERER', fallback_url)

    # NOVO: Prepara o contexto para enviar ao template
    context = {
        'paciente': paciente,
        'voltar_para_url': voltar_para_url
    }
    
    return render(request, 'site/detalhes.html', context)

def update_view(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'GET':
        form = PacienteForm(instance=paciente)
        return render(request, 'site/atualizar.html', {'paciente': paciente, 'form': form})
    elif request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('hosp:mostrar', pk=paciente.pk)
        
def delete_view(request, pk):
    paciente = Paciente.objects.get(pk = pk)
    if paciente:
        paciente.delete()
        request.status_code = 204
        return redirect('hosp:listar')
    
@login_required
def dashboard_view(request):
    pacientes = Paciente.objects.all()
    status_contagem = Counter(p.status for p in pacientes)

    return render(request, 'site/dashboard.html', {
        'pacientes': pacientes,
        'status_contagem': status_contagem
    })
    
def triagem_view(request):
    return render(request, 'site/triagem.html')

@csrf_exempt
def predict_view(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Use POST'}, status=405)
    data = json.loads(request.body)
    pred, probs = predict_from_dict(data)
    return JsonResponse({'classificacao': pred, 'probs': probs})

def registro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Conta criada com sucesso! Por favor, faça o login.')
            return redirect('hosp:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'site/registro.html', {'form': form})

@login_required # Garante que apenas usuários logados possam ver esta página
def perfil_view(request):
    """
    Exibe as informações do usuário logado e seu histórico de pacientes.
    """
    # Prepara um dicionário de contexto para enviar ao template
    context = {}
    
    # Pega o usuário logado
    usuario_logado = request.user
    
    # 1. VERIFICA O TIPO DE USUÁRIO E BUSCA O HISTÓRICO CORRESPONDENTE
    if usuario_logado.tipo_usuario == 'MEDICO':
        # Usa o 'related_name' que definimos no modelo Paciente
        pacientes_do_usuario = usuario_logado.pacientes_atendidos.all().order_by('-id')
        context['titulo_historico'] = 'Histórico de Pacientes Atendidos'
        context['historico_pacientes'] = pacientes_do_usuario

    elif usuario_logado.tipo_usuario == 'ATENDENTE':
        # Usa o outro 'related_name' que já existia no modelo
        pacientes_do_usuario = usuario_logado.pacientes_criados.all().order_by('-id')
        context['titulo_historico'] = 'Pacientes Registrados na Triagem'
        context['historico_pacientes'] = pacientes_do_usuario

    feedbacks_do_usuario = FeedbackTriagem.objects.filter(usuario=usuario_logado).order_by('-data_criacao')
    context['feedbacks_do_usuario'] = feedbacks_do_usuario
        
    # 2. RENDERIZA O TEMPLATE COM O CONTEXTO ATUALIZADO
    return render(request, 'site/perfil.html', context)

@require_POST # Garante que esta view só aceite requisições POST
@login_required
# @medico_required # Use seu decorador aqui
def mudar_status_view(request, pk):
    # Encontra o paciente ou retorna erro 404
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Lógica de transição de status
    if paciente.status == 'Aguardando':
        # Muda o status para "Em atendimento"
        paciente.status = 'Em atendimento'
        # Vincula o médico logado ao paciente
        paciente.medico_responsavel = request.user
        paciente.hora_inicio_atendimento = timezone.now() 
    
    elif paciente.status == 'Em atendimento':
        # Muda o status para "Concluído"
        paciente.status = 'Concluido'
        paciente.hora_fim_atendimento = timezone.now()

    
    # Salva as alterações no banco de dados
    paciente.save()
    
    # Redireciona o usuário de volta para a página de detalhes do paciente
    return redirect('hosp:mostrar', pk=paciente.pk)

@login_required
def feedback_view(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Impede que um feedback seja dado duas vezes para o mesmo paciente
    if FeedbackTriagem.objects.filter(paciente=paciente).exists():
        messages.error(request, 'Já existe um feedback para este paciente.')
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
    # Busca todos os feedbacks, ordenados do mais recente para o mais antigo
    todos_os_feedbacks = FeedbackTriagem.objects.all().order_by('-data_criacao')
    context = {
        'feedbacks': todos_os_feedbacks
    }
    return render(request, 'site/lista_feedback.html', context)