# triagem/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import LogAcao, Paciente, EntradaProntuario, FeedbackTriagem, CustomUser

# --- Sinais de Login/Logout ---

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registra o login do usuário."""
    LogAcao.objects.create(usuario=user, acao="Login realizado")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Registra o logout do usuário."""
    if user: # Garante que existe um usuário associado ao logout
        LogAcao.objects.create(usuario=user, acao="Logout realizado")

# --- Sinais de Criação/Alteração (post_save) ---

@receiver(post_save, sender=Paciente)
def log_paciente_save(sender, instance, created, **kwargs):
    """Registra a criação ou alteração de um Paciente."""
    if created:
        acao_desc = f"Paciente '{instance.nome}' (ID: {instance.pk}) criado."
        LogAcao.objects.create(usuario=instance.atendente, acao=acao_desc) # Associa ao atendente
    else:
        # Aqui poderíamos adicionar lógica para detalhar o que foi alterado,
        # mas por simplicidade, vamos apenas registrar a edição.
        # A informação de quem alterou (médico, admin) é mais difícil de pegar aqui.
        acao_desc = f"Paciente '{instance.nome}' (ID: {instance.pk}) atualizado."
        # Tentamos pegar o usuário da requisição (se disponível) ou deixamos nulo
        # Note: Pegar o 'request.user' aqui é complexo, idealmente faríamos no save() do modelo.
        # Por simplicidade agora, não associaremos usuário à atualização via signal.
        LogAcao.objects.create(acao=acao_desc)

@receiver(post_save, sender=EntradaProntuario)
def log_entrada_prontuario_save(sender, instance, created, **kwargs):
    """Registra a criação de uma nova observação no prontuário."""
    if created:
        acao_desc = f"Observação adicionada ao prontuário do paciente '{instance.paciente.nome}' (ID: {instance.paciente.pk})."
        LogAcao.objects.create(usuario=instance.autor, acao=acao_desc)

@receiver(post_save, sender=FeedbackTriagem)
def log_feedback_save(sender, instance, created, **kwargs):
    """Registra o envio de um feedback."""
    if created:
        acao_desc = f"Feedback enviado para o paciente '{instance.paciente.nome}' (ID: {instance.paciente.pk})."
        LogAcao.objects.create(usuario=instance.usuario, acao=acao_desc)

# --- Sinais de Deleção (post_delete) ---

@receiver(post_delete, sender=Paciente)
def log_paciente_delete(sender, instance, **kwargs):
    """Registra a deleção de um Paciente."""
    # A deleção geralmente é feita por um admin, mas pegar o 'request.user' aqui é difícil.
    acao_desc = f"Paciente '{instance.nome}' (ID: {instance.pk}) DELETADO."
    LogAcao.objects.create(acao=acao_desc)

@receiver(post_delete, sender=EntradaProntuario)
def log_entrada_prontuario_delete(sender, instance, **kwargs):
    """Registra a deleção de uma observação."""
    acao_desc = f"Observação (ID: {instance.pk}) DELETADA do prontuário do paciente '{instance.paciente.nome}'."
    LogAcao.objects.create(acao=acao_desc)

@receiver(post_delete, sender=CustomUser)
def log_user_delete(sender, instance, **kwargs):
    """Registra a deleção de um Usuário."""
    acao_desc = f"Usuário '{instance.username}' (ID: {instance.pk}) DELETADO."
    LogAcao.objects.create(acao=acao_desc)

# --- Sinal para Desativação/Reativação (Mais Complexo com Signal) ---
# A mudança de 'is_active' é uma atualização (post_save), mas precisamos saber QUEM fez.
# A melhor forma é registrar isso DENTRO das views 'desativar_usuario_view' e 'reativar_usuario_view'.

# Exemplo de como registrar na view:
# Dentro de desativar_usuario_view, após o save():
# LogAcao.objects.create(usuario=request.user, acao=f"Usuário '{usuario_a_desativar.username}' desativado.")