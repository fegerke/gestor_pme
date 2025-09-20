from django.http import JsonResponse
from .models import Item, PrecoItem, RegraDePreco
from decimal import Decimal # <-- ADICIONE ESTA LINHA

def get_item_price(request):
    item_id = request.GET.get('item_id')
    tabela_id = request.GET.get('tabela_id')
    preco_final = Decimal('0.00')

    if item_id and tabela_id:
        try:
            item = Item.objects.get(pk=item_id)
            
            # 1. Busca preço específico
            preco_especifico = PrecoItem.objects.filter(item=item, tabela_de_preco_id=tabela_id).first()
            
            if preco_especifico:
                preco_final = preco_especifico.valor
            # 2. Se não achar, busca regra de grupo
            elif item.grupo and item.tamanho:
                regra_grupo = RegraDePreco.objects.filter(
                    grupo=item.grupo,
                    tamanho=item.tamanho,
                    tabela_de_preco_id=tabela_id
                ).first()
                if regra_grupo:
                    preco_final = regra_grupo.valor
        except Item.DoesNotExist:
            pass # Se o item não existir, o preço continua 0.00
    
    # Retorna o preço formatado com 2 casas decimais
    return JsonResponse({'price': f'{preco_final:.2f}'})