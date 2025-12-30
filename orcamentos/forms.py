from django import forms
from .models import Cliente, Orcamento, ItemOrcamento, ConfiguracaoGlobal
from materiais.models import Acabamento, Insumo

# --- ESTILOS "UNFOLD" (Tailwind) ---
# Inputs de Texto e Número
INPUT_CLASS = (
    "block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 "
    "placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 "
    "dark:bg-gray-800 dark:text-gray-300 dark:ring-gray-700 dark:focus:ring-primary-500 transition-shadow duration-200"
)

CHEVRON_SVG = "data:image/svg+xml,%3csvg%20xmlns='http://www.w3.org/2000/svg'%20fill='none'%20viewBox='0%200%2020%2020'%3e%3cpath%20stroke='%236b7280'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='1.5'%20d='M6%208l4%204%204-4'/%3e%3c/svg%3e"

# Selects (Dropdowns)
SELECT_CLASS = (
    f"block w-full rounded-md border-0 pl-3 pr-10 h-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 "
    f"focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 "
    f"dark:bg-gray-800 dark:text-gray-300 dark:ring-gray-700 dark:focus:ring-primary-500 transition-shadow duration-200 "
    f"appearance-none bg-white dark:bg-gray-800 bg-no-repeat "
    f"bg-[url(\"{CHEVRON_SVG}\")] bg-[length:1.5em_1.5em] bg-[right_0.5rem_center]"
)

# Select Multiple (Caixa alta para acabamentos)
SELECT_MULTIPLE_CLASS = (
    "block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 "
    "dark:bg-gray-800 dark:text-gray-300 dark:ring-gray-700 min-h-[120px] transition-shadow duration-200"
)

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo', 'nome', 'nome_fantasia', 'documento', 'telefone', 'email']
        widgets = {
            'tipo': forms.Select(attrs={'class': SELECT_CLASS, 'x-model': 'tipoCliente'}),
            'nome': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ex: Gráfica Rápida Ltda'}),
            'nome_fantasia': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'documento': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'CPF ou CNPJ'}),
            'telefone': forms.TextInput(attrs={'class': INPUT_CLASS, 'data-mask': 'phone', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'contato@email.com'}),
        }

class ItemOrcamentoForm(forms.ModelForm):
    # Campo extra para quantidades
    quantidades_input = forms.CharField(
        label="Quantidades",
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS, 
            'placeholder': 'Ex: 100, 500, 1000',
            'autocomplete': 'off'
        })
    )
    
    # Acabamentos e Insumos com visual melhorado
    acabamentos = forms.ModelMultipleChoiceField(
        queryset=Acabamento.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': SELECT_MULTIPLE_CLASS})
    )
    
    insumos = forms.ModelMultipleChoiceField(
        queryset=Insumo.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': SELECT_MULTIPLE_CLASS})
    )

    class Meta:
        model = ItemOrcamento
        fields = ['titulo', 'largura_final_mm', 'altura_final_mm', 'sangria_mm', 'papel', 'impressora', 'cor_impressao', 'paginas', 'acabamentos', 'insumos']
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
            'cor_impressao': forms.Select(attrs={'class': SELECT_CLASS}),
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