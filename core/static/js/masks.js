document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Máscara de Telefone (Mantido) ---
    function inputHandler(masks, max, event) {
        var c = event.target;
        var v = c.value.replace(/\D/g, '');
        var m = c.value.length > max ? 1 : 0;
        VMasker(c).maskPattern(masks[m]);
        c.value = VMasker.toPattern(v, masks[m]);
    }

    var telMask = ['(99) 9999-99999', '(99) 99999-9999'];
    var telInputs = document.querySelectorAll('input[name*="telefone"]');

    if (typeof VMasker !== 'undefined') {
        telInputs.forEach(function (input) {
            VMasker(input).maskPattern(telMask[0]);
            input.addEventListener('input', inputHandler.bind(undefined, telMask, 14), false);
        });

        // --- 2. Máscara de Documento (CPF / CNPJ) ---
        // Seletor mais genérico para garantir que encontre o campo 'cliente-documento'
        var docInput = document.querySelector('input[id$="documento"]');
        var tipoSelect = document.querySelector('select[id$="tipo"]');

        if (docInput && tipoSelect) {

            function applyDocMask() {
                var tipo = tipoSelect.value; // 'PF' ou 'PJ'

                // Remove formatação antiga para evitar bugs visuais ao trocar
                // var valueClean = docInput.value.replace(/\D/g, '');

                if (tipo === 'PJ') {
                    // Máscara CNPJ
                    VMasker(docInput).maskPattern('99.999.999/9999-99');
                    // Força a atualização do placeholder
                    docInput.setAttribute('placeholder', '00.000.000/0000-00');
                } else {
                    // Máscara CPF
                    VMasker(docInput).maskPattern('999.999.999-99');
                    // Força a atualização do placeholder
                    docInput.setAttribute('placeholder', '000.000.000-00');
                }
            }

            // Aplica imediatamente ao carregar
            applyDocMask();

            // Reaplica quando o tipo mudar
            tipoSelect.addEventListener('change', function () {
                docInput.value = ''; // Limpa valor para não misturar máscaras
                applyDocMask();
            });

            // Garante a máscara no input
            docInput.addEventListener('input', applyDocMask);
        }
    }
});