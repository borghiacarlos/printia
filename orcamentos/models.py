from django.db import models
from django.contrib.auth.models import User
from materiais.models import Papel, Impressora, Acabamento, Insumo

# ==========================================
# 1. CLIENTES (CRM SIMPLIFICADO)
# ==========================================

class Cliente(models.Model):
    TIPO_PESSOA = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]
    
    tipo = models.CharField(max_length=2, choices=TIPO_PESSOA, default='PF')
    nome = models.CharField(max_length=150, verbose_name="Nome / Razão Social")
    
    # Campos opcionais dependendo do tipo (Validaremos no Frontend/Form)
    nome_fantasia = models.CharField(max_length=150, blank=True, null=True)
    documento = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    
    telefone = models.CharField(max_length=20, verbose_name="Telefone/Celular")
    email = models.EmailField(blank=True, null=True)
    contato = models.CharField(max_length=100, blank=True, null=True, help_text="Nome de quem pediu o orçamento (para PJ)")
    
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.tipo == 'PJ' and self.nome_fantasia:
            return f"{self.nome_fantasia} ({self.contato})"
        return self.nome
    
    class Meta:
        ordering = ['nome']


# ==========================================
# 2. O CABEÇALHO DO ORÇAMENTO
# ==========================================

class Orcamento(models.Model):
    STATUS = [
        ('EM_ANALISE', 'Em Análise / Rascunho'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    validade_dias = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS, default='EM_ANALISE')

    # TOTAIS E TAXAS GERAIS
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frete/Entrega")
    
    # Percentuais (Padrões definidos no Prompt)
    percentual_imposto = models.DecimalField(max_digits=5, decimal_places=2, default=8.00, verbose_name="Imposto (%)")
    percentual_comissao = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name="Comissão (%)")
    percentual_cartao = models.DecimalField(max_digits=5, decimal_places=2, default=8.00, verbose_name="Taxa Cartão (%)")
    
    # Resultado Final
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.cliente}"


# ==========================================
# 3. O PRODUTO (ITEM DO ORÇAMENTO)
# ==========================================

class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    titulo = models.CharField(max_length=100, help_text="Ex: Cartão de Visita, Catálogo, Folder")
    quantidade = models.IntegerField(default=100)
    
    # Dimensões e Sangria (Para cálculo de aproveitamento)
    largura_final_mm = models.IntegerField(verbose_name="Largura Final (mm)")
    altura_final_mm = models.IntegerField(verbose_name="Altura Final (mm)")
    sangria_mm = models.IntegerField(default=3, verbose_name="Sangria (mm)")
    
    # Configuração de Refile (Guilhotina)
    capacidade_corte_folhas = models.IntegerField(default=250, help_text="Quantas folhas a guilhotina corta por vez (maço)?")

    def __str__(self):
        return f"{self.titulo} ({self.quantidade} un)"


# ==========================================
# 4. AS PARTES DO PRODUTO (CAPA, MIOLO, ETC)
# ==========================================
# Aqui entra a lógica de "Duplicar": Um catálogo tem "Capa" e "Miolo".
# Um cartão de visita só tem uma parte (Corpo).

class ParteItem(models.Model):
    CORES_ESCOLHA = [
        ('4x4', 'Colorido Frente e Verso'),
        ('4x0', 'Colorido Somente Frente'),
        ('1x1', 'Preto Frente e Verso'),
        ('1x0', 'Preto Somente Frente'),
        ('0x0', 'Sem Impressão (Apenas Papel)'),
    ]

    item = models.ForeignKey(ItemOrcamento, on_delete=models.CASCADE, related_name='partes')
    nome_parte = models.CharField(max_length=50, default="Corpo", help_text="Ex: Capa, Miolo, Encarte")
    
    papel = models.ForeignKey(Papel, on_delete=models.PROTECT)
    impressora = models.ForeignKey(Impressora, on_delete=models.PROTECT)
    
    # O numero de páginas desta parte (Ex: Miolo tem 50 páginas. Capa tem 2 paginas/lados)
    paginas = models.IntegerField(default=1, verbose_name="Nº Páginas/Lâminas") 
    
    cor_impressao = models.CharField(max_length=3, choices=CORES_ESCOLHA, default='4x0')
    
    # Aproveitamento calculado (será preenchido via HTMX/Backend)
    formato_papel_usado = models.CharField(max_length=50, editable=False) # Ex: 330x480mm
    itens_por_folha = models.IntegerField(default=0, verbose_name="Aproveitamento (un/fl)")
    
    # Margem de segurança técnica (pinça)
    margem_papel_top = models.IntegerField(default=5, verbose_name="Margem Topo (mm)")
    margem_papel_bottom = models.IntegerField(default=5, verbose_name="Margem Base (mm)")
    margem_papel_left = models.IntegerField(default=5, verbose_name="Margem Esq (mm)")
    margem_papel_right = models.IntegerField(default=5, verbose_name="Margem Dir (mm)")

    def __str__(self):
        return f"{self.nome_parte} - {self.papel.nome}"


# ==========================================
# 5. EXTRAS (ACABAMENTOS E INSUMOS)
# ==========================================

class AcabamentoItem(models.Model):
    item = models.ForeignKey(ItemOrcamento, on_delete=models.CASCADE, related_name='acabamentos')
    acabamento = models.ForeignKey(Acabamento, on_delete=models.PROTECT)
    
    # Quantidade de aplicação (Geralmente é igual à qtd do item, mas pode variar)
    quantidade = models.IntegerField(help_text="Quantidade a aplicar (geralmente igual à tiragem)")
    observacao = models.CharField(max_length=100, blank=True)

class InsumoItem(models.Model):
    item = models.ForeignKey(ItemOrcamento, on_delete=models.CASCADE, related_name='insumos')
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT)
    quantidade_consumida = models.DecimalField(max_digits=10, decimal_places=4, help_text="Qtd total consumida no pedido")