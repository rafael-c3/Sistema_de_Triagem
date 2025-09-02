from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .ml.predict import predict_from_dict
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date

class CustomUser(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ATENDENTE = 'ATENDENTE', 'Atendente'
        MEDICO = 'MEDICO', 'Médico'
        ADMIN = 'ADMIN', 'Admin'

    Especializacoes = [
        ('CLINICA_GERAL', 'Clínica Geral'),
        ('CARDIOLOGIA', 'Cardiologia'),
        ('ORTOPEDIA', 'Ortopedia'),
        ('PEDIATRIA', 'Pediatria'),
        ('NEUROLOGIA', 'Neurologia'),
        ('OUTRA', 'Outra')
    ]

    nome_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    tipo_usuario = models.CharField(max_length=10, choices=TipoUsuario.choices, default=TipoUsuario.ATENDENTE)

    registro_profissional = models.CharField(max_length=20, blank=True, null=True)   # Permite que o valor seja nulo no banco
    especializacao = models.CharField(max_length=50, choices=Especializacoes,blank=True,null=True)

    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['email', 'nome_completo', 'cpf']


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
    # idade = models.CharField(max_length=3)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    sexo = models.CharField(choices=Sexualidade, max_length=50)
    cpf = models.CharField(unique=True, max_length=11)
    convenio = models.CharField(choices=Convenios, max_length=50)

    temperatura = models.FloatField(max_length=3)
    pressao_sistolica = models.CharField(max_length=3) # Valor maior
    pressao_diastolica = models.CharField(max_length=3) # Valor menor
    pulso = models.CharField(max_length=3)
    frequenciaRespiratoria = models.CharField(max_length=3)
    saturacao = models.CharField(max_length=3)
    glicemia = models.CharField(max_length=3)
    dor = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    queixa = models.CharField(max_length=1000)
    inicio_sintomas = models.DateField()
    sintomas_associados = models.CharField(choices=Sintomas, max_length=50)
    observacoes = models.CharField(blank=True, null=True, max_length=1000)

    classificacao = models.CharField(choices=Risco, max_length=50,blank=True, null=True)
    justificativa = models.CharField(blank=True, null=True)
    encaminhamento = models.CharField(choices=Profissionais, max_length=50,blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status, default='Aguardando',blank=True, null=True)
    hora_chegada = models.DateTimeField(default=timezone.now, blank=True)
    hora_inicio_atendimento = models.DateTimeField(null=True, blank=True)
    hora_fim_atendimento = models.DateTimeField(null=True, blank=True)

    atendente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pacientes_criados')
    medico_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='pacientes_atendidos', null=True, blank=True)

    @property
    def idade(self):
        """Calcula a idade do paciente com base na data de nascimento."""
        if not self.data_nascimento:
            return None # Retorna nada se a data de nascimento não estiver preenchida
            
        hoje = date.today()
        # O cálculo subtrai os anos e depois ajusta -1 se o aniversário ainda não passou no ano corrente
        idade_calculada = hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return idade_calculada
    
    @property
    def tempo_de_espera(self):
        """Calcula o tempo desde a chegada até o início do atendimento."""
        if self.hora_chegada and self.hora_inicio_atendimento:
            return self.hora_inicio_atendimento - self.hora_chegada
        return None

    @property
    def tempo_de_atendimento(self):
        """Calcula a duração do atendimento."""
        if self.hora_inicio_atendimento and self.hora_fim_atendimento:
            return self.hora_fim_atendimento - self.hora_inicio_atendimento
        return None

    def save(self, *args, **kwargs):
        campos_necessarios_ia = [
            self.temperatura,
            self.pressao_sistolica,
            self.pressao_diastolica,
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
                'pressao_sistolica': self.pressao_sistolica,
                'pressao_diastolica': self.pressao_diastolica,
                'pulso': self.pulso,
                'frequenciaRespiratoria': self.frequenciaRespiratoria,
                'saturacao': self.saturacao,
                'glicemia': self.glicemia,
                'dor': self.dor,
                'sintomas_associados': self.sintomas_associados,
                'queixa': self.queixa,
            }
            try:
                pred, probs, justificativa_ia = predict_from_dict(data)
                self.classificacao = pred
                self.justificativa = justificativa_ia

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
        
    @property
    def pressao_arterial(self):
        """Retorna a pressão arterial no formato 'Sistólica/Diastólica'."""
        return f"{self.pressao_sistolica}/{self.pressao_diastolica}"

    def __str__(self):
        return self.nome
    
class FeedbackTriagem(models.Model):
    # Usamos OneToOneField para garantir que cada paciente só tenha UM feedback
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    
    # Quem deu o feedback
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Campos do formulário de feedback
    triagem_correta = models.BooleanField(default=True, verbose_name="A classificação do sistema foi correta?")
    classificacao_correta = models.CharField(max_length=50, choices=Paciente.Risco, blank=True, null=True, verbose_name="Se não, qual seria a classificação correta?")
    motivo = models.TextField(blank=True, null=True, verbose_name="Motivo da reclassificação")

    # Data de criação do feedback
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback para {self.paciente.nome} por {self.usuario.username}"