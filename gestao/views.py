from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Pedido, Empresa, Item, PrecoItem, RegraDePreco, ItemPedido
import qrcode
import base64
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
import re
from unicodedata import normalize
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.contrib import messages
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import date
import os  # <--- Adicionado para manipular caminhos de arquivo

def home(request):
    return HttpResponse("Sistema Funcionando!")

def sanitize_pix_field(text, max_length, remove_spaces=False):
    if not text:
        return ""
    s = normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    if remove_spaces:
        s = re.sub(r'[^A-Z0-9]', '', s.upper())
    else:
        s = re.sub(r'[^A-Z0-9 ]', '', s.upper())
    return s[:max_length].strip()

def get_item_price(request):
    item_id = request.GET.get('item_id')
    tabela_id = request.GET.get('tabela_id')
    preco_final = Decimal('0.00')
    if item_id and tabela_id:
        try:
            item = Item.objects.get(pk=item_id)
            preco_especifico = PrecoItem.objects.filter(item=item, tabela_de_preco_id=tabela_id).first()
            if preco_especifico:
                preco_final = preco_especifico.valor
            elif item.grupo and item.tamanho:
                regra_grupo = RegraDePreco.objects.filter(grupo=item.grupo, tamanho=item.tamanho, tabela_de_preco_id=tabela_id).first()
                if regra_grupo:
                    preco_final = regra_grupo.valor
        except Item.DoesNotExist:
            pass
    return JsonResponse({'price': f'{preco_final:.2f}'})

