from django import forms
from .models import Cliente, Orcamento, ItemOrcamento, ParteItem

# Classe CSS base para inputs estilo Unfold
INPUT_CLASS = "w-full border-gray-200 rounded-md text-sm focus:ring-primary-600 focus:border-primary-600 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300"
SELECT_CLASS = "w-full border-gray-200 rounded-md text-sm focus:ring-primary-600 focus:border-primary-600 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300"

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo', 'nome', 'nome_fantasia', 'documento', 'telefone', 'email', 'contato']
        widgets = {
            'tipo': forms.Select(attrs={'class': SELECT_CLASS, 'x-model': 'tipoCliente'}), # x-model é para o AlpineJS
            'nome': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'nome_fantasia': forms.TextInput(attrs={'class': INPUT_CLASS, 'x-show': "tipoCliente == 'PJ'"}),
            'documento': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'telefone': forms.TextInput(attrs={'class': INPUT_CLASS, 'data-mask': 'phone'}), # data-mask para o JS
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'contato': forms.TextInput(attrs={'class': INPUT_CLASS, 'x-show': "tipoCliente == 'PJ'"}),
        }

class ItemOrcamentoForm(forms.ModelForm):
    class Meta:
        model = ItemOrcamento
        fields = ['titulo', 'quantidade', 'largura_final_mm', 'altura_final_mm', 'sangria_mm', 'capacidade_corte_folhas']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ex: Cartão de Visita'}),
            'quantidade': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'largura_final_mm': forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'step': '0.1',                                # Permite decimais
            'hx-get': '/orcamentos/htmx/aproveitamento/', # Chama a URL
            'hx-trigger': 'keyup changed delay:500ms',    # Espera 500ms após digitar
            'hx-target': '#aproveitamento-visual',        # Onde desenhar o resultado
            'hx-swap': 'outerHTML',                       # Substitui o elemento todo
            'hx-include': 'closest form'                  # Envia TODOS os dados do form
        }),
        'altura_final_mm': forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'step': '0.1',
            'hx-get': '/orcamentos/htmx/aproveitamento/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#aproveitamento-visual',
            'hx-swap': 'outerHTML',
            'hx-include': 'closest form'
        }),
        'sangria_mm': forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'step': '0.1',
            'hx-get': '/orcamentos/htmx/aproveitamento/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#aproveitamento-visual',
            'hx-swap': 'outerHTML',
            'hx-include': 'closest form'
        }),
            'capacidade_corte_folhas': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }

class ParteItemForm(forms.ModelForm):
    class Meta:
        model = ParteItem
        fields = ['nome_parte', 'papel', 'impressora', 'paginas', 'cor_impressao', 'itens_por_folha']
        widgets = {
            'nome_parte': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'papel': forms.Select(attrs={
            'class': SELECT_CLASS,
            'hx-get': '/orcamentos/htmx/aproveitamento/',
            'hx-trigger': 'change',                       # Dispara assim que muda a opção
            'hx-target': '#aproveitamento-visual',
            'hx-swap': 'outerHTML',
            'hx-include': 'closest form'
        }),
            'impressora': forms.Select(attrs={'class': SELECT_CLASS}),
            'paginas': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'cor_impressao': forms.Select(attrs={'class': SELECT_CLASS}),
            'itens_por_folha': forms.NumberInput(attrs={'class': INPUT_CLASS}), # Será readonly ou editável
        }