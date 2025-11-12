window.addEventListener('load', function() {
    const $ = django.jQuery;
    $('#id_cpf').mask('000.000.000-00', {reverse: true});
    $('#id_cnpj').mask('00.000.000/0000-00', {reverse: true});
    $('#id_cep').mask('00000-000');
    var phoneMaskBehavior = function (val) { return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009'; };
    var phoneOptions = { onKeyPress: function(val, e, field, options) { field.mask(phoneMaskBehavior.apply({}, arguments), options); } };
    $('#id_celular').mask(phoneMaskBehavior, phoneOptions);
    $('#id_telefone_fixo').mask(phoneMaskBehavior, phoneOptions);

    $('#id_tipo_chave_pix').on('change', function() {
        const tipo = $(this).val();
        let valor = '';
        if (tipo === 'CPF') valor = $('#id_cpf').val();
        else if (tipo === 'CNPJ') valor = $('#id_cnpj').val();
        else if (tipo === 'EMAIL') valor = $('#id_email').val();
        else if (tipo === 'CEL') valor = $('#id_celular').val();
        $('#id_chave_pix').val(valor);
    });
});