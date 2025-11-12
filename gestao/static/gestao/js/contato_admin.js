window.addEventListener('load', function() {

    // Garante que temos o atalho seguro para o jQuery do Django
    const $ = django.jQuery;

    console.log("--- SCRIPT DO CONTATO CARREGADO ---");

    // --- LÓGICA DAS MÁSCARAS DE INPUT ---

    $('#id_data_nascimento').mask('00/00/0000');
    $('#id_cpf').mask('000.000.000-00', {reverse: true});
    $('#id_cnpj').mask('00.000.000/0000-00', {reverse: true});
    $('#id_cep').mask('00000-000');

    // Máscara inteligente que se adapta a telefone fixo ou celular
    var phoneMaskBehavior = function (val) {
        return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
    };
    var phoneOptions = {
        onKeyPress: function(val, e, field, options) {
            field.mask(phoneMaskBehavior.apply({}, arguments), options);
        }
    };

    $('#id_celular').mask(phoneMaskBehavior, phoneOptions);
    $('#id_telefone_fixo').mask(phoneMaskBehavior, phoneOptions);
});