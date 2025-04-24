from decimal import Decimal


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
