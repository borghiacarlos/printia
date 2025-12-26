from django.contrib import admin
from django.utils.html import format_html 
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    RangeDateFilter, 
    MultipleRelatedDropdownFilter,
    DropdownFilter
)
from django.utils.formats import number_format
from django.db.models import Sum, F, DecimalField # <--- Importante para os cálculos dos Cards

# CORREÇÃO: Removido TabelaPrecoInsumo das importações pois não existe mais
from .models import (
    Papel, CompraPapel, SaidaEstoque, Fornecedor, TabelaPrecoPapel,
    Insumo, CompraInsumo, CategoriaInsumo,
    Acabamento, TabelaPrecoAcabamento, CategoriaAcabamento
)

@admin.register(Fornecedor)
class FornecedorAdmin(ModelAdmin):
    list_display = ['nome_empresa', 'contato', 'telefone', 'segmento']
    search_fields = ['nome_empresa', 'contato']
    list_filter = ['segmento']
    
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/vanilla-masker@1.2.0/build/vanilla-masker.min.js',
            'js/masks.js',
        )

# INLINES
class TabelaPrecoPapelInline(TabularInline):
    model = TabelaPrecoPapel
    extra = 1
    tab = True
    fields = ['qtd_minima', 'valor_venda']
    verbose_name = "Faixa de Preço"
    verbose_name_plural = "Tabela de Preços de Venda (Papel + Click)"

# CORREÇÃO: Removido TabelaPrecoInsumoInline (Não usamos mais tabela de venda para insumo)

class TabelaPrecoAcabamentoInline(TabularInline):
    model = TabelaPrecoAcabamento
    extra = 1
    tab = True
    fields = ['qtd_minima', 'valor_venda']
    verbose_name = "Faixa de Preço"
    verbose_name_plural = "Tabela de Venda (Serviço)"

# ADMINS
@admin.register(Papel)
class PapelAdmin(ModelAdmin):
    change_list_template = "admin/materiais/papel/change_list.html"

    list_display = ['nome', 'gramatura', 'formato_legivel', 'estoque_atual', 'exibir_valor_pacote', 'exibir_preco_atual', 'exibir_faixas_preco']
    search_fields = ['nome', 'gramatura']

    readonly_fields = ['estoque_atual', 'ultimo_preco_unitario', 'ultimo_valor_pacote']
    
    inlines = [TabelaPrecoPapelInline]
    
    fieldsets = (
        (None, {'fields': ('nome', 'gramatura', 'tipo')}),
        ('Dimensões', {'fields': (('largura_mm', 'altura_mm'),)}),
        ('Estoque e Preço de Custo', {'fields': ('estoque_atual', 'ultimo_valor_pacote', 'ultimo_preco_unitario')}),
    )

    def exibir_faixas_preco(self, obj):
        precos = obj.tabela_precos.all()[:3] 
        if not precos:
            return "-"
        return f"De R$ {number_format(precos[0].valor_venda, 2)} a R$ {number_format(precos[len(precos)-1].valor_venda, 2)}"
    exibir_faixas_preco.short_description = "Escala de Venda"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
            
        metrics = {
            'total_papeis': qs.count(),
            'total_pacotes': qs.aggregate(Sum('estoque_atual'))['estoque_atual__sum'] or 0,
            'valor_estoque': qs.aggregate(
                total=Sum(F('estoque_atual') * F('ultimo_valor_pacote'), output_field=DecimalField())
            )['total'] or 0
        }
        response.context_data['kpi'] = metrics
        return response

    def exibir_preco_atual(self, obj):
        valor = number_format(obj.ultimo_preco_unitario, decimal_pos=4)
        return f"R$ {valor}"
    exibir_preco_atual.short_description = "Preço Folha"
    
    def exibir_valor_pacote(self, obj):
        valor = number_format(obj.ultimo_valor_pacote, decimal_pos=2)
        return f"R$ {valor}"
    exibir_valor_pacote.short_description = "Último pct Pago"

