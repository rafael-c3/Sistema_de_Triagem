from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Paciente, CustomUser, FeedbackTriagem, EntradaProntuario
from validate_docbr import CPF

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        exclude = ['atendente']

        labels = {
            'nome': 'Nome',
            'data_nascimento': 'Data de Nascimento',
            'sexo': 'Gênero',
            'cpf': 'CPF',
            'convenio': 'Convenio',
            'hora_chegada': 'Hora de Chegada',

            'nome_responsavel': 'Nome do Responsável',
            'cpf_responsavel': 'CPF do Responsável',

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
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'convenio': forms.Select(attrs={'class': 'form-control'}),
            'hora_chegada': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),

            'nome_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_responsavel': forms.TextInput(attrs={'class': 'form-control'}),

            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'pressao_sistolica': forms.NumberInput(attrs={'class': 'form-control'}),
            'pressao_diastolica': forms.NumberInput(attrs={'class': 'form-control'}),
            'pulso': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequenciaRespiratoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'saturacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'glicemia': forms.NumberInput(attrs={'class': 'form-control'}),
            'dor': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': '0', 'max': '10', 'step': '1'}),

            'queixa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inicio_sintomas': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sintomas_associados': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'classificacao': forms.Select(attrs={'class': 'form-control'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control'}),
            'encaminhamento': forms.Select(attrs={'class': 'form-control'}),

            'status_atendimento': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_cpf(self):
        # Pega o valor do CPF que o usuário digitou
        cpf_value = self.cleaned_data.get('cpf')
        
        if cpf_value:
            # Cria uma instância do validador
            cpf_validator = CPF()
            
            # A biblioteca automaticamente remove pontos e traços
            # e verifica se o CPF é matematicamente válido.
            if not cpf_validator.validate(cpf_value):
                # Se não for válido, levanta um erro de validação
                raise forms.ValidationError("O CPF informado não é válido.")
        
        # Se for válido, retorna o valor para o Django continuar
        return cpf_value
    
class CustomUserCreationForm(UserCreationForm):

    terms_agreement = forms.BooleanField(
        required=True,
        label="Eu li e concordo com os Termos de Uso e Política de Privacidade"
    )
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'nome_completo', 'email', 'cpf', 'tipo_usuario', 'registro_profissional', 'especializacao')

        # === ESTA É A PARTE CRUCIAL QUE FALTAVA ===
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome de usuário'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
            'registro_profissional': forms.TextInput(attrs={'class': 'form-control'}),
            'especializacao': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}),
        }
        # === FIM DA PARTE QUE FALTAVA ===

        # Também é bom definir os labels aqui para garantir consistência
        labels = {
            'username': 'Nome de Usuário *',
            'nome_completo': 'Nome Completo *',
            'email': 'Email *',
            'cpf': 'CPF *',
            'tipo_usuario': 'Tipo de Usuário *',
            'password1': 'Senha *',
            'password2': 'Confirmar Senha *',
        }

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
    
    def clean_cpf(self):
        cpf_value = self.cleaned_data.get('cpf')
        if cpf_value:
            cpf_validator = CPF()
            if not cpf_validator.validate(cpf_value):
                raise forms.ValidationError("O CPF informado não é válido.")
        return cpf_value

class FeedbackTriagemForm(forms.ModelForm):
    class Meta:
        model = FeedbackTriagem
        # Apenas os campos que o usuário deve preencher
        fields = ['triagem_correta', 'classificacao_correta', 'motivo']
        widgets = {
            'triagem_correta': forms.RadioSelect(choices=(
                (True, 'Sim, a classificação estava adequada.'),
                (False, 'Não, a classificação estava inadequada.')
            )),
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

class EntradaProntuarioForm(forms.ModelForm):
    class Meta:
        model = EntradaProntuario
        # O formulário só precisa do campo de texto. Os outros serão preenchidos na view.
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Digite sua observação clínica aqui...'}),
        }
        labels = {
            'texto': '' # Deixamos o label vazio para um visual mais limpo
        }

class ValidacaoTriagemForm(forms.ModelForm):
    class Meta:
        model = Paciente
        # O técnico só precisa poder alterar a classificação
        fields = ['classificacao']
        labels = {
            'classificacao': 'Se a classificação estiver incorreta, selecione a correta:'
        }