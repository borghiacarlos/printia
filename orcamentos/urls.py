from django.urls import path
from . import views
from .views import NovoOrcamentoView, htmx_calcular_aproveitamento, configuracoes_view

app_name = 'orcamentos'

urlpatterns = [
    path('novo/', NovoOrcamentoView.as_view(), name='novo_orcamento'),
    
    path('configuracoes/', configuracoes_view, name='configuracoes'),

    path('htmx/aproveitamento/', htmx_calcular_aproveitamento, name='htmx_aproveitamento'),

    path('htmx/buscar-cliente/', views.buscar_cliente, name='buscar_cliente'),
]