from django import template
from core.models import Order


register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        order = Order.objects.filter(user=user, ordered=False).first()
        if order:
            qty = order.items.all()
            return sum([i.quantity for i in qty])
        else:
            return 0
    else:
        return 0
