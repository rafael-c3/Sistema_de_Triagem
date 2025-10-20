# triagem/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Paciente, FeedbackTriagem

# --- Personalização para o modelo de Usuário (CustomUser) ---

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuração de administração para o modelo de usuário personalizado.
    Herda de UserAdmin para manter toda a segurança e funcionalidades padrão.
    """
    # Adiciona nossos campos customizados à página de edição do usuário
    # Organizando-os em seções (fieldsets)
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {'fields': ('nome_completo', 'cpf')}),
        ('Perfil Profissional', {'fields': ('tipo_usuario', 'especializacao')}),
    )
    
    # Adiciona campos customizados à página de criação de um novo usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('nome_completo', 'email', 'cpf', 'tipo_usuario', 'crm', 'coren', 'uf_registro', 'especializacao')}),
    )

    # Define as colunas que aparecerão na lista de usuários
    list_display = ('username', 'nome_completo', 'tipo_usuario', 'is_active', 'is_staff')
    
    # Adiciona uma barra de filtros à direita
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'especializacao')
    
    # Adiciona uma barra de busca
    search_fields = ('username', 'nome_completo', 'email')


# --- Personalização para o modelo de Paciente ---

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """
    Configuração de administração para o modelo de Paciente.
    """
    # Define as colunas que aparecerão na lista de pacientes
    list_display = ('nome', 'cpf', 'idade', 'classificacao', 'status', 'hora_chegada_formatada', 'medico_responsavel')
    
    # Adiciona uma barra de filtros à direita
    list_filter = ('status', 'classificacao', 'convenio')
    
    # Adiciona uma barra de busca
    search_fields = ('nome', 'cpf')
    
    # Define campos que não podem ser editados diretamente no admin (são automáticos)
    readonly_fields = ('idade', 'hora_chegada', 'hora_inicio_atendimento', 'hora_fim_atendimento', 
                       'atendente', 'medico_responsavel', 'tempo_de_espera', 'tempo_de_atendimento')

    # Organiza a página de edição do paciente em seções lógicas
    fieldsets = (
        ('Informações do Atendimento', {
            'fields': ('status', 'atendente', 'medico_responsavel')
        }),
        ('Linha do Tempo', {
            'fields': ('hora_chegada', 'hora_inicio_atendimento', 'hora_fim_atendimento', 
                       'tempo_de_espera', 'tempo_de_atendimento')
        }),
        ('Dados Pessoais do Paciente', {
            'fields': ('nome', 'data_nascimento', 'idade', 'sexo', 'cpf', 'convenio')
        }),
        ('Sinais Vitais e Triagem', {
            'fields': ('temperatura', 'pressao_sistolica', 'pressao_diastolica', 'pulso', 
                       'frequenciaRespiratoria', 'saturacao', 'glicemia', 'dor')
        }),
        ('Anamnese e Classificação', {
            'fields': ('queixa', 'inicio_sintomas', 'sintomas_associados', 'observacoes', 
                       'classificacao', 'justificativa', 'encaminhamento')
        }),
    )

    # Função para formatar a hora na lista para melhor visualização
    def hora_chegada_formatada(self, obj):
        if obj.hora_chegada:
            return obj.hora_chegada.strftime("%d/%m/%Y %H:%M")
        return "N/A"
    hora_chegada_formatada.admin_order_field = 'hora_chegada'
    hora_chegada_formatada.short_description = 'Hora da Chegada'

@admin.register(FeedbackTriagem)
class FeedbackTriagemAdmin(admin.ModelAdmin):
    # Campos que aparecerão na lista de feedbacks
    list_display = ('paciente', 'usuario', 'triagem_correta', 'status', 'data_criacao')
    
    # Adiciona filtros para encontrar feedbacks facilmente
    list_filter = ('status', 'triagem_correta', 'usuario__tipo_usuario')
    
    # Torna o campo 'status' editável diretamente na lista
    list_editable = ('status',)
    
    # Campos de busca
    search_fields = ('paciente__nome', 'usuario__username')
    
    # Campos que não podem ser editados (são registros fixos)
    readonly_fields = ('paciente', 'usuario', 'data_criacao')

    # Organiza a página de edição
    fieldsets = (
        ('Detalhes do Feedback', {
            'fields': ('paciente', 'usuario', 'data_criacao')
        }), 
        ('Avaliação do Profissional', {
            'fields': ('triagem_correta', 'classificacao_correta', 'motivo')
        }),
        ('Gestão do Feedback (Ação do Admin)', {
            'fields': ('status',)
        }),
    )