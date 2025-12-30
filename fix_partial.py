
import os

content = r"""{% load l10n %}

<div id="aproveitamento-visual"
    class="mt-6 w-full bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 p-6 flex flex-col items-center shadow-inner transition-all duration-300 ease-in-out">

    <div class="w-full flex justify-between items-end mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
        <div class="flex flex-col">
            <span class="text-xs text-gray-400 uppercase tracking-wider font-semibold">Papel Selecionado</span>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ papel.largura_mm }} <span class="text-gray-400">x</span> {{ papel.altura_mm }} mm
            </span>
        </div>
        <div class="flex flex-col text-right">
            <span class="text-xs text-gray-400 uppercase tracking-wider font-semibold">Aproveitamento</span>
            <span class="text-2xl font-bold text-primary-600 dark:text-primary-400 leading-none">
                {{ resultado.total }} <span class="text-sm font-normal text-gray-500">un/fl</span>
            </span>
        </div>
    </div>

    {% localize off %}
    <div
        class="relative w-full h-80 flex justify-center items-center bg-gray-200/50 dark:bg-gray-900/50 rounded-lg p-4 overflow-hidden">

        <svg viewBox="0 0 {{ papel.largura_mm }} {{ papel.altura_mm }}"
            class="max-h-full max-w-full shadow-md bg-white transition-transform duration-500">

            <rect width="100%" height="100%" fill="white" />

            <rect x="5" y="5" width="{{ papel.largura_mm|add:'-10' }}" height="{{ papel.altura_mm|add:'-10' }}"
                fill="none" stroke="#ef4444" stroke-width="0.5" stroke-dasharray="8" opacity="0.3" />

            {% for rect in resultado.rectangles %}
            <rect x="{{ rect.x }}" y="{{ rect.y }}" width="{{ resultado.item_w_final }}"
                height="{{ resultado.item_h_final }}" fill="#ddd6fe" stroke="#7c3aed" stroke-width="0.5" />
            {% endfor %}

        </svg>
    </div>

    <div
        class="mt-4 w-full flex justify-between text-xs text-gray-500 bg-white dark:bg-gray-900 p-2 rounded border border-gray-100 dark:border-gray-700">
        <div class="flex gap-4">
            <span>Orientacao: <strong class="text-gray-700 dark:text-gray-300">{% if resultado.orientacao %}{{ resultado.orientacao|title }}{% endif %}</strong></span>
            <span>Corte Final: <strong class="text-gray-700 dark:text-gray-300">{% if corte_w and corte_h %}{{ corte_w }}x{{ corte_h }}mm{% endif %}</strong></span>
        </div>
        <div class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-red-400 opacity-50"></span>
            <span>Margem técnica (5mm)</span>
        </div>
    </div>
    {% endlocalize %}
</div>

<input type="number" name="item-itens_por_folha" id="id_item-itens_por_folha" value="{{ resultado.total }}"
    class="w-full border-gray-200 rounded-md text-sm focus:ring-primary-600 focus:border-primary-600 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300 font-bold text-blue-600"
    hx-swap-oob="true">
"""

file_path = r"d:\print_ia\templates\orcamentos\partials\aproveitamento_resultado.html"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content.strip())
print(f"File {file_path} overwritten successfully.")
