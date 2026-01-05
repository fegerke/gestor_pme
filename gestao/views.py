from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Pedido, Empresa, Item, PrecoItem, RegraDePreco, ItemPedido, Contato, TabelaDePreco
import qrcode
import base64
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
import re
from unicodedata import normalize
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q, Case, When, F
from django.utils.dateparse import parse_date
from datetime import date
import os
from django.contrib.staticfiles import finders
import json
from django.db import transaction
from .forms import PedidoForm, ItemPedidoFormSet

def home(request):
    return HttpResponse("Sistema Funcionando!")

# --- DASHBOARD ---
@login_required
def dashboard(request):
    hoje = date.today()
    vendas_mes = Pedido.objects.filter(
        status='F',
        data_emissao__year=hoje.year,
        data_emissao__month=hoje.month
    ).aggregate(total=Sum('valor_total'))['total'] or 0

    pedidos_pendentes = Pedido.objects.filter(status='A').count()
    
    clientes_ativos = Contato.objects.filter(
        eh_cliente=True,
        situacao='Ativo'
    ).count()

    ticket_medio = Pedido.objects.filter(status='F').aggregate(media=Avg('valor_total'))['media'] or 0

    ultimos_pedidos = Pedido.objects.select_related('cliente').order_by('-data_emissao')[:10]

    context = {
        'total_vendas_mes': vendas_mes,
        'pedidos_pendentes': pedidos_pendentes,
        'clientes_ativos': clientes_ativos,
        'ticket_medio': ticket_medio,
        'ultimos_pedidos': ultimos_pedidos,
    }

    return render(request, 'gestao/dashboard.html', context)

# --- LISTA DE PEDIDOS AVANÇADA ---
@login_required
def lista_pedidos(request):
    # Lógica de Ordenação Inteligente
    ordem_abertos = Case(
        When(status='A', then=F('data_entrega')),
        default=None
    ).asc(nulls_last=True)

    ordem_outros = Case(
        When(status='A', then=None),
        default=F('data_entrega')
    ).desc(nulls_last=True)

    pedidos = Pedido.objects.select_related('cliente').prefetch_related('itens__item').order_by(
        'status',
        ordem_abertos,
        ordem_outros,
        '-numero_pedido'
    )
    
    # Filtros
    query = request.GET.get('q')
    if query:
        pedidos = pedidos.filter(
            Q(cliente__nome_razao_social__icontains=query) |
            Q(cliente__apelido__icontains=query) |
            Q(numero_pedido__icontains=query)
        )

    status_filter = request.GET.get('status')
    if status_filter:
        pedidos = pedidos.filter(status=status_filter)

    context = {
        'pedidos': pedidos,
        'status_filter': status_filter,
    }
    return render(request, 'gestao/lista_pedidos.html', context)

# --- FUNÇÕES AUXILIARES DE PIX E PREÇO ---
def sanitize_pix_field(text, max_length, remove_spaces=False):
    if not text: return ""
    s = normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    s = re.sub(r'[^A-Z0-9 ]', '', s.upper()) if not remove_spaces else re.sub(r'[^A-Z0-9]', '', s.upper())
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
    nome_beneficiario = sanitize_pix_field(empresa.nome_beneficiario_pix or empresa.razao_social, 25)
    cidade_beneficiario = sanitize_pix_field(empresa.cidade or 'FORTALEZA', 15, remove_spaces=True)
    
    chave_pix_sanitizada = ""
    if empresa.tipo_chave_pix == 'EMAIL':
        chave_pix_sanitizada = empresa.chave_pix.strip().lower()
    elif empresa.tipo_chave_pix == 'CEL':
        numeros_cel = re.sub(r'[^\d+]', '', empresa.chave_pix)
        if numeros_cel.startswith('55'): chave_pix_sanitizada = f"+{numeros_cel}"
        elif not numeros_cel.startswith('+55'): chave_pix_sanitizada = f"+55{numeros_cel.lstrip('0')}"
        else: chave_pix_sanitizada = numeros_cel
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

