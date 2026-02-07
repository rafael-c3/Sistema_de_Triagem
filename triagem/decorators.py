from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Agora verifica se o usuário é superuser OU se tem o tipo de usuário 'ADMIN'
        if not (request.user.is_superuser or (request.user.is_authenticated and request.user.tipo_usuario == 'ADMIN')):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def medico_required(view_func):
    """
    Decorator que verifica se o usuário é do tipo 'MEDICO' ou um superusuário.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Um admin pode acessar tudo
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se o usuário é médico
        if request.user.is_authenticated and request.user.tipo_usuario == 'MEDICO':
            return view_func(request, *args, **kwargs)
        
        # Se não for nenhum dos dois, nega a permissão
        raise PermissionDenied
    return _wrapped_view


def atendente_required(view_func):
    """
    Decorator que verifica se o usuário é do tipo 'ATENDENTE' ou um superusuário.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
            
        if request.user.is_authenticated and request.user.tipo_usuario == 'ATENDENTE':
            return view_func(request, *args, **kwargs)
            
        raise PermissionDenied
    return _wrapped_view

def enfermeiro_required(view_func):
    """
    Decorator que verifica se o usuário é Enfermeiro ou superusuário.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.tipo_usuario == 'ENFERMEIRO':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def pode_realizar_triagem_required(view_func):
    """
    Decorator que verifica se o usuário tem permissão para criar
    um novo paciente (Atendentes e Técnicos de Enfermagem).
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
            
        if request.user.is_authenticated and request.user.tipo_usuario in ['ATENDENTE', 'ENFERMEIRO']:
            return view_func(request, *args, **kwargs)
            
        raise PermissionDenied
    return _wrapped_view

# 1. Crie esta função de verificação (pode ser logo acima da view)
def pode_editar_cadastro(user):
    # Verifica se está logado E se o tipo é um dos permitidos
    return user.is_authenticated and (user.tipo_usuario == 'ADMIN' or user.tipo_usuario == 'ATENDENTE')