document.addEventListener('DOMContentLoaded', function () {
    // Função simples de máscara para telefone BR (Celular e Fixo)
    function inputHandler(masks, max, event) {
        var c = event.target;
        var v = c.value.replace(/\D/g, '');
        var m = c.value.length > max ? 1 : 0;
        VMasker(c).maskPattern(masks[m]);
        c.value = VMasker.toPattern(v, masks[m]);
    }

    var telMask = ['(99) 9999-99999', '(99) 99999-9999'];
    var telInputs = document.querySelectorAll('input[name*="telefone"]');

    // Usando uma lib leve que carregaremos via CDN no Admin
    if (typeof VMasker !== 'undefined') {
        telInputs.forEach(function (input) {
            VMasker(input).maskPattern(telMask[0]);
            input.addEventListener('input', inputHandler.bind(undefined, telMask, 14), false);
        });
    }
});