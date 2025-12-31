from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ConfiguracaoGlobal, Cliente
from materiais.models import Papel
from .utils import calcular_imposicao
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ClienteForm, ItemOrcamentoForm, ConfiguracaoGlobalForm
from django.views.generic import TemplateView, ListView  # Adicionado ListView
from django.db.models import Q                           # Adicionado Q

class NovoOrcamentoView(LoginRequiredMixin, TemplateView):
    template_name = "orcamentos/novo_orcamento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mantemos os formulários no contexto
        context['form_cliente'] = ClienteForm(prefix='cliente')
        context['form_item'] = ItemOrcamentoForm(prefix='item') 
        return context

    def post(self, request, *args, **kwargs):
        # Captura apenas os dados do formulário de Cliente
        form_cliente = ClienteForm(request.POST, prefix='cliente')
        
        # Instanciamos o form_item apenas para não quebrar a validação visual, 
        # mas não vamos salvá-lo agora.
        form_item = ItemOrcamentoForm(request.POST, prefix='item')

        if form_cliente.is_valid():
            try:
                # Lógica para Salvar ou Atualizar Cliente pelo Documento
                cliente_data = form_cliente.cleaned_data
                documento = cliente_data.get('documento')
                
                if documento:
                    # Se tem documento, tenta atualizar ou criar (evita duplicados)
                    cliente, created = Cliente.objects.update_or_create(
                        documento=documento,
                        defaults=cliente_data
                    )
                    acao = "cadastrado" if created else "atualizado"
                else:
                    # Se não tem documento, cria um novo sempre
                    cliente = form_cliente.save()
                    acao = "cadastrado"

                messages.success(request, f"Cliente {cliente.nome} {acao} com sucesso!")
                
                # Redireciona para a nova lista de clientes
                return redirect('orcamentos:lista_clientes')

            except Exception as e:
                messages.error(request, f"Erro ao salvar cliente: {e}")
        else:
            messages.error(request, "Verifique os dados do formulário.")

        # Se algo deu errado, recarrega a página mantendo os dados preenchidos
        return render(request, self.template_name, {
            'form_cliente': form_cliente,
            'form_item': form_item
        })

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

class ClientesListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "orcamentos/clientes.html"
    context_object_name = "clientes"
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('q')
        # Filtra por Nome, Documento ou Email
        if query:
            qs = qs.filter(
                Q(nome__icontains=query) | 
                Q(documento__icontains=query) |
                Q(email__icontains=query)
            )
        return qs.order_by('-id')