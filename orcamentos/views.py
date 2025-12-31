from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ConfiguracaoGlobal, Cliente
from materiais.models import Papel
from .utils import calcular_imposicao
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ClienteForm, ItemOrcamentoForm, ConfiguracaoGlobalForm

class NovoOrcamentoView(LoginRequiredMixin, TemplateView):
    template_name = "orcamentos/novo_orcamento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Injetamos os formulários no contexto para renderizar no template
        context['form_cliente'] = ClienteForm(prefix='cliente')
        context['form_item'] = ItemOrcamentoForm(prefix='item')
        
        return context

def htmx_calcular_aproveitamento(request):
    try:
        # 1. Coleta dados do Request
        largura_final = float(request.GET.get('item-largura_final_mm') or 0)
        altura_final = float(request.GET.get('item-altura_final_mm') or 0)
        sangria = float(request.GET.get('item-sangria_mm') or 0)
        papel_id = request.GET.get('item-papel')
        
        # 2. Validações básicas
        if not papel_id or largura_final == 0 or altura_final == 0:
            return render(request, 'orcamentos/partials/aproveitamento_vazio.html')

        papel = Papel.objects.get(pk=papel_id)
        
        # Tamanho total do "corte" (Item + Sangria de cada lado)
        corte_w = largura_final + (sangria * 2)
        corte_h = altura_final + (sangria * 2)

        # 3. Faz o Cálculo
        resultado = calcular_imposicao(
            papel.largura_mm, 
            papel.altura_mm, 
            corte_w, 
            corte_h
        )

        if not resultado:
            return render(request, 'orcamentos/partials/aproveitamento_vazio.html')

        # 4. Prepara contexto para o template
        context = {
            'papel': papel,
            'resultado': resultado,
            'corte_w': corte_w,
            'corte_h': corte_h,
        }
        return render(request, 'orcamentos/partials/aproveitamento_resultado.html', context)

    except Exception as e:
        print(f"Erro no cálculo: {e}")
        return render(request, 'orcamentos/partials/aproveitamento_vazio.html')

def configuracoes_view(request):
    # Pega a config existente ou cria a primeira (ID=1)
    config, created = ConfiguracaoGlobal.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = ConfiguracaoGlobalForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações atualizadas com sucesso!")
            return redirect('configuracoes')
    else:
        form = ConfiguracaoGlobalForm(instance=config)

    return render(request, 'orcamentos/configuracoes.html', {'form': form})

def buscar_cliente(request):
    query = request.GET.get('q', '')
    clientes = []
    
    if len(query) > 2: # Só busca se tiver mais de 2 caracteres
        clientes = Cliente.objects.filter(
            nome__icontains=query
        )[:5] # Limita a 5 resultados
        
        # Se quiser buscar por documento também:
        # from django.db.models import Q
        # clientes = Cliente.objects.filter(Q(nome__icontains=query) | Q(documento__icontains=query))[:5]

    return render(request, 'orcamentos/partials/resultados_busca_cliente.html', {'clientes': clientes})