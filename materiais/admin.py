from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, MultipleRelatedDropdownFilter, MultipleChoicesDropdownFilter, DropdownFilter
from django.db.models import Sum, F, DecimalField
from django.utils.formats import number_format

from .models import Papel, CompraPapel, SaidaEstoque, Insumo, Fornecedor

@admin.register(Fornecedor)
class FornecedorAdmin(ModelAdmin):
    list_display = ['nome_empresa', 'contato', 'telefone', 'segmento']
    search_fields = ['nome_empresa', 'contato']
    list_filter = ['segmento']
    
    # Injeta o Script de Máscara e a biblioteca VMasker (CDN)
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/vanilla-masker@1.2.0/build/vanilla-masker.min.js',
            'js/masks.js',
        )

@admin.register(Papel)
class PapelAdmin(ModelAdmin):
    change_list_template = "admin/materiais/papel/change_list.html"

    list_display = ['nome', 'gramatura', 'formato_legivel', 'estoque_atual', 'exibir_valor_pacote', 'exibir_preco_atual']
    search_fields = ['nome', 'gramatura']

    readonly_fields = ['estoque_atual', 'ultimo_preco_unitario', 'ultimo_valor_pacote']
    
    fieldsets = (
        (None, {'fields': ('nome', 'gramatura', 'tipo')}),
        ('Dimensões', {'fields': (('largura_mm', 'altura_mm'),)}),
        ('Estoque e Preço', {'fields': ('estoque_atual', 'ultimo_valor_pacote', 'ultimo_preco_unitario')}),
    )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        
        # Tenta pegar os dados filtrados (queryset) da tela atual
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            # Se der erro ou não tiver queryset, retorna normal
            return response
            
        # Faz os Cálculos Dinâmicos
        metrics = {
            'total_papeis': qs.count(),
            
            # Soma a coluna estoque_atual
            'total_pacotes': qs.aggregate(Sum('estoque_atual'))['estoque_atual__sum'] or 0,
            
            # Multiplica Estoque * Valor Pacote linha por linha e soma tudo
            'valor_estoque': qs.aggregate(
                total=Sum(F('estoque_atual') * F('ultimo_valor_pacote'), output_field=DecimalField())
            )['total'] or 0
        }
        
        # Injeta os dados no template
        response.context_data['kpi'] = metrics
        
        return response

    def exibir_preco_atual(self, obj):
        # number_format força o uso da vírgula definida no settings
        valor = number_format(obj.ultimo_preco_unitario, decimal_pos=4)
        return f"R$ {valor}"
    exibir_preco_atual.short_description = "Preço Folha"
    
    def exibir_valor_pacote(self, obj):
        valor = number_format(obj.ultimo_valor_pacote, decimal_pos=2)
        return f"R$ {valor}"
    exibir_valor_pacote.short_description = "Último pct Pago"

@admin.register(CompraPapel)
class CompraPapelAdmin(ModelAdmin):
    # Adicionado valor_unitario na listagem
    list_display = ['papel', 'data_formatada', 'fornecedor', 'qtd_pacotes_compra', 'valor_pacote', 'exibir_unitario']
    
    list_filter = [
        ('data_compra', RangeDateFilter), 
        ('papel', MultipleRelatedDropdownFilter), # <--- Permite selecionar múltiplos papéis
        ('fornecedor', MultipleRelatedDropdownFilter),
    ]
    autocomplete_fields = ['papel', 'fornecedor']
    
    def exibir_unitario(self, obj):
        valor = number_format(obj.valor_unitario, decimal_pos=4)
        return f"R$ {valor}"
    exibir_unitario.short_description = "Custo Folha"

    def data_formatada(self, obj):
        return obj.data_compra.strftime('%d/%m/%Y')
    data_formatada.short_description = "Data Compra"

@admin.register(SaidaEstoque)
class SaidaEstoqueAdmin(ModelAdmin):
    list_display = ['data_formatada', 'papel', 'qtd_pacotes_baixa', 'usuario', 'observacao']
    
    list_filter = [
        ('data_movimento', RangeDateFilter), 
        ('papel', MultipleRelatedDropdownFilter), # <--- Permite selecionar múltiplos papéis
        ('usuario', MultipleRelatedDropdownFilter),
    ]
    autocomplete_fields = ['papel']
    fields = ['papel', 'qtd_pacotes_baixa', 'observacao']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def data_formatada(self, obj):
        return obj.data_movimento.strftime('%d/%m/%Y às %H:%M')
    data_formatada.short_description = "Data/Hora"

@admin.register(Insumo)
class InsumoAdmin(ModelAdmin):
    list_display = ['nome', 'categoria', 'fornecedor', 'valor_unitario']
    list_filter = ['categoria']
    search_fields = ['nome']
    autocomplete_fields = ['fornecedor']