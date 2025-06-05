from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        labels = {
            'nome': 'Nome',
            'idade': 'Idade',
            'sexo': 'Gênero',
            'cpf': 'CPF',
            'convenio': 'Convenio',
            'hora_chegada': 'Hora de Chegada',

            'temperatura': 'Temperatura',
            'pressaoArterial': 'Pressão Arterial',
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
            'pressaoArterial': forms.NumberInput(attrs={'class': 'form-control'}),
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
    
