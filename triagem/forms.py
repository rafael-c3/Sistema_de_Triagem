from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        labels = {
            'nome': 'Nome',
            'data_nascimento': 'Data de Nascimento',
            'sexo': 'Sexo',
            'cpf': 'CPF',
            'data_chegada': 'Data de Chegada',
            'prioridade': 'Prioridade',
            'status_atendimento': 'Status de Atendimento',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_chegada': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'status_atendimento': forms.Select(attrs={'class': 'form-control'})
        }
    
