from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from materiais.models import Papel, Impressora, Acabamento, Insumo

# ==========================================
# 0. CONFIGURAÇÕES GLOBAIS (Singleton)
# ==========================================
class ConfiguracaoGlobal(models.Model):
    # Financeiro
    imposto_padrao = models.DecimalField(max_digits=5, decimal_places=2, default=8.00, verbose_name="Imposto Padrão (%)")
    comissao_padrao = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name="Comissão Padrão (%)")
    taxa_cartao = models.DecimalField(max_digits=5, decimal_places=2, default=4.50, verbose_name="Taxa Cartão (%)")
    
    # Produção
    custo_hora_arte = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, verbose_name="Custo Hora Arte (R$)")
    
    # Layout
    logo_empresa = models.ImageField(upload_to='config/', blank=True, null=True)

    class Meta:
        verbose_name = "Configuração Global"
        verbose_name_plural = "Configurações Globais"

    def save(self, *args, **kwargs):
        # Garante que só exista 1 registro
        if not self.pk and ConfiguracaoGlobal.objects.exists():
            raise ValidationError('Só pode haver uma configuração global.')
        return super(ConfiguracaoGlobal, self).save(*args, **kwargs)

    def __str__(self):
        return "Configurações do Sistema"


# ==========================================
# 1. CLIENTES
# ==========================================
class Cliente(models.Model):
    TIPO_PESSOA = [('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')]
    tipo = models.CharField(max_length=2, choices=TIPO_PESSOA, default='PF')
    nome = models.CharField(max_length=150, verbose_name="Nome / Razão Social")
    nome_fantasia = models.CharField(max_length=150, blank=True, null=True)
    documento = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=20, verbose_name="Telefone/Celular")
    email = models.EmailField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


# ==========================================
# 2. MODELOS PRÉ-CONFIGURADOS (PRESETS)
# ==========================================
class ProdutoModelo(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Nome do Modelo", help_text="Ex: Cartão de Visita Padrão")
    descricao = models.TextField(blank=True, verbose_name="Descrição Interna")
    
    # Especificações Padrão
    largura_final_mm = models.IntegerField(verbose_name="Largura (mm)")
    altura_final_mm = models.IntegerField(verbose_name="Altura (mm)")
    sangria_mm = models.IntegerField(default=3, verbose_name="Sangria (mm)")
    
    # Materiais Sugeridos
    papel_padrao = models.ForeignKey(Papel, on_delete=models.SET_NULL, null=True, blank=True)
    impressora_padrao = models.ForeignKey(Impressora, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Modelo de Produto"
        verbose_name_plural = "Modelos de Produtos"

    def __str__(self):
        return self.titulo


# ==========================================
# 3. O ORÇAMENTO
# ==========================================
class Orcamento(models.Model):
    # ... (Mantenha igual ao código anterior) ...
    STATUS = [('EM_ANALISE', 'Em Análise'), ('APROVADO', 'Aprovado'), ('RECUSADO', 'Recusado')]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='EM_ANALISE')
    
    percentual_imposto = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_comissao = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_cartao = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            config = ConfiguracaoGlobal.objects.first()
            if config:
                self.percentual_imposto = config.imposto_padrao
                self.percentual_comissao = config.comissao_padrao
                self.percentual_cartao = config.taxa_cartao
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.cliente}"


# ==========================================
# 4. ITEM DO ORÇAMENTO (A Especificação)
# ==========================================
class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    titulo = models.CharField(max_length=100, help_text="Ex: Cartão de Visita, Folder")
    
    # Dimensões Finais
    largura_final_mm = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Largura (mm)")
    altura_final_mm = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Altura (mm)")
    sangria_mm = models.DecimalField(max_digits=4, decimal_places=1, default=3, verbose_name="Sangria (mm)")
    
    # Material e Impressão (Trazido do antigo ParteItem)
    papel = models.ForeignKey(Papel, on_delete=models.PROTECT, verbose_name="Papel / Mídia")
    impressora = models.ForeignKey(Impressora, on_delete=models.PROTECT, verbose_name="Máquina")
    cor_impressao = models.CharField(max_length=10, default='4x0', verbose_name="Cores", help_text="Ex: 4x0, 4x4, 1x0")
    paginas = models.IntegerField(default=1, verbose_name="Nº Páginas/Lâminas")
    
    def __str__(self):
        return f"{self.titulo} - {self.papel}"


# ==========================================
# 5. AS TIRAGENS (QUANTIDADES E PREÇOS)
# ==========================================
class ItemOrcamentoTiragem(models.Model):
    item = models.ForeignKey(ItemOrcamento, on_delete=models.CASCADE, related_name='tiragens')
    quantidade = models.IntegerField(verbose_name="Quantidade / Tiragem")
    
    # Custos Detalhados
    custo_papel = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_impressao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_acabamento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totais
    custo_total_producao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_final_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['quantidade']

    def __str__(self):
        return f"{self.quantidade}un - R$ {self.valor_final_venda}"