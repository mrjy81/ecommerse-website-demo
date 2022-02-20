from django.urls import path
from .views import (add_to_cart,
                    delete_from_cart,
                    cartView, decrease_item,
                    increase_item, remove_all_item,
                    checkout_view,
                    feedback,
                    ItemDetailView,
                    Home,
                    go_to_gateway_view,
                    callback_gateway_view,
                    )
app_name = 'core'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('product/<slug>', ItemDetailView, name='detail'),
    path('add-to-cart/<slug>', add_to_cart, name='add_to_cart'),
    path('delete-from-cart/<slug>', delete_from_cart, name='delete_from_cart'),
    path('cart-summary', cartView, name='cart-summary'),
    path('decrease/<slug>', decrease_item, name='decrease'),
    path('increase/<slug>', increase_item, name='increase'),
    path('delete-all/<slug>', remove_all_item, name='delete-all'),
    path('checkout', checkout_view, name='checkout'),
    path('feedback/<slug>', feedback, name='feedback'),
    path('go_to_gateway_view', go_to_gateway_view, name='go_to_gateway_view'),
    path('callback_gateway_view', callback_gateway_view,
         name='callback-gateway'),










]
