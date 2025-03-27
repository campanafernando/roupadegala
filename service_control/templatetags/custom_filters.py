import locale

from django import template

register = template.Library()

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")  # Define locale para BR


@register.filter
def brl_format(value):
    try:
        return locale.currency(value, grouping=True, symbol=True)
    except (ValueError, TypeError):
        return value


@register.filter
def format_brl(value, decimal_places=2):
    """
    Formata um número no estilo brasileiro, com casas decimais e separador de milhar.
    :param value: O valor que será formatado
    :param decimal_places: Número de casas decimais (padrão 2)
    :return: String formatada
    """
    try:
        value = float(value)
        formatted_value = f"{value:,.{decimal_places}f}"
        return formatted_value.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value


@register.filter
def format_cpf_cnpj(value):
    """
    Aplica máscara ao CPF ou CNPJ.
    - CPF: 000.000.000-00
    - CNPJ: 00.000.000/0000-00
    :param value: O valor que será formatado (string ou número)
    :return: String formatada com a máscara de CPF ou CNPJ
    """
    try:
        value = str(value)

        if len(value) == 11:
            return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
        elif len(value) == 14:
            return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"
        else:
            return value
    except (ValueError, TypeError):
        return value
