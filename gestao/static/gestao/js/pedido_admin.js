// Arquivo: gestao/js/pedido_admin.js (Versão 8.0 - Atualiza Preços ao Mudar Tabela)

window.addEventListener('load', function() {
    
    const $ = django.jQuery;
    console.log("--- SCRIPT DE PEDIDOS PRONTO (VERSÃO 8.0 - Atualiza Preços Tabela) ---");

    // --- LÓGICA DA PÁGINA DE LISTA (CHANGELIST) ---
    if ($('body').hasClass('change-list')) {
        console.log("JS: Modo Lista (change-list) ativado.");
        const $topActionsBar = $('div.actions').first();
        const $bottomSaveButton = $('input[name="_save"]').last();
        console.log("JS: Barra do topo encontrada:", $topActionsBar.length);
        console.log("JS: Botão Salvar do rodapé encontrado:", $bottomSaveButton.length);
        if ($bottomSaveButton.length > 0 && $topActionsBar.length > 0) {
            console.log("JS: Clonando e movendo o botão...");
            const $clonedButton = $bottomSaveButton.clone();
            $clonedButton.css('margin-left', '10px'); 
            $clonedButton.appendTo($topActionsBar);
            console.log("JS: Botão clonado com sucesso!");
        }
    }

    // --- LÓGICA DA PÁGINA DE EDIÇÃO/CRIAÇÃO (CHANGEFORM) ---
    else if ($('body').hasClass('change-form')) {
        console.log("JS: Modo Formulário (change-form) ativado.");

        // Limpa os campos de valor ao focar
        $('input[id="id_valor_desconto"], input[id="id_taxa_entrega"]').one('focus', function() {
            const $this = $(this);
            // Usa parseFloat com replace para tratar vírgula decimal, se houver
            if (parseFloat(($this.val() || '0').replace(',', '.')) === 0) {
                $this.val('');
            }
        });


        // --- FUNÇÃO MESTRA DE CÁLCULO (sem alteração) ---
        function updateAllCalculations() {
            let subtotalGeral = 0;
            $('.dynamic-itens:not(.deleted)').each(function() {
                const $row = $(this);
                const quantidadeInput = $row.find('input[id*="-quantidade"]');
                const precoUnitarioInput = $row.find('input[id*="-preco_unitario"]');
                const subtotalInput = $row.find('input[id*="-subtotal"]');
                const quantidadeVal = quantidadeInput.val() || '0';
                const precoUnitarioVal = precoUnitarioInput.val() || '0';
                const quantidade = parseFloat(quantidadeVal.replace(',', '.')) || 0;
                const precoUnitario = parseFloat(precoUnitarioVal.replace(',', '.')) || 0;
                const subtotal = quantidade * precoUnitario;
                subtotalInput.val(subtotal.toFixed(2));
                subtotalGeral += subtotal;
            });
            const tipoDesconto = $('#id_tipo_desconto').val();
            const valorDescontoVal = $('#id_valor_desconto').val() || '0';
            const valorDesconto = parseFloat(valorDescontoVal.replace(',', '.')) || 0;
            let descontoAplicado = 0;
            if (tipoDesconto === 'P') { descontoAplicado = (subtotalGeral * valorDesconto) / 100; } 
            else if (tipoDesconto === 'V') { descontoAplicado = valorDesconto; }
            const taxaEntregaVal = $('#id_taxa_entrega').val() || '0';
            const taxaEntrega = parseFloat(taxaEntregaVal.replace(',', '.')) || 0;
            const finalTotal = subtotalGeral - descontoAplicado + taxaEntrega;
            $('input[id="id_valor_total"]').val(finalTotal.toFixed(2));
        }


        // --- FUNÇÃO AUXILIAR PARA BUSCAR PREÇO (reutilizável) ---
        function fetchAndUpdatePrice($row, tabelaId) {
            const itemSelect = $row.find('select[id*="-item"]');
            const precoUnitarioInput = $row.find('input[id*="-preco_unitario"]');
            const itemId = itemSelect.val();

            if (itemId && tabelaId) {
                console.log(`JS: Buscando preço para item ${itemId} na tabela ${tabelaId}`);
                $.ajax({
                    url: `/gestao/api/get-item-price/?item_id=${itemId}&tabela_id=${tabelaId}`,
                    success: function(data) {
                        precoUnitarioInput.val(data.price);
                        console.log(`JS: Preço atualizado para ${data.price}`);
                        // Não precisa chamar updateAllCalculations aqui, o interval faz isso
                    },
                    error: function() {
                        console.error(`JS: Erro ao buscar preço para item ${itemId}`);
                        // Opcional: Limpar o preço ou mostrar erro
                        // precoUnitarioInput.val('0.00'); 
                    }
                });
            } else {
                // Se não houver item selecionado na linha, limpa o preço
                // precoUnitarioInput.val('0.00');
                 console.log("JS: Item ou Tabela não selecionados na linha, preço não buscado.");
            }
        }


        // --- "ESPIÃO" DE BUSCA DE PREÇO (AO SELECIONAR ITEM) ---
        // Agora usa a função auxiliar
        $(document.body).on('select2:select', 'select[id*="-item"]', function(e) {
            const $row = $(this).closest('.dynamic-itens');
            const tabelaPrecoId = $('#id_tabela_de_preco').val();
            
            if (!tabelaPrecoId) {
                alert("Por favor, selecione uma Tabela de Preço no cabeçalho antes de adicionar itens.");
                $(this).val(null).trigger('change'); // Limpa a seleção do item
                return;
            }
            fetchAndUpdatePrice($row, tabelaPrecoId);
        });


        // --- **** NOVA LÓGICA **** ---
        // --- "ESPIÃO" DE MUDANÇA DA TABELA DE PREÇO ---
        $('#id_tabela_de_preco').on('change', function() {
            const novaTabelaId = $(this).val();
            console.log(`JS: Tabela de Preço alterada para ID: ${novaTabelaId}`);

            if (!novaTabelaId) {
                console.warn("JS: Nenhuma tabela de preço selecionada. Preços não serão atualizados.");
                // Opcional: Poderíamos limpar todos os preços unitários aqui?
                // $('.dynamic-itens:not(.deleted) input[id*="-preco_unitario"]').val('0.00');
                return; 
            }

            // Itera sobre todas as linhas de itens existentes (não deletadas)
            $('.dynamic-itens:not(.deleted)').each(function() {
                const $row = $(this);
                fetchAndUpdatePrice($row, novaTabelaId); // Usa a função auxiliar
            });
        });
        // --- FIM DA NOVA LÓGICA ---


        // --- O ROBÔ FISCAL (sem alteração) ---
        setInterval(updateAllCalculations, 250);
    }

});