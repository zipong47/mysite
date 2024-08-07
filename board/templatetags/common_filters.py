from django import template

register = template.Library()

@register.filter(name="divide")
def divide(value, arg):
    try:
        # Calculate the division and convert to a percentage
        rate = (int(value) / int(arg)) * 100
        # Format the rate as a percentage string with one decimal place
        rate = "{:.1f}%".format(rate)
        return rate
    except (ValueError, ZeroDivisionError):
        return None