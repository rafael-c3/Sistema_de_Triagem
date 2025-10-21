from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .ml.predict import predict_from_dict
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date

class UnidadeSaude(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    # Adicione outros campos relevantes: CNPJ, endereço, telefone, etc.
    # ...

    def __str__(self):
        return self.nome

class CustomUser(AbstractUser):
    unidade_saude = models.ForeignKey(UnidadeSaude, on_delete=models.CASCADE, null=True) # Campo OBRIGATÓRIO
    class TipoUsuario(models.TextChoices):
        ATENDENTE = 'ATENDENTE', 'Atendente'
        MEDICO = 'MEDICO', 'Médico'
        TECNICO_ENFERMAGEM = 'TECNICO_ENFERMAGEM', 'Téc. de Enfermagem' # <-- NOVO TIPO
        ADMIN = 'ADMIN', 'Admin'

    UF_CHOICES = [
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'), 
        ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'), 
        ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'), 
        ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'), 
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'), 
        ('SE', 'SE'), ('TO', 'TO'),
    ]

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
    cpf = models.CharField(max_length=14, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=TipoUsuario.choices, default=TipoUsuario.ATENDENTE)

    crm = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRM (Apenas para Médicos)")    
    especializacao = models.CharField(max_length=50, choices=Especializacoes,blank=True,null=True)

    coren = models.CharField(max_length=20, blank=True, null=True, verbose_name="COREN (Apenas para Téc. de Enfermagem)")

    uf_registro = models.CharField(max_length=2, choices=UF_CHOICES, blank=True, null=True, verbose_name="UF do Registro Profissional")

    foto_perfil = models.ImageField(upload_to='fotos_perfil/', default='fotos_perfil/default.jpg', null=True,blank=True,verbose_name="Foto de Perfil")
    
    @property
    def registro_formatado(self):
        """Retorna o registro profissional (CRM ou COREN) formatado com a UF."""
        if self.tipo_usuario == self.TipoUsuario.MEDICO and self.crm and self.uf_registro:
            return f"CRM-{self.uf_registro} {self.crm}"
        elif self.tipo_usuario == self.TipoUsuario.TECNICO_ENFERMAGEM and self.coren and self.uf_registro:
            return f"COREN-{self.uf_registro} {self.coren}"
        return "-" # Retorna um traço se não houver registro aplicável
    
    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['email', 'nome_completo', 'cpf']


class Paciente(models.Model):
    unidade_saude = models.ForeignKey(UnidadeSaude, on_delete=models.CASCADE, null=True) # Campo OBRIGATÓRIO

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
        ('Pendente', 'Pendente'),
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
    cpf = models.CharField(unique=True, max_length=14)
    convenio = models.CharField(choices=Convenios, max_length=50)

    nome_responsavel = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome do Responsável")
    cpf_responsavel = models.CharField(max_length=11, blank=True, null=True, verbose_name="CPF do Responsável")

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

    status = models.CharField(max_length=30, choices=Status, default='Pendente',blank=True, null=True)
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
        """Calcula e formata o tempo desde a chegada até o início do atendimento."""
        # A "cláusula de guarda": se algum dos valores for Nulo, pare aqui.
        if not self.hora_chegada or not self.hora_inicio_atendimento:
            return "Em andamento"
        
        delta = self.hora_inicio_atendimento - self.hora_chegada
        
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0: total_seconds = 0

        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        segundos = total_seconds % 60

        if horas > 0:
            return f"{horas}h {minutos}min {segundos}s"
        elif minutos > 0:
            return f"{minutos}min {segundos}s"
        else:
            return f"{segundos}s"

    @property
    def tempo_de_atendimento(self):
        """Calcula e formata a duração do atendimento."""
        # A "cláusula de guarda" para esta propriedade
        if not self.hora_inicio_atendimento or not self.hora_fim_atendimento:
            return "Em andamento"
        
        delta = self.hora_fim_atendimento - self.hora_inicio_atendimento
        
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0: total_seconds = 0

        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        segundos = total_seconds % 60

        if horas > 0:
            return f"{horas}h {minutos}min {segundos}s"
        elif minutos > 0:
            return f"{minutos}min {segundos}s"
        else:
            return f"{segundos}s"


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
    unidade_saude = models.ForeignKey(UnidadeSaude, on_delete=models.CASCADE, null=True) # Campo OBRIGATÓRIO

    # Usamos OneToOneField para garantir que cada paciente só tenha UM feedback
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    
    # Quem deu o feedback
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Campos do formulário de feedback
    triagem_correta = models.BooleanField(verbose_name="A classificação do sistema foi correta?")
    classificacao_correta = models.CharField(max_length=50, choices=Paciente.Risco, blank=True, null=True, verbose_name="Se não, qual seria a classificação correta?")
    motivo = models.TextField(blank=True, null=True, verbose_name="Motivo da reclassificação")

    # Data de criação do feedback
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback para {self.paciente.nome} por {self.usuario.username}"
    
    class StatusFeedback(models.TextChoices):
        EM_ANALISE = 'EM_ANALISE', 'Em Análise'
        ACATADO = 'ACATADO', 'Acatado'
        NAO_ACATADO = 'NAO_ACATADO', 'Não Acatado'

    status = models.CharField(
        max_length=20,
        choices=StatusFeedback.choices,
        default=StatusFeedback.EM_ANALISE, # Todo novo feedback começa "Em Análise"
        verbose_name="Status do Feedback"
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback para {self.paciente.nome} por {self.usuario.username}"
    
class EntradaProntuario(models.Model):
    unidade_saude = models.ForeignKey(UnidadeSaude, on_delete=models.CASCADE, null=True) # Campo OBRIGATÓRIO

    # Relação com o Paciente. Se o paciente for deletado, as anotações vão junto.
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historico_prontuario')
    
    # Relação com o profissional que escreveu a nota
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # O conteúdo da anotação
    texto = models.TextField(verbose_name="Descrição do Atendimento / Observação")
    
    # Data/hora em que a anotação foi criada
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que as novas entradas sempre apareçam no topo
        ordering = ['-data_criacao'] 

    def __str__(self):
        return f"Entrada em {self.data_criacao.strftime('%d/%m/%y %H:%M')} para {self.paciente.nome}"
    
class AnexoPaciente(models.Model):
    unidade_saude = models.ForeignKey(UnidadeSaude, on_delete=models.CASCADE, null=True) # Campo OBRIGATÓRIO

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='anexos')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    descricao = models.CharField(max_length=100, verbose_name="Descrição do Arquivo")
    arquivo = models.FileField(upload_to='anexos_pacientes/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - {self.paciente.nome}"
    
class LogAcao(models.Model):
    unidade_saude = models.ForeignKey(UnidadeSaude, on_delete=models.CASCADE, null=True) # Campo OBRIGATÓRIO

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Mantém o log mesmo se o usuário for deletado
        null=True, 
        blank=True, 
        verbose_name="Usuário"
    )
    acao = models.CharField(max_length=255, verbose_name="Ação Realizada")
    detalhes = models.TextField(blank=True, null=True, verbose_name="Detalhes Adicionais")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    class Meta:
        ordering = ['-timestamp'] # Ordena do mais recente para o mais antigo
        verbose_name = "Registro de Auditoria"
        verbose_name_plural = "Registros de Auditoria"

    def __str__(self):
        user_display = self.usuario.username if self.usuario else "Sistema"
        return f"{self.timestamp.strftime('%d/%m/%y %H:%M')} - {user_display} - {self.acao}"
