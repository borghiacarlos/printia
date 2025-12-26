from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

# --- UTILS: Cores para as Tags (Padrão Tailwind do Unfold) ---
COLORS = [
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('amber', 'Amarelo'),
    ('green', 'Verde'),
    ('teal', 'Verde Água'),
    ('blue', 'Azul'),
    ('indigo', 'Indigo'),
    ('purple', 'Roxo'),
    ('pink', 'Rosa'),
    ('gray', 'Cinza'),
]

# --- 1. CADASTRO DE FORNECEDORES ---
class Fornecedor(models.Model):
    # SEUS NOVOS SEGMENTOS CORRIGIDOS
    SEGMENTOS = [
        ('PAPEL', 'Papéis e Adesivos'),
        ('INSUMO', 'Insumos e Acabamentos'),
        ('IMPRESSORA', 'Tonners e Suprimentos'),
    ]

    nome_empresa = models.CharField(max_length=100, verbose_name="Razão Social / Nome")
    contato = models.CharField(max_length=100, blank=True, verbose_name="Pessoa de Contato")
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    segmento = models.CharField(max_length=10, choices=SEGMENTOS, default='PAPEL')

    class Meta:
        verbose_name_plural = "Cadastros: Fornecedores"
        ordering = ['nome_empresa']

    def __str__(self):
        return self.nome_empresa


# --- 2. CATÁLOGO DE PAPÉIS ---
class Papel(models.Model):
    nome = models.CharField(max_length=100, help_text="Ex: Couchê, Offset, Adesivo")
    gramatura = models.CharField(max_length=20, help_text="Ex: 90g, 150g")
    tipo = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: Fosco, Brilho")
    
    largura_mm = models.IntegerField(verbose_name="Largura (mm)", help_text="Ex: 330")
    altura_mm = models.IntegerField(verbose_name="Altura (mm)", help_text="Ex: 480")
    
    estoque_atual = models.IntegerField(default=0, editable=False, verbose_name="Estoque (Pcts)")

    ultimo_valor_pacote = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False, 
        verbose_name="Último Pago (Pacote)"
    )

    ultimo_preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, editable=False, 
        verbose_name="Preço Atual (Folha)"
    )

    class Meta:
        verbose_name = "Catálogo: Papel"
        verbose_name_plural = "Catálogo: Papéis"
        ordering = ['nome', 'gramatura']

    def atualizar_estoque(self):
        total_entradas = self.compras.aggregate(total=Sum('qtd_pacotes_compra'))['total'] or 0
        total_saidas = self.saidas.aggregate(total=Sum('qtd_pacotes_baixa'))['total'] or 0
        self.estoque_atual = total_entradas - total_saidas
        self.save()

    def formato_legivel(self):
        return f"{self.largura_mm}x{self.altura_mm}mm"
    formato_legivel.short_description = "Formato"

    def __str__(self):
        return f"{self.nome} {self.gramatura} ({self.largura_mm}x{self.altura_mm})"


# --- 3. HISTÓRICO DE COMPRAS (ENTRADAS) ---
class CompraPapel(models.Model):
    papel = models.ForeignKey(Papel, on_delete=models.CASCADE, related_name='compras')
    data_compra = models.DateField()
    
    # CORREÇÃO: Removido 'AMBOS' que não existe mais e mantido coerência
    fornecedor = models.ForeignKey(
        Fornecedor, 
        on_delete=models.PROTECT, 
        limit_choices_to={'segmento__in': ['PAPEL']} 
    )
    
    qtd_pacotes_compra = models.IntegerField(default=1, verbose_name="Qtd. Pacotes")
    qtd_embalagem = models.IntegerField(verbose_name="Folhas por Pacote")
    valor_pacote = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Pacote")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=4, editable=False)

    class Meta:
        verbose_name = "Movimento: Compra de Papel"
        verbose_name_plural = "Movimento: Compras de Papel"
        ordering = ['-data_compra']

    def save(self, *args, **kwargs):
        if self.qtd_embalagem and self.valor_pacote:
            self.valor_unitario = self.valor_pacote / self.qtd_embalagem
        super().save(*args, **kwargs)
        self.papel.ultimo_preco_unitario = self.valor_unitario
        self.papel.ultimo_valor_pacote = self.valor_pacote
        self.papel.atualizar_estoque()


