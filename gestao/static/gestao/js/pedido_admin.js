window.addEventListener('load', function() {

    const $ = django.jQuery;
    let itemRowCount = 0;

    function updateAll() {
        let grandTotal = 0;
        const currentRows = $('.dynamic-itens').length;

        if (currentRows !== itemRowCount || currentRows > 0) {
            $('.dynamic-itens').each(function() {
                const $row = $(this);
                const deleteCheckbox = $row.find('input[id*="-DELETE"]');
                const quantidadeInput = $row.find('input[id*="-quantidade"]');
                const precoUnitarioInput = $row.find('input[id*="-preco_unitario"]');
                const subtotalInput = $row.find('input[id*="-subtotal"]');

                const quantidade = parseFloat(quantidadeInput.val().replace(',', '.')) || 0;
                const precoUnitario = parseFloat(precoUnitarioInput.val().replace(',', '.')) || 0;
                const subtotal = quantidade * precoUnitario;
                subtotalInput.val(subtotal.toFixed(2));

                if (!deleteCheckbox.prop('checked')) {
                    grandTotal += subtotal;
                }
            });

            $('input[id="id_valor_total"]').val(grandTotal.toFixed(2));
            itemRowCount = currentRows;
        }
    }

    // --- LÓGICA DE BUSCA DE PREÇO ---
    $(document.body).on('select2:select', 'select[id*="-item"]', function(e) {
        const $row = $(this).closest('.dynamic-itens');
        const precoUnitarioInput = $row.find('input[id*="-preco_unitario"]');
        const itemId = $(this).val();
        const tabelaPrecoId = $('#id_tabela_de_preco').val();

        if (!tabelaPrecoId) {
            alert("Por favor, selecione uma Tabela de Preço no cabeçalho antes de adicionar itens.");
            $(this).val(null).trigger('change');
            return;
        }
        if (itemId) {
            $.ajax({
                url: `/gestao/api/get-item-price/?item_id=${itemId}&tabela_id=${tabelaPrecoId}`,
                success: function(data) {
                    precoUnitarioInput.val(data.price);
                }
            });
        }
    });

    // --- O ROBÔ FISCAL ---
    setInterval(updateAll, 250);

});