@admin.register(CompraPapel)
class CompraPapelAdmin(ModelAdmin):
    list_display = ['papel', 'data_formatada', 'fornecedor', 'qtd_pacotes_compra', 'valor_pacote', 'exibir_unitario']
    list_filter = [
        ('data_compra', RangeDateFilter), 
        ('papel', MultipleRelatedDropdownFilter), 
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
        ('papel', MultipleRelatedDropdownFilter), 
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

# --- HELPERS E BADGES ---
def criar_badge(texto, cor):
    cores_map = {
        'red': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'blue': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'green': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'orange': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
        'purple': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
        'gray': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    }
    classe_cor = cores_map.get(cor, cores_map['gray'])
    return format_html(
        '<span class="px-2.5 py-0.5 rounded-md text-xs font-medium {}">{}</span>',
        classe_cor,
        texto
    )

@admin.register(CategoriaInsumo)
class CategoriaInsumoAdmin(ModelAdmin):
    list_display = ['nome', 'visualizacao_cor']
    
    def visualizacao_cor(self, obj):
        return criar_badge(obj.nome, obj.cor)
    visualizacao_cor.short_description = "Visualização"

@admin.register(CategoriaAcabamento)
class CategoriaAcabamentoAdmin(ModelAdmin):
    list_display = ['nome', 'visualizacao_cor']
    
    def visualizacao_cor(self, obj):
        return criar_badge(obj.nome, obj.cor)
    visualizacao_cor.short_description = "Visualização"

@admin.register(Insumo)
class InsumoAdmin(ModelAdmin):
    list_display = ['nome', 'exibir_tag', 'unidade_medida', 'exibir_custo']
    search_fields = ['nome']
    list_filter = [('categoria', MultipleRelatedDropdownFilter)]
    
    fieldsets = (
        (None, {'fields': ('nome', 'categoria', 'unidade_medida')}),
        ('Custo e Estoque', {'fields': ('estoque_atual', 'ultimo_preco_custo')}),
    )
    readonly_fields = ['estoque_atual', 'ultimo_preco_custo']

    def exibir_tag(self, obj):
        if obj.categoria:
            return criar_badge(obj.categoria.nome, obj.categoria.cor)
        return "-"
    exibir_tag.short_description = "Categoria"

    def exibir_custo(self, obj):
        val = number_format(obj.ultimo_preco_custo, decimal_pos=4)
        return f"R$ {val}"
    exibir_custo.short_description = "Custo Unit."

@admin.register(CompraInsumo)
class CompraInsumoAdmin(ModelAdmin):
    list_display = ['insumo', 'data_compra', 'fornecedor', 'qtd_compra', 'exibir_total', 'exibir_unitario']
    list_filter = [
        ('data_compra', RangeDateFilter),
        ('insumo', MultipleRelatedDropdownFilter),
        ('fornecedor', MultipleRelatedDropdownFilter),
    ]
    autocomplete_fields = ['insumo', 'fornecedor']

    def exibir_total(self, obj):
        return f"R$ {number_format(obj.valor_total_nota, 2)}"
    exibir_total.short_description = "Total Nota"

    def exibir_unitario(self, obj):
        return f"R$ {number_format(obj.valor_unitario, 4)}"
    exibir_unitario.short_description = "Custo Calc."

@admin.register(Acabamento)
class AcabamentoAdmin(ModelAdmin):
    list_display = ['nome', 'exibir_tag', 'exibir_faixas']
    search_fields = ['nome']
    list_filter = [('categoria', MultipleRelatedDropdownFilter)]
    
    inlines = [TabelaPrecoAcabamentoInline]

    def exibir_tag(self, obj):
        if obj.categoria:
            return criar_badge(obj.categoria.nome, obj.categoria.cor)
        return "-"
    exibir_tag.short_description = "Categoria"

    def exibir_faixas(self, obj):
        precos = obj.tabela_precos.all()
        if not precos: return "-"
        return f"Inicia em R$ {number_format(precos[0].valor_venda, 2)}"
    exibir_faixas.short_description = "Preço Base"