from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

# --- 1. CADASTRO DE FORNECEDORES ---
class Fornecedor(models.Model):
    SEGMENTOS = [
        ('PAPEL', 'Papéis e Adesivos'),
        ('INSUMO', 'Insumos e Acabamentos'),
        ('IMPRESSORA', 'Tonners e Suprimentos'),
    ]

    nome_empresa = models.CharField(max_length=100, verbose_name="Razão Social / Nome")
    contato = models.CharField(max_length=100, blank=True, verbose_name="Pessoa de Contato")
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    segmento = models.CharField(
        max_length=10, 
        choices=SEGMENTOS, 
        default='PAPEL',
        help_text="Define onde este fornecedor aparecerá nas listas de seleção."
    )

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
    
    # NOVOS CAMPOS DE DIMENSÃO (Base para o cálculo futuro)
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

    # Cria uma "Label" bonita juntando os números para exibir na tela
    def formato_legivel(self):
        return f"{self.largura_mm}x{self.altura_mm}mm"
    formato_legivel.short_description = "Formato"

    def __str__(self):
        return f"{self.nome} {self.gramatura} ({self.largura_mm}x{self.altura_mm})"


# --- 3. HISTÓRICO DE COMPRAS (ENTRADAS) ---
class CompraPapel(models.Model):
    papel = models.ForeignKey(Papel, on_delete=models.CASCADE, related_name='compras')
    data_compra = models.DateField()
    
    # Vínculo com Fornecedor (Filtrando apenas quem vende PAPEL ou AMBOS)
    fornecedor = models.ForeignKey(
        Fornecedor, 
        on_delete=models.PROTECT, 
        limit_choices_to={'segmento__in': ['PAPEL', 'IMPRESSORA']}
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
        self.papel.ultimo_valor_pacote = self.valor_pacote # <--- Atualiza o valor do pacote lá
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


# --- 5. INSUMOS DIVERSOS ---
class Insumo(models.Model):
    CATEGORIAS = [
        ('ESPIRAL', 'Espiral'),
        ('WIREO', 'Wire-o'),
        ('CAPA', 'Capa (Acetato/PP)'),
        ('PAPELAO', 'Papelão (Capa Dura)'),
        ('OUTRO', 'Outro'),
    ]
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='OUTRO')
    
    # Filtra fornecedores de INSUMO ou AMBOS
    fornecedor = models.ForeignKey(
        Fornecedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'segmento__in': ['INSUMO', 'AMBOS']}
    )
    
    qtd_embalagem = models.IntegerField(verbose_name="Qtd. na Embalagem")
    valor_pacote = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pacote")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=4, editable=False)
    
    class Meta:
        verbose_name = "Catálogo: Insumo"
        verbose_name_plural = "Catálogo: Insumos"

    def save(self, *args, **kwargs):
        if self.qtd_embalagem and self.valor_pacote:
            self.valor_unitario = self.valor_pacote / self.qtd_embalagem
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome