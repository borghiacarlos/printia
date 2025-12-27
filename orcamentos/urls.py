from django.urls import path
from .views import NovoOrcamentoView, htmx_calcular_aproveitamento

app_name = 'orcamentos'

urlpatterns = [
    path('novo/', NovoOrcamentoView.as_view(), name='novo_orcamento'),
    
    # Rota exclusiva para o HTMX
    path('htmx/aproveitamento/', htmx_calcular_aproveitamento, name='htmx_aproveitamento'),
]