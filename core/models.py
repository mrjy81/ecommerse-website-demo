from django.db import models
from django.conf import settings
from django.shortcuts import reverse
CATEGORY_CHIOSES = (
    ('s', 'shirts'),
    ('sw', 'sport wear'),
    ('ow', 'outwears'),

)
LABEL_CHIOSES = (
    ('p', 'primary'),
    ('s', 'secondary'),
    ('d', 'danger'),

)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_price = models.IntegerField(null=True, blank=True)
    category = models.CharField(choices=CATEGORY_CHIOSES, max_length=50)
    label = models.CharField(choices=LABEL_CHIOSES, max_length=50)
    image = models.ImageField(upload_to='products',
                              default='products/shirt.png')
    slug = models.SlugField()

    def get_feedback(self):
        return reverse("core:feedback", kwargs={"slug": self.slug})

    def get_absolute_url(self):
        return reverse("core:detail", kwargs={"slug": self.slug})

    def get_add_to_cart(self):
        return reverse("core:add_to_cart", kwargs={"slug": self.slug})

    def get_delete_from_cart(self):
        return reverse("core:delete_from_cart", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def get_each_order_total_price(self):
        return self.quantity * self.item.price

    def get_single_delete_from_cart(self):
        return reverse("core:decrease", kwargs={"slug": self.item.slug})

    def get_single_add_from_cart(self):
        return reverse("core:increase", kwargs={"slug": self.item.slug})

    def get_delete_all_qty_of_instance(self):
        return reverse("core:delete-all", kwargs={"slug": self.item.slug})

    def __str__(self):
        return f'{self.user.username} ordered {self.quantity} of {self.item.title}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def get_total_price(self):
        return sum([i.get_each_order_total_price() for i in self.items.all()])

    def __str__(self):
        return self.user.username


class CheckoutModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField()
    zip = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


class FeedbackModel(models.Model):
    user = user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE)
    feedback = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    feedback_for = models.ForeignKey(
        Item, on_delete=models.CASCADE)

    def __str__(self):
        return f'feedback of {self.user.username} on {self.feedback_for} on {self.created}'
