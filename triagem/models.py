from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .ml.predict import predict_from_dict
from django.conf import settings
from django.contrib.auth.models import AbstractUser # Importe o AbstractUser

class CustomUser(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ATENDENTE = 'ATENDENTE', 'Atendente'
        MEDICO = 'MEDICO', 'Médico'
        ADMIN = 'ADMIN', 'Admin'

    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    tipo_usuario = models.CharField(max_length=10, choices=TipoUsuario.choices, default=TipoUsuario.ATENDENTE)

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
        # Sintomas Chave (Geralmente Indicam Urgência)
        ('Dor_Toracica', 'Dor Torácica / Aperto no Peito'),
        ('Falta_de_Ar', 'Falta de Ar / Dificuldade para Respirar'),
        ('Alteracao_Neurologica_Grave', 'Alteração de Consciência / Convulsão / Confusão'),
        ('Sangramento_Ativo', 'Sangramento Ativo / Vômito ou Fezes com Sangue'),

        # Sintomas Comuns
        ('Febre', 'Febre / Calafrios'),
        ('Dor_de_Cabeca', 'Dor de Cabeça'),
        ('Tontura_MalEstar', 'Tontura / Fraqueza / Mal-estar Geral'),
        ('Sintomas_Respiratorios_Leves', 'Tosse / Espirros / Dor de Garganta'),
        ('Dor_Abdominal', 'Dor Abdominal / Cólica'),
        ('Sintomas_Gastrointestinais', 'Náusea / Vômito / Diarreia'),

        # Sintomas Específicos
        ('Lesao_Trauma', 'Lesão / Trauma / Queda Recente'),
        ('Dor_Locomotora', 'Dor Muscular / Articular / Lombar'),
        ('Reacao_Alergica_Pele', 'Reação Alérgica / Erupção na Pele / Inchaço'),
        ('Queixa_Urinaria', 'Queixa Urinária (Dor ao urinar / Sangue na urina)'),

        # Outros
        ('Outro', 'Outro'),
    ]

    Risco = [
        ('Vermelho', 'Emergência'),
        ('Laranja', 'Muito Urgente'),
        ('Amarelo', 'Urgente'),
        ('Verde', 'Pouco Urgente'),
        ('Azul', 'Não Urgente'),
    ]

    Profissionais = [
        ('Clinica Medica', 'Clinica Medica'),
        ('Ortopedia', 'Ortopedia'),
        ('Pediatria', 'Pediatria'),
        ('Cardiologia', 'Cardiologia'),
        ('Neurologia', 'Neurologia'),
    ]

    nome = models.CharField(max_length=100)
    idade = models.CharField(max_length=3)
    sexo = models.CharField(choices=Sexualidade, max_length=50)
    cpf = models.CharField(max_length=11)
    convenio = models.CharField(choices=Convenios, max_length=50)
    hora_chegada = models.TimeField(blank=True, null=True)

    temperatura = models.FloatField(max_length=3)
    pressaoArterial = models.CharField(max_length=3)
    pulso = models.CharField(max_length=3)
    frequenciaRespiratoria = models.CharField(max_length=3)
    saturacao = models.CharField(max_length=3)
    glicemia = models.CharField(max_length=3)
    dor = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    queixa = models.CharField(max_length=1000)
    inicio_sintomas = models.DateField(blank=True, null=True)
    sintomas_associados = models.CharField(choices=Sintomas, max_length=50)
    observacoes = models.CharField(blank=True, null=True, max_length=1000)

    classificacao = models.CharField(choices=Risco, max_length=50,blank=True, null=True)
    justificativa = models.CharField(max_length=200,blank=True, null=True)
    encaminhamento = models.CharField(choices=Profissionais, max_length=50,blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status, default='Aguardando',blank=True, null=True)

    atendente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='pacientes_criados')

    def save(self, *args, **kwargs):
        campos_necessarios_ia = [
            self.temperatura,
            self.pressaoArterial,
            self.pulso,
            self.frequenciaRespiratoria,
            self.saturacao,
            self.glicemia,
            self.dor,
            self.sintomas_associados,
            self.queixa
        ]
        # se não tiver classificacao definida, predizer
        if not self.classificacao and all(campo is not None and campo != '' for campo in campos_necessarios_ia):
            data = {
                'temperatura': self.temperatura,
                'pressaoArterial': self.pressaoArterial,
                'pulso': self.pulso,
                'frequenciaRespiratoria': self.frequenciaRespiratoria,
                'saturacao': self.saturacao,
                'glicemia': self.glicemia,
                'dor': self.dor,
                'sintomas_associados': self.sintomas_associados,
                'queixa': self.queixa,
            }
            try:
                pred, probs = predict_from_dict(data)
                self.classificacao = pred
            except Exception as e:
                # logar erro e prosseguir sem quebrar
                import logging
                logging.exception("Erro ao predizer classificação: %s", e)
        super().save(*args, **kwargs)
    
    @property
    def status_risco(self):
        if self.classificacao == 'Vermelho':
            return 'Crítico'
        elif self.classificacao in ['Laranja', 'Amarelo']:
            return 'Urgente'
        else:
            return 'Normal'

    def __str__(self):
        return self.nome
    
    atendente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Não deleta o paciente se o atendente for removido
        null=True,
        blank=True,
        related_name='pacientes_criados'
    )