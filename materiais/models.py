from django.db import models
from django.db.models import F

class Papel(models.Model):
    # --- O CADASTRO ÚNICO (CATÁLOGO) ---
    nome = models.CharField(max_length=100)
    gramatura = models.CharField(max_length=20)
    formato = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    
    # Este campo guardará sempre o preço da ÚLTIMA compra para facilitar o cálculo
    ultimo_preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, editable=False, 
        verbose_name="Preço Atual (Unitário)"
    )

    class Meta:
        verbose_name = "Catálogo de Papel"
        verbose_name_plural = "Catálogo de Papéis"
        ordering = ['nome', 'gramatura']

    def __str__(self):
        return f"{self.nome} {self.gramatura} ({self.formato})"


class CompraPapel(models.Model):
    # --- O HISTÓRICO (MOVIMENTAÇÃO) ---
    papel = models.ForeignKey(Papel, on_delete=models.CASCADE, related_name='compras')
    
    data_compra = models.DateField()
    fornecedor = models.CharField(max_length=100)
    
    qtd_embalagem = models.IntegerField(verbose_name="Qtd. no Pacote")
    valor_pacote = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago (Pacote)")
    
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=4, editable=False)

    class Meta:
        verbose_name = "Entrada de Estoque"
        verbose_name_plural = "Histórico de Compras"
        ordering = ['-data_compra'] # Ordena do mais recente para o antigo

    def save(self, *args, **kwargs):
        # 1. Calcula o unitário desta compra específica
        if self.qtd_embalagem and self.valor_pacote:
            self.valor_unitario = self.valor_pacote / self.qtd_embalagem
        
        super().save(*args, **kwargs)
        
        # 2. A MÁGICA: Atualiza o preço no Catálogo (Pai) automaticamente
        # Pega o papel relacionado e atualiza o campo de preço
        self.papel.ultimo_preco_unitario = self.valor_unitario
        self.papel.save()

    def __str__(self):
        return f"Compra de {self.papel} em {self.data_compra}"

class Insumo(models.Model):
    nome = models.CharField(max_length=100)
    unidade = models.CharField(max_length=20, help_text="Ex: un, metro, litro, etc")
    
    ultimo_preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, editable=False, 
        verbose_name="Preço Atual (Unitário)"
    )

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

    def __str__(self):
        return self.nome