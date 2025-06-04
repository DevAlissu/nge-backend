from rest_framework.permissions import BasePermission

ADMIN = 'ADMIN'
GERENTE = 'GERENTE'
OPERADOR = 'OPERADOR'
    


class IsAdmin(BasePermission):
    """
    Permissão personalizada que permite o acesso apenas a usuários com a função 'ADMIN'.
    """

    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e tem a função 'ADMIN'
        return request.user.is_authenticated and request.user.role == ADMIN
    
class IsOperador(BasePermission):
    """
    Permissão personalizada que permite o acesso apenas a usuários com a função 'ADMIN'.
    """

    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e tem a função 'OPERADOR'
        return request.user.is_authenticated and request.user.role == OPERADOR
    
class IsGerente(BasePermission):
    """
    Permissão personalizada que permite o acesso apenas a usuários com a função 'ADMIN'.
    """

    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e tem a função 'OPERADOR'
        return request.user.is_authenticated and request.user.role == GERENTE