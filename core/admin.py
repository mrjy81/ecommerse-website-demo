from django.contrib import admin
from .models import Item, Order, OrderItem, CheckoutModel, FeedbackModel

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(FeedbackModel)
admin.site.register(CheckoutModel)
