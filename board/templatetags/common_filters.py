from django import template

register = template.Library()

@register.filter(name="divide")
def divide(value, arg):
    try:
        rate=int(value) / int(arg)
        rate="{:.1f}%".format(rate)
        return rate
    except (ValueError, ZeroDivisionError):
        return None