def get_static_base64(path):
    try:
        abs_path = finders.find(path)
        if abs_path:
            with open(abs_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Erro ao carregar estatico {path}: {e}")
    return None

def imprimir_pedido_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    empresa = Empresa.objects.first()
    itens_pedido = pedido.itens.all()
    qrcode_base64 = None
    
    if pedido.forma_pagamento == 'PIX' and not pedido.pago:
        if empresa and empresa.chave_pix:
            pix_copia_e_cola = _build_pix_string(empresa, pedido)
            qr_img = qrcode.make(pix_copia_e_cola)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qrcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    logo_base64 = None
    if empresa and empresa.logo:
        try:
            path = empresa.logo.path
            with open(path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Erro ao converter logo para base64: {e}")

    whatsapp_b64 = get_static_base64('gestao/img/whatsapp.svg')
    instagram_b64 = get_static_base64('gestao/img/instagram.svg')

    context = {
        'pedido': pedido, 
        'empresa': empresa, 
        'itens_pedido': itens_pedido, 
        'qrcode_base64': qrcode_base64,
        'logo_base64': logo_base64,
        'whatsapp_b64': whatsapp_b64,
        'instagram_b64': instagram_b64
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
    context = {'total_vendas': None, 'data_inicio': None, 'data_fim': None, 'pedidos_periodo': None}
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
            context['total_vendas'] = resultado['total'] or 0 
            context['data_inicio'] = data_inicio
            context['data_fim'] = data_fim
            context['pedidos_periodo'] = pedidos_periodo
        else:
            messages.error(request, "Datas inválidas. Por favor, use o formato AAAA-MM-DD.")
    return render(request, 'gestao/relatorio_vendas.html', context)

# --- NOVIDADES: APIs PARA A LISTA INTERATIVA ---

# Função Auxiliar de Cores (Cérebro do Semáforo)
def calcular_urgencia(pedido):
    """Retorna cor, peso da fonte e se deve mostrar alerta"""
    if not pedido.data_entrega or pedido.status in ['F', 'C']:
        return '#212529', 'normal', False # Preto Padrão
    
    hoje = date.today()
    dias_restantes = (pedido.data_entrega - hoje).days

    if dias_restantes > 15:
        return '#198754', 'normal', False # Verde
    elif 3 <= dias_restantes <= 15:
        return '#fd7e14', 'bold', False # Laranja
    elif dias_restantes >= 0:
        return '#dc3545', 'bold', False # Vermelho
    else:
        return '#8B0000', 'bold', True # Vinho + Alerta

@login_required
@require_POST
def alterar_status_pedido(request, pedido_id):
    try:
        data = json.loads(request.body)
        novo_status = data.get('status')
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        
        pedido.status = novo_status
        pedido.save()
        
        cor, peso, mostrar_alerta = calcular_urgencia(pedido)
        
        return JsonResponse({
            'success': True, 
            'novo_status': pedido.get_status_display(),
            'cor': cor,
            'peso': peso,
            'mostrar_alerta': mostrar_alerta
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def alterar_data_entrega(request, pedido_id):
    try:
        data = json.loads(request.body)
        nova_data = data.get('data_entrega') # Formato YYYY-MM-DD
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        
        if nova_data:
            pedido.data_entrega = parse_date(nova_data)
        else:
            pedido.data_entrega = None
            
        pedido.save()
        
        cor, peso, mostrar_alerta = calcular_urgencia(pedido)
        
        return JsonResponse({
            'success': True,
            'cor': cor,
            'peso': peso,
            'mostrar_alerta': mostrar_alerta
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def toggle_pago_pedido(request, pedido_id):
    try:
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        pedido.pago = not pedido.pago
        pedido.save()
        return JsonResponse({'success': True, 'pago': pedido.pago})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def acao_em_massa(request):
    ids_selecionados = request.POST.getlist('selected_pedidos')
    acao = request.POST.get('acao')
    
    if ids_selecionados and acao == 'delete':
        qtde, _ = Pedido.objects.filter(id__in=ids_selecionados).delete()
        messages.success(request, f"{qtde} pedido(s) apagado(s) com sucesso!")
        
    return redirect('gestao:lista_pedidos')

@login_required
def pedido_novo(request):
    return _salvar_pedido(request, None)

@login_required
def pedido_editar(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    return _salvar_pedido(request, pedido)

def _salvar_pedido(request, pedido):
    """Função interna para lidar tanto com criar quanto editar"""
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        formset = ItemPedidoFormSet(request.POST, instance=pedido)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic(): # Garante que só salva se tudo estiver OK
                pedido_salvo = form.save(commit=False)
                
                # Garante a empresa se for novo
                if not pedido_salvo.pk:
                    user_empresa = getattr(request.user, 'empresa', None)
                    pedido_salvo.empresa = user_empresa
                
                pedido_salvo.save() # Salva o Mestre para ter um ID
                
                # Salva os Itens
                formset.instance = pedido_salvo
                itens = formset.save(commit=False)
                
                user_empresa = getattr(request.user, 'empresa', None)
                for item in itens:
                    if not item.pk and user_empresa:
                        item.empresa = user_empresa
                    item.save()
                
                # Deleta os removidos
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Recalcula totais finais (chama o save do model novamente)
                pedido_salvo.save()
                
            messages.success(request, f"Pedido Nº {pedido_salvo.numero_pedido} salvo com sucesso!")
            return redirect('gestao:lista_pedidos')
        else:
            messages.error(request, "Erro ao salvar. Verifique os campos abaixo.")
    else:
        form = PedidoForm(instance=pedido)
        formset = ItemPedidoFormSet(instance=pedido)
        
        # Se for novo, define valores padrão
        if not pedido:
            # Padrão: Data de Entrega = Hoje
            form.initial['data_entrega'] = date.today() # <--- ADICIONE ISSO
            
            user_empresa = getattr(request.user, 'empresa', None)
            tabela_padrao = TabelaDePreco.objects.filter(empresa=user_empresa).first()
            if tabela_padrao:
                form.initial['tabela_de_preco'] = tabela_padrao

    context = {
        'form': form,
        'formset': formset,
        'titulo': f"Editar Pedido {pedido.numero_pedido}" if pedido else "Novo Pedido"
    }
    return render(request, 'gestao/pedido_form.html', context)