# --- 4. BAIXAS (SAÍDAS) ---
class SaidaEstoque(models.Model):
    papel = models.ForeignKey(Papel, on_delete=models.CASCADE, related_name='saidas')
    data_movimento = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    qtd_pacotes_baixa = models.IntegerField(verbose_name="Qtd. Pacotes Usados")
    observacao = models.CharField(max_length=100, blank=True, verbose_name="Motivo/Obs")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)

    class Meta:
        verbose_name = "Movimento: Baixa"
        verbose_name_plural = "Movimento: Baixas / Uso Interno"
        ordering = ['-data_movimento']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.papel.atualizar_estoque()

class TabelaPrecoPapel(models.Model):
    papel = models.ForeignKey(Papel, on_delete=models.CASCADE, related_name='tabela_precos')
    qtd_minima = models.IntegerField(verbose_name="A partir de (unid.)", help_text="Quantidade mínima para aplicar este preço")
    valor_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda (unid.)")

    class Meta:
        verbose_name = "Faixa de Preço"
        verbose_name_plural = "Tabela de Preços"
        ordering = ['qtd_minima']

    def __str__(self):
        return f">= {self.qtd_minima} un: R$ {self.valor_venda}"

# --- 5. INSUMOS (Somente Custo) ---

class CategoriaInsumo(models.Model):
    nome = models.CharField(max_length=50)
    cor = models.CharField(max_length=20, choices=COLORS, default='gray')

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Config: Categ. de Insumo"
        verbose_name_plural = "Config: Tags de Insumos"

class Insumo(models.Model):
    nome = models.CharField(max_length=100, help_text="Ex: Espiral 12mm, Capa PP, Cola Hotmelt")
    categoria = models.ForeignKey(CategoriaInsumo, on_delete=models.SET_NULL, null=True, verbose_name="Tag / Categoria")
    unidade_medida = models.CharField(max_length=20, default="unid", help_text="Ex: kg, litro, caixa, milheiro")
    
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Estoque Atual")
    
    ultimo_preco_custo = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, editable=False, 
        verbose_name="Último Custo (Unitário)"
    )

    class Meta:
        verbose_name = "Catálogo: Insumo"
        verbose_name_plural = "Catálogo: Insumos"
        ordering = ['nome']

    def atualizar_estoque_custo(self):
        total_entradas = self.compras.aggregate(total=Sum('qtd_compra'))['total'] or 0
        self.estoque_atual = total_entradas 
        self.save()

    def __str__(self):
        return self.nome

class CompraInsumo(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='compras')
    data_compra = models.DateField()
    
    # CORREÇÃO: Filtra apenas quem vende INSUMO (removemos AMBOS)
    fornecedor = models.ForeignKey(
        Fornecedor, 
        on_delete=models.PROTECT, 
        limit_choices_to={'segmento__in': ['INSUMO']}
    )
    
    qtd_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade Comprada")
    valor_total_nota = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total da Nota")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=4, editable=False, verbose_name="Custo Unitário")

    class Meta:
        verbose_name = "Movimento: Compra de Insumo"
        verbose_name_plural = "Movimento: Compras de Insumo"
        ordering = ['-data_compra']

    def save(self, *args, **kwargs):
        if self.qtd_compra and self.valor_total_nota:
            self.valor_unitario = self.valor_total_nota / self.qtd_compra
        super().save(*args, **kwargs)
        self.insumo.ultimo_preco_custo = self.valor_unitario
        self.insumo.atualizar_estoque_custo()

# --- 6. ACABAMENTOS (Serviços e Venda) ---

class CategoriaAcabamento(models.Model):
    nome = models.CharField(max_length=50)
    cor = models.CharField(max_length=20, choices=COLORS, default='blue')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Config: Categ. de Acabamento"
        verbose_name_plural = "Config: Tags de Acabamentos"

class Acabamento(models.Model):
    nome = models.CharField(max_length=100, help_text="Ex: Encadernação Wire-o A4, Refile, Vinco")
    categoria = models.ForeignKey(CategoriaAcabamento, on_delete=models.SET_NULL, null=True, verbose_name="Tag / Categoria")
    descricao = models.TextField(blank=True, help_text="Detalhes técnicos do serviço")

    class Meta:
        verbose_name = "Serviço: Acabamento"
        verbose_name_plural = "Serviço: Acabamentos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class TabelaPrecoAcabamento(models.Model):
    acabamento = models.ForeignKey(Acabamento, on_delete=models.CASCADE, related_name='tabela_precos')
    qtd_minima = models.IntegerField(verbose_name="A partir de (unid.)")
    valor_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço do Serviço (unid.)")

    class Meta:
        verbose_name = "Faixa de Preço"
        verbose_name_plural = "Tabela de Preços"
        ordering = ['qtd_minima']

    def __str__(self):
        return f">= {self.qtd_minima}: R$ {self.valor_venda}"