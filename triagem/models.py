from django.db import models

class Paciente(models.Model):
    Sexualidade = [
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
    ]

    Cores = [
        ('Vermelha', 'Vemelha'),
        ('Laranja', 'Laranja'),
        ('Amarela', 'Amarela'),
        ('Verde', 'Verde'),
        ('Azul', 'Azul'),
    ]

    Status = [
        ('Esperando', 'Esperando'),
        ('Em atendimento', 'Em atendimento'),
        ('Finalizado', 'Finalizado'),
    ]

    nome = models.CharField(max_length=20)
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=10, choices=Sexualidade, default='Masculino')
    cpf = models.CharField(max_length=11)
    data_chegada = models.DateField(null=True, blank=True)
    prioridade = models.CharField(max_length=20, choices=Cores, default='Vermelha')
    status_atendimento = models.CharField(max_length=20, choices=Status, default='Esperando')

    def __str__(self):
        return self.nome