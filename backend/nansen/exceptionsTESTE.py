from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

def nansen_exception_handler(exc, context):
    # Obtenha a resposta padrão do DRF
    response = exception_handler(exc, context)

    # Verifique se a exceção é do tipo JWT inválido
    if isinstance(exc, AuthenticationFailed):
        detail = getattr(exc, 'detail', 'Authentication error')
        response = Response({
            "success": False,
            "error": {
                "code": "authentication_failed",
                "message": "Seu Token é inválido ou expirou. Por favor, faça login novamente.",
                "details": {
                    "falha": "Token Inválido ou expirado"
                }
            }
        }, status=401)

    # Personalize erro de permissão negada
    elif isinstance(exc, PermissionDenied):
        response.data = {
            "success": False,
            "error": {
                "code": "permission_denied",
                "message": "Você não tem permissão para acessar este recurso."
            }
        }
        response.status_code = 403

    # Se a resposta não for nula, personalize outras mensagens, se necessário
    

    return response
