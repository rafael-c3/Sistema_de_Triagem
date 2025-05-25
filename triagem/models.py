from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Paciente(models.Model):
    Sexualidade = [
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
    ]

    Convenios = [
        ('SUS', 'SUS'),
        ('Unimed', 'Unimed'),
        ('Hapvida', 'Hapvida'),
        ('Amil', 'Amil'),
        ('Bradesco Saude', 'Bradesco Saude'),
    ]

    Status = [
        ('Aguardando', 'Aguardando'),
        ('Em atendimento', 'Em atendimento'),
        ('Concluido', 'Concluido'),
    ]

    Sintomas = [
        ('Febre', 'Febre'),
        ('Dor de Cabeça', 'Dor de Cabeça'),
        ('Falta de Ar', 'Falta de Ar'),
        ('Náusea/Vômito', 'Náusea/Vômito'),
        ('Tontura', 'Tontura'),
        ('Fraqueza', 'Fraqueza'),
    ]

    Risco = [
        ('Vermelho', 'Emergência'),
        ('Laranja', 'Muito Urgente'),
        ('Amarelo', 'Urgente'),
        ('Verde', 'Pouco Urgente'),
        ('Azul', 'Não Urgente'),

    ]

    nome = models.CharField(max_length=100)
    idade = models.CharField(max_length=3)
    sexo = models.CharField(choices=Sexualidade, max_length=50)
    cpf = models.CharField(max_length=11)
    convenio = models.CharField(choices=Convenios, max_length=50)
    hora_chegada = models.TimeField(blank=True, null=True)

    temperatura = models.CharField(max_length=2)
    pulso = models.CharField(max_length=2)

    queixa = models.CharField(max_length=1000)
    dor = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    inicio_sintomas = models.DateField(blank=True, null=True)
    sintomas_associados = models.CharField(choices=Sintomas, max_length=50)
    observacoes = models.CharField(blank=True, null=True, max_length=1000)

    classificacao = models.CharField(choices=Risco, max_length=50)
    status_atendimento = models.CharField(max_length=20, choices=Status, default='Esperando')

    @property
    def status(self):
        if self.classificacao == 'Vermelho':
            return 'Crítico'
        elif self.classificacao in ['Laranja', 'Amarelo']:
            return 'Urgente'
        else:
            return 'Normal'

    def __str__(self):
        return self.nome