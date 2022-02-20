from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Item, OrderItem, Order, CheckoutModel, FeedbackModel
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .form import CheckoutForm, FeedbackForm
import logging
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException


def go_to_gateway_view(request):
    person = Order.objects.filter(user=request.user, ordered=False).first()
    if person:
        total_price = person.get_total_price()
    else:
        messages.info('you have not active account')
        return redirect('core:home')
    # خواندن مبلغ از هر جایی که مد نظر است
    amount = total_price
    # تنظیم شماره موبایل کاربر از هر جایی که مد نظر است
    user_mobile_number = '+989112221234'  # اختیاری

    factory = bankfactories.BankFactory()
    try:
        bank = factory.create()  # or factory.create(bank_models.BankType.BMI) or set identifier
        bank.set_request(request)
        bank.set_amount(amount)
        # یو آر ال بازگشت به نرم افزار برای ادامه فرآیند
        bank.set_client_callback_url(reverse('core:callback-gateway'))
        bank.set_mobile_number(user_mobile_number)  # اختیاری

        # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
        # پرداخت برقرار کنید.
        bank_record = bank.ready()

        # هدایت کاربر به درگاه بانک
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        # TODO: redirect to failed page.
        raise e


def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
    if bank_record.is_success:
        person = Order.objects.filter(user=request.user, ordered=False).first()
        person.ordered = True
        person.save()

        # پرداخت با موفقیت انجام پذیرفته است و بانک تایید کرده است.
        # می توانید کاربر را به صفحه نتیجه هدایت کنید یا نتیجه را نمایش دهید.
        messages.success(request, 'your ordered has successfully pharchuse')
        return redirect('core:home')

    # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
    return HttpResponse("پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")


class Home(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'
    context_object_name = 'items'


def ItemDetailView(request, slug):
    obj = get_object_or_404(Item, slug=slug)
    feedback = FeedbackModel.objects.filter(feedback_for__slug=slug)
    form = FeedbackForm()
    context = {
        'fb': feedback,
        'form': form,
        'item': obj,
    }
    return render(request, "product-page.html", context)


@login_required
def cartView(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
    except:
        messages.info(request, 'you have no active order')
        return redirect('/')
    context = {
        'order': order,
    }
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if order:
        if order.items.filter(item__slug=item.slug).exists():  # more than one products
            order_item.quantity += 1
            order_item.save()
            messages.info(
                request, f'one more {item.title} added to your cart wow!')
        else:
            order.items.add(order_item)  # add that to m2m
            messages.info(
                request, f'{item.title} successfully added to your cart wow!')

    else:   # if cart isn't created yet
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(
            request, 'wow your cart isn\'nt empty anymore')

    return redirect('core:detail', slug=slug)


@login_required
def delete_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()
    order_item = OrderItem.objects.filter(
        user=request.user, ordered=False, item=item).first()
    if order:
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(
                    request, f'{item.title} successfully removed from your cart')
            else:
                order_item.delete()
                messages.info(
                    request, f' you have no longer {item.title} in your cart')

        else:
            messages.info(
                request, f'{item.title} is not added to your cart yet')
    else:
        messages.info(
            request, f'you have no active order')

    return redirect('core:detail', slug=slug)


@login_required
def decrease_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()
    order_item = OrderItem.objects.filter(
        user=request.user, ordered=False, item=item).first()

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    return redirect('core:cart-summary')


@login_required
def increase_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()
    order_item = OrderItem.objects.filter(
        user=request.user, ordered=False, item=item).first()
    order_item.quantity += 1
    order_item.save()
    return redirect('core:cart-summary')


@login_required
def remove_all_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()
    order_item = OrderItem.objects.filter(
        user=request.user, ordered=False, item=item).first()
    order_item.delete()
    return redirect('core:cart-summary')


@login_required
def checkout_view(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if order:
        form = CheckoutForm()
        if request.method == 'POST':
            form = CheckoutForm(request.POST or None)
            if form.is_valid():
                address = form.cleaned_data['address']
                zip = form.cleaned_data['zip']
                phone = form.cleaned_data['phone_number']
                check = CheckoutModel.objects.get_or_create(
                    user=request.user, zip=zip, phone_number=phone, address=address)

                return redirect('core:go_to_gateway_view')

    else:
        messages.info('you have no active order')
        return redirect('core:home')
    context = {
        'form': form,
    }
    return render(request, 'checkout-page.html', context)


@login_required
def feedback(request, slug):
    form = FeedbackForm()
    obj = get_object_or_404(Item, slug=slug)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            f_model, created = FeedbackModel.objects.get_or_create(
                user=request.user,
                feedback_for=obj,
            )
            if not created:
                pass

            else:
                f_model.feedback = form.cleaned_data['feedback']
                f_model.save()

    return redirect('core:detail', slug=slug)