def _build_pix_string(empresa, pedido):
    nome_beneficiario = sanitize_pix_field(
        empresa.nome_beneficiario_pix or empresa.razao_social,
        25,
        remove_spaces=False
    )
    cidade_beneficiario = sanitize_pix_field(empresa.cidade or 'FORTALEZA', 15, remove_spaces=True)

    chave_pix_sanitizada = ""
    if empresa.tipo_chave_pix == 'EMAIL':
        chave_pix_sanitizada = empresa.chave_pix.strip().lower()
    elif empresa.tipo_chave_pix == 'CEL':
        numeros_cel = re.sub(r'[^\d+]', '', empresa.chave_pix)
        if numeros_cel.startswith('55'):
            chave_pix_sanitizada = f"+{numeros_cel}"
        elif not numeros_cel.startswith('+55'):
            chave_pix_sanitizada = f"+55{numeros_cel.lstrip('0')}"
        else:
            chave_pix_sanitizada = numeros_cel
    else:
        chave_pix_sanitizada = sanitize_pix_field(empresa.chave_pix, 77, remove_spaces=True)

    payload = [
        f"000201", f"010211",
        f"26{len(f'0014br.gov.bcb.pix01{len(chave_pix_sanitizada):02d}{chave_pix_sanitizada}'):02d}0014br.gov.bcb.pix01{len(chave_pix_sanitizada):02d}{chave_pix_sanitizada}",
        f"52040000", f"5303986",
    ]
    if pedido.valor_total > 0:
        valor_str = f"{pedido.valor_total:.2f}"
        payload.append(f"54{len(valor_str):02d}{valor_str}")
    payload.extend([
        f"5802BR", f"59{len(nome_beneficiario):02d}{nome_beneficiario}",
        f"60{len(cidade_beneficiario):02d}{cidade_beneficiario}",
    ])
    txid = "***"
    payload.append(f"62{len(f'05{len(txid):02d}{txid}'):02d}05{len(txid):02d}{txid}")
    payload_string = "".join(payload) + "6304"
    def crc16_ccitt_false(data: str) -> str:
        crc = 0xFFFF
        for byte in data.encode('ascii'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000: crc = (crc << 1) ^ 0x1021
                else: crc <<= 1
        return f"{crc & 0xFFFF:04X}"
    crc = crc16_ccitt_false(payload_string)
    return payload_string + crc

def gerar_pix_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    empresa = Empresa.objects.first()
    if empresa and empresa.chave_pix:
        pix_copia_e_cola = _build_pix_string(empresa, pedido)
        qr_img = qrcode.make(pix_copia_e_cola)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qrcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        context = {'pedido': pedido, 'pix_copia_e_cola': pix_copia_e_cola, 'qrcode_base64': qrcode_base64}
    else:
        context = {'erro': 'Empresa ou Chave PIX não configurada.'}
    return render(request, 'gestao/gerar_pix.html', context)

def imprimir_pedido_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    empresa = Empresa.objects.first()
    itens_pedido = pedido.itens.all()
    qrcode_base64 = None
    
    # Lógica do QR Code PIX
    if pedido.forma_pagamento == 'PIX' and not pedido.pago:
        if empresa and empresa.chave_pix:
            pix_copia_e_cola = _build_pix_string(empresa, pedido)
            qr_img = qrcode.make(pix_copia_e_cola)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qrcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # --- NOVO: Lógica para carregar o Logo como Base64 (Evita erro de memória no Render) ---
    logo_base64 = None
    if empresa and empresa.logo:
        try:
            # Tenta pegar o caminho físico do arquivo
            path = empresa.logo.path
            with open(path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            # Se der erro (ex: arquivo não existe localmente), segue sem logo ou usa URL
            print(f"Erro ao converter logo para base64: {e}")
    # ---------------------------------------------------------------------------------------

    context = {
        'pedido': pedido, 
        'empresa': empresa, 
        'itens_pedido': itens_pedido, 
        'qrcode_base64': qrcode_base64,
        'logo_base64': logo_base64  # <--- Enviando a nova variável para o HTML
    }
    
    html_string = render_to_string('gestao/pedido_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    return response

@staff_member_required
def clonar_pedido(request, pedido_id):
    pedido_original = get_object_or_404(Pedido, pk=pedido_id)
    novo_pedido = Pedido()

    novo_pedido.cliente = pedido_original.cliente
    novo_pedido.tabela_de_preco = pedido_original.tabela_de_preco
    novo_pedido.forma_pagamento = pedido_original.forma_pagamento
    novo_pedido.tipo_desconto = pedido_original.tipo_desconto
    novo_pedido.valor_desconto = pedido_original.valor_desconto
    novo_pedido.taxa_entrega = pedido_original.taxa_entrega

    user_empresa = getattr(request.user, 'empresa', None)
    novo_pedido.empresa = user_empresa or pedido_original.empresa

    novo_pedido.save()

    itens_clonados = []
    for item_original in pedido_original.itens.all():
        subtotal_calculado = (item_original.quantidade * item_original.preco_unitario).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        novo_item = ItemPedido(
            pedido=novo_pedido,
            item=item_original.item,
            quantidade=item_original.quantidade,
            preco_unitario=item_original.preco_unitario,
            subtotal=subtotal_calculado,  
            empresa=novo_pedido.empresa
        )
        itens_clonados.append(novo_item)

    if itens_clonados:
        ItemPedido.objects.bulk_create(itens_clonados)
        novo_pedido.save()

    messages.success(request, f"Pedido Nº {pedido_original.numero_pedido} clonado com sucesso. Editando o novo Pedido Nº {novo_pedido.numero_pedido}.")
    url_edicao = reverse('admin:gestao_pedido_change', args=[novo_pedido.id])
    return redirect(url_edicao)

@staff_member_required
def relatorio_vendas_periodo(request):
    context = {
        'total_vendas': None,
        'data_inicio': None,
        'data_fim': None,
        'pedidos_periodo': None,
    }
    user_empresa = getattr(request.user, 'empresa', None)

    if request.method == 'POST' and user_empresa:
        data_inicio_str = request.POST.get('data_inicio')
        data_fim_str = request.POST.get('data_fim')

        data_inicio = parse_date(data_inicio_str)
        data_fim = parse_date(data_fim_str)

        if data_inicio and data_fim:
            from datetime import timedelta
            data_fim_consulta = data_fim + timedelta(days=1)
            
            pedidos_periodo = Pedido.objects.filter(
                empresa=user_empresa,
                data_emissao__gte=data_inicio, 
                data_emissao__lt=data_fim_consulta, 
                status='F' 
            ).order_by('data_emissao')

            resultado = pedidos_periodo.aggregate(total=Sum('valor_total'))
            total_vendas = resultado['total'] or 0 

            context['total_vendas'] = total_vendas
            context['data_inicio'] = data_inicio
            context['data_fim'] = data_fim
            context['pedidos_periodo'] = pedidos_periodo
        else:
            messages.error(request, "Datas inválidas. Por favor, use o formato AAAA-MM-DD.")
    return render(request, 'gestao/relatorio_vendas.html', context)