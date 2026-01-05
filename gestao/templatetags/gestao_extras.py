from django import template
from django.utils.html import format_html
from datetime import date

register = template.Library()

# --- FILTRO 1: Retorna o HTML completo (usado se quiser exibir texto fixo) ---
@register.filter
def formatar_prazo_entrega(pedido):
    if not pedido.data_entrega:
        return "-"
    data_fmt = pedido.data_entrega.strftime('%d/%m/%Y')
    if pedido.status in ['F', 'C']:
        return data_fmt

    hoje = date.today()
    dias_restantes = (pedido.data_entrega - hoje).days

    cor = 'black'
    peso = 'normal'
    icone = ''
    
    if dias_restantes > 15:
        cor = '#198754' # Verde
    elif 3 <= dias_restantes <= 15:
        cor = '#fd7e14' # Laranja
        peso = 'bold'
    elif dias_restantes >= 0:
        cor = '#dc3545' # Vermelho
        peso = 'bold'
    else:
        cor = '#8B0000' # Vinho
        peso = 'bold'
        icone = ' (!)'

    return format_html(
        '<span style="color: {}; font-weight: {}; white-space: nowrap;">{}{}</span>',
        cor, peso, data_fmt, format_html(icone)
    )

# --- FILTRO 2 (NOVO): Retorna SÓ A COR para usar no Input ---
@register.filter
def get_cor_urgencia(pedido):
    """Retorna o código Hex da cor baseado na urgência"""
    # Se não tem data ou já está finalizado, retorna cor padrão (cinza escuro/preto)
    if not pedido.data_entrega or pedido.status in ['F', 'C']:
        return '#212529' 

    hoje = date.today()
    dias_restantes = (pedido.data_entrega - hoje).days

    if dias_restantes > 15:
        return '#198754' # Verde
    elif 3 <= dias_restantes <= 15:
        return '#fd7e14' # Laranja
    elif dias_restantes >= 0:
        return '#dc3545' # Vermelho
    else:
        return '#8B0000' # Vinho (Atrasado)