from django import forms
from .models import Cliente, Orcamento, ItemOrcamento, ConfiguracaoGlobal

# Classe CSS base para inputs estilo Unfold
INPUT_CLASS = "w-full border-gray-200 rounded-md text-sm focus:ring-primary-600 focus:border-primary-600 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300"
SELECT_CLASS = "w-full border-gray-200 rounded-md text-sm focus:ring-primary-600 focus:border-primary-600 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300"

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo', 'nome', 'nome_fantasia', 'documento', 'telefone', 'email']
        widgets = {
            'tipo': forms.Select(attrs={'class': SELECT_CLASS, 'x-model': 'tipoCliente'}),
            'nome': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'nome_fantasia': forms.TextInput(attrs={'class': INPUT_CLASS, 'x-show': "tipoCliente == 'PJ'"}),
            'documento': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'telefone': forms.TextInput(attrs={'class': INPUT_CLASS, 'data-mask': 'phone'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
        }

class ItemOrcamentoForm(forms.ModelForm):
    quantidades_input = forms.CharField(
        label="Quantidades a Orçar",
        help_text="Separe por vírgula. Ex: 100, 500, 1000",
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ex: 100, 500, 1000'})
    )
    itens_por_folha = forms.IntegerField(label="Aproveitamento", required=False, widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'readonly': 'readonly'}))

    class Meta:
        model = ItemOrcamento
        fields = ['titulo', 'largura_final_mm', 'altura_final_mm', 'sangria_mm', 'papel', 'impressora', 'cor_impressao', 'paginas']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'largura_final_mm': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.1'}),
            'altura_final_mm': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.1'}),
            'sangria_mm': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.1'}),
            'papel': forms.Select(attrs={
                'class': SELECT_CLASS,
                'hx-get': '/orcamentos/htmx/aproveitamento/',
                'hx-trigger': 'change',
                'hx-target': '#aproveitamento-visual',
                'hx-swap': 'outerHTML',
                'hx-include': 'closest form'
            }),
            'impressora': forms.Select(attrs={'class': SELECT_CLASS}),
            'cor_impressao': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ex: 4x0'}),
            'paginas': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }

class ConfiguracaoGlobalForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoGlobal
        fields = '__all__'
        widgets = {
            'imposto_padrao': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'comissao_padrao': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'taxa_cartao': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'custo_hora_arte': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'logo_empresa': forms.FileInput(attrs={'class': INPUT_CLASS}),
        }