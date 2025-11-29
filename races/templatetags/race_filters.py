from django import template

register = template.Library()

@register.filter
def format_seconds(value, show_decimal=True):
    """
    Format seconds:
    - show_decimal=True: MM:SS.hh if >= 60s, otherwise SS.hh (two decimals)
    - show_decimal=False: whole seconds (for penalties)
    """
    try:
        total_seconds = float(value)
    except (TypeError, ValueError):
        return "--"

    if show_decimal:
        if total_seconds >= 60:
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:05.2f}"  # MM:SS.hh
        else:
            return f"{total_seconds:05.2f}"           # SS.hh
    else:
        return str(int(round(total_seconds)))        # whole seconds
