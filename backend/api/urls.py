# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuração do Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Documentation API NGE",
        default_version='v2',
        description="Documentação da API utilizando Swagger - Funcionalidade desenvolvidas Por Fagner Costa",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="fagner.costa@ifam.edu.br"),
        license=openapi.License(name="Licença MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('nansen.urls')),
    # Rotas do Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
