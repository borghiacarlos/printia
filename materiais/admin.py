from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter # <--- Importante para o filtro de datas
from .models import Papel, CompraPapel, Insumo

# Configuração do Catálogo (Onde você vê os preços atuais para orçamento)
@admin.register(Papel)
class PapelAdmin(ModelAdmin):
    list_display = ['nome', 'gramatura', 'formato', 'exibir_preco_atual']
    search_fields = ['nome', 'gramatura']
    
    def exibir_preco_atual(self, obj):
        return f"R$ {obj.ultimo_preco_unitario:.4f}"
    exibir_preco_atual.short_description = "Preço Vigente (Unitário)"


# Configuração do Histórico (Onde você lança as compras)
@admin.register(CompraPapel)
class CompraPapelAdmin(ModelAdmin):
    list_display = [
        'papel', 
        'data_formatada',  # <--- Sua data BR
        'fornecedor', 
        'valor_pacote', 
        'exibir_unitario'
    ]
    
    # SEU FILTRO DE DATA AQUI
    list_filter = [
        ('data_compra', RangeDateFilter), # Permite selecionar início e fim
        'fornecedor',
        'papel__nome' # Filtra pelo nome do papel
    ]
    
    # Campo de busca e Autocomplete (Facilita achar o papel)
    autocomplete_fields = ['papel'] 
    
    def exibir_unitario(self, obj):
        return f"R$ {obj.valor_unitario:.4f}"
    exibir_unitario.short_description = "Custo Unitário"

    # Sua formatação de data BR
    def data_formatada(self, obj):
        return obj.data_compra.strftime('%d/%m/%Y')
    data_formatada.short_description = "Data da Compra"