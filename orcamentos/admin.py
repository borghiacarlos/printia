from django.contrib import admin
from .models import Cliente, Orcamento, ItemOrcamento, ItemOrcamentoTiragem, ConfiguracaoGlobal, ProdutoModelo

@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'imposto_padrao')
    def has_add_permission(self, request):
        return not self.model.objects.exists()

@admin.register(ProdutoModelo)
class ProdutoModeloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'papel_padrao')

class ItemTiragemInline(admin.TabularInline):
    model = ItemOrcamentoTiragem
    extra = 0
    readonly_fields = ('valor_final_venda',)

@admin.register(ItemOrcamento)
class ItemOrcamentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'papel', 'impressora')
    inlines = [ItemTiragemInline]

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cliente', 'status', 'data_criacao')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'telefone')