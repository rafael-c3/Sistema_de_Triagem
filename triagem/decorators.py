from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    """
    Decorator que verifica se o usuário é um superusuário (admin).
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
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