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

# ... (Mantenha todo o código anterior: Fornecedor, Papel, Insumo, Acabamento) ...

# ==========================================
# 7. GESTÃO DE CUSTO DE IMPRESSÃO (CLICK)
# ==========================================

class Impressora(models.Model):
    # DADOS GERAIS
    nome = models.CharField(max_length=100, help_text="Apelido da máquina. Ex: Konica 01")
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    
    # FORMATO MÁXIMO (Para travar orçamento se o papel for maior que a máquina)
    largura_max_mm = models.IntegerField(verbose_name="Largura Máx (mm)")
    altura_max_mm = models.IntegerField(verbose_name="Altura Máx (mm)")
    
    # CUSTOS CALCULADOS (Cache para não processar tudo a cada orçamento)
    custo_click_mono = models.DecimalField(max_digits=10, decimal_places=4, default=0, editable=False, verbose_name="Custo Click (P&B)")
    custo_click_color = models.DecimalField(max_digits=10, decimal_places=4, default=0, editable=False, verbose_name="Custo Click (Cor)")
    
    # RELATÓRIO
    contador_total_atual = models.IntegerField(default=0, verbose_name="Contador Geral Atual")

    class Meta:
        verbose_name = "Ativo: Impressora"
        verbose_name_plural = "Ativos: Impressoras"

    def __str__(self):
        return f"{self.nome} ({self.modelo})"
    
    def recalcular_custos(self):
        """
        Soma o custo médio de todos os componentes ativos desta impressora.
        Separa o que é custo P&B (K) do que é Color (C, M, Y).
        """
        componentes = self.componentes.all()
        custo_k = 0
        custo_cmy = 0
        
        for comp in componentes:
            if comp.cor == 'K':
                custo_k += float(comp.custo_medio_por_pagina)
            elif comp.cor in ['C', 'M', 'Y']:
                custo_cmy += float(comp.custo_medio_por_pagina)
            else:
                # Peças gerais (Fusor/Belt) entram no custo de ambas ou rateado?
                # Por simplicidade, vamos somar peças gerais no custo base P&B e Color
                custo_k += float(comp.custo_medio_por_pagina)
                custo_cmy += float(comp.custo_medio_por_pagina)
        
        self.custo_click_mono = custo_k
        self.custo_click_color = custo_k + custo_cmy # Click Color geralmente inclui o K
        self.save()


class ComponenteImpressora(models.Model):
    CORES = [
        ('K', 'Preto (Black)'),
        ('C', 'Ciano'),
        ('M', 'Magenta'),
        ('Y', 'Amarelo'),
        ('ALL', 'Peça Geral (Fusor/Belt/Etc)'),
    ]
    
    impressora = models.ForeignKey(Impressora, on_delete=models.CASCADE, related_name='componentes')
    nome = models.CharField(max_length=100, help_text="Ex: Toner TN-619K, Cilindro DR-512")
    tipo = models.CharField(max_length=50, help_text="Toner, Cilindro, Revelador, etc.")
    cor = models.CharField(max_length=5, choices=CORES, default='K')
    
    # PARÂMETROS PARA O PRIMEIRO CÁLCULO (QUANDO NÃO HÁ HISTÓRICO)
    rendimento_estimado = models.IntegerField(verbose_name="Rendimento Padrão (Pág)", help_text="Estimativa de fábrica para o primeiro cálculo")
    
    # DADOS REAIS (MÉDIA HISTÓRICA)
    custo_medio_por_pagina = models.DecimalField(max_digits=12, decimal_places=5, default=0, editable=False)
    
    class Meta:
        verbose_name = "Suprimento / Componente"
        verbose_name_plural = "Suprimentos e Componentes"
        
    def __str__(self):
        return f"{self.nome} ({self.get_cor_display()})"

    def atualizar_media_custo(self):
        """
        A LÓGICA PEDIDA: Média de TODAS as trocas realizadas.
        Custo = Total Gasto Historicamente / Total Páginas Produzidas Historicamente
        """
        trocas = self.trocas.all().order_by('data_troca')
        
        if not trocas.exists():
            # Sem histórico? Usa estimativa base.
            # Precisamos de um valor de referência. Se não houver troca, assumimos R$ 0,00 ou esperamos a primeira compra?
            # Para não quebrar, vamos deixar 0 até a primeira compra.
            return

        total_gasto = trocas.aggregate(Sum('valor_compra'))['valor_compra__sum'] or 0
        total_paginas = trocas.aggregate(Sum('rendimento_real'))['rendimento_real__sum'] or 0
        
        # Se for a primeira troca e não tivermos rendimento anterior calculado ainda
        # O sistema vai usar a estimativa padrão para a primeira divisão se total_paginas for 0
        if total_paginas > 0:
            self.custo_medio_por_pagina = total_gasto / total_paginas
        else:
            # Fallback para primeira inserção: Custo da 1ª compra / Rendimento Estimado
            ultima = trocas.last()
            if ultima and self.rendimento_estimado > 0:
                self.custo_medio_por_pagina = ultima.valor_compra / self.rendimento_estimado
                
        self.save()
        # Avisa a impressora para somar tudo de novo
        self.impressora.recalcular_custos()


class TrocaSuprimento(models.Model):
    componente = models.ForeignKey(ComponenteImpressora, on_delete=models.CASCADE, related_name='trocas')
    data_troca = models.DateField()
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, limit_choices_to={'segmento__in': ['IMPRESSORA', 'AMBOS']})
    
    contador_no_momento = models.IntegerField(verbose_name="Contador da Máquina", help_text="Valor total do contador no momento da troca")
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago (R$)")
    
    # Campo calculado: Quanto durou o suprimento ANTERIOR a este?
    rendimento_real = models.IntegerField(default=0, editable=False, verbose_name="Rendimento Real (Pág)")

    class Meta:
        verbose_name = "Movimento: Troca/Compra"
        verbose_name_plural = "Movimento: Trocas de Suprimentos"
        ordering = ['-data_troca']

    def save(self, *args, **kwargs):
        # 1. Tentar encontrar a troca anterior para calcular o rendimento
        # Buscamos a última troca deste componente com contador MENOR que o atual
        ultima_troca = TrocaSuprimento.objects.filter(
            componente=self.componente,
            contador_no_momento__lt=self.contador_no_momento
        ).order_by('-contador_no_momento').first()

        if ultima_troca:
            # A diferença é quanto o suprimento ANTERIOR durou
            rendimento = self.contador_no_momento - ultima_troca.contador_no_momento
            # Atualizamos o registro ANTERIOR com o rendimento real dele
            # (Porque só sabemos quanto durou o Toner 1 quando colocamos o Toner 2)
            ultima_troca.rendimento_real = rendimento
            ultima_troca.save(update_fields=['rendimento_real'])
            
            # Para o registro ATUAL, o rendimento é 0 (pois acabou de entrar)
            # ou podemos usar o estimado provisoriamente
            self.rendimento_real = 0 
        else:
            # É o primeiro registro da história.
            # Não temos como calcular rendimento real ainda.
            self.rendimento_real = 0

        super().save(*args, **kwargs)
        
        # 2. Atualiza o contador geral da impressora
        self.componente.impressora.contador_total_atual = self.contador_no_momento
        self.componente.impressora.save()
        
        # 3. Recalcula a média global do componente
        self.componente.atualizar_media_custo()


# Leitura Mensal Simples (apenas para registro)
class LeituraImpressora(models.Model):
    impressora = models.ForeignKey(Impressora, on_delete=models.CASCADE)
    data_leitura = models.DateField()
    contador_total = models.IntegerField()
    
    class Meta:
        verbose_name = "Relatório: Leitura Mensal"
        verbose_name_plural = "Relatório: Leituras Mensais"
        ordering = ['-data_leitura']

class GuilhotinaConfig(models.Model):
    gramatura_min = models.IntegerField(default=0, verbose_name="Gramatura Mínima")
    gramatura_max = models.IntegerField(default=999, verbose_name="Gramatura Máxima")
    folhas_por_corte = models.IntegerField(help_text="Quantas folhas a guilhotina corta por vez (batida) nesta faixa?")

    class Meta:
        ordering = ['gramatura_min']
        verbose_name = "Capacidade de Guilhotina"
        verbose_name_plural = "Configuração de Guilhotina"

    def __str__(self):
        return f"{self.gramatura_min}g até {self.gramatura_max}g: {self.folhas_por_corte} fls/corte"