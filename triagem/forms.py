from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Paciente, CustomUser, FeedbackTriagem

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        exclude = ['atendente']

        labels = {
            'nome': 'Nome',
            'idade': 'Idade',
            'sexo': 'Gênero',
            'cpf': 'CPF',
            'convenio': 'Convenio',
            'hora_chegada': 'Hora de Chegada',

            'temperatura': 'Temperatura',
            'pressao_sistolica': 'Pressão Sistólica',
            'pressao_diastolica': 'Pressão Diastólica',
            'pulso': 'Pulso',
            'frequenciaRespiratoria': 'Frequencia Respiratória',
            'saturacao': 'Saturação',
            'glicemia': 'Glicemia',
            'dor': 'Escala de Dor',

            'queixa': 'Queixa',
            'inicio_sintomas': 'Inicio dos sintomas',
            'sintomas_associados': 'Sintomas Associados',
            'observacoes': 'Observações',

            'classificacao': 'Classificação',
            'justificativa': 'Justificativa',
            'encaminhamento': 'Encaminhamento',

            'status_atendimento': 'Status de Atendimento',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'idade': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'convenio': forms.Select(attrs={'class': 'form-control'}),
            'hora_chegada': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),

            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'pressao_sistolica': forms.NumberInput(attrs={'class': 'form-control'}),
            'pressao_diastolica': forms.NumberInput(attrs={'class': 'form-control'}),
            'pulso': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequenciaRespiratoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'saturacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'glicemia': forms.NumberInput(attrs={'class': 'form-control'}),
            'dor': forms.NumberInput(attrs={'class': 'form-control'}),

            'queixa': forms.Textarea(attrs={'class': 'form-control'}),
            'inicio_sintomas': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sintomas_associados': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control'}),

            'classificacao': forms.Select(attrs={'class': 'form-control'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control'}),
            'encaminhamento': forms.Select(attrs={'class': 'form-control'}),

            'status_atendimento': forms.Select(attrs={'class': 'form-control'}),
        }
    
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'nome_completo', 'email', 'cpf', 'tipo_usuario', 'registro_profissional', 'especializacao')

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')

        # Se o usuário for um médico, verifique os campos extras
        if tipo_usuario == 'MEDICO':
            registro = cleaned_data.get('registro_profissional')
            especializacao = cleaned_data.get('especializacao')

            if not registro:
                self.add_error('registro_profissional', 'Este campo é obrigatório para médicos.')
            
            if not especializacao:
                self.add_error('especializacao', 'Este campo é obrigatório para médicos.')
        
        return cleaned_data

class FeedbackTriagemForm(forms.ModelForm):
    class Meta:
        model = FeedbackTriagem
        # Apenas os campos que o usuário deve preencher
        fields = ['triagem_correta', 'classificacao_correta', 'motivo']
        widgets = {
            'triagem_correta': forms.RadioSelect(choices=((True, 'Sim'), (False, 'Não'))),
            'classificacao_correta': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        triagem_foi_correta = cleaned_data.get('triagem_correta')

        # Se a triagem foi marcada como incorreta, os outros campos se tornam obrigatórios
        if triagem_foi_correta is False:
            classificacao = cleaned_data.get('classificacao_correta')
            motivo = cleaned_data.get('motivo')
            if not classificacao:
                self.add_error('classificacao_correta', 'Este campo é obrigatório quando a classificação está incorreta.')
            if not motivo:
                self.add_error('motivo', 'O motivo é obrigatório quando a classificação está incorreta.')
        
        return cleaned_data