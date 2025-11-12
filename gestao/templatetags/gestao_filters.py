from django import template
import re

register = template.Library()

@register.filter
def formatar_cpf(value):
    if not value: return ""
    # Garante que só temos números
    value = re.sub(r'\D', '', str(value))
    if len(value) != 11: return value
    return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"

@register.filter
def formatar_cnpj(value):
    if not value: return ""
    # Garante que só temos números
    value = re.sub(r'\D', '', str(value))
    if len(value) != 14: return value
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"

@register.filter
def formatar_telefone(value):
    if not value: return ""
    # Garante que só temos números
    value = re.sub(r'\D', '', str(value))
    if len(value) == 11:
        return f"({value[:2]}) {value[2:7]}-{value[7:]}"
    elif len(value) == 10:
        return f"({value[:2]}) {value[2:6]}-{value[6:]}"
    else:
        return value