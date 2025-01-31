from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    user_pic = models.ImageField(blank=True, upload_to='coins/user_pic/')
    phone = models.CharField(max_length=20, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    addres = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=20, blank=True)

    # New Fields
    # coin_holders = models.PositiveIntegerField(default=0)
    # holder_pages = models.PositiveIntegerField(default=0)
    # albums = models.PositiveIntegerField(default=0)
    # postage_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def has_offers_under_consideration(self):
        offers = Offer.objects.filter(responder=self.user, status='c')
        return offers.exists()

    def has_multi_offers_under_consideration(self):
        offers = MultiOffer.objects.filter(responder=self.user, status='c')
        return offers.exists()

    def multi_offers_under_consideration(self):
        offers = MultiOffer.objects.filter(responder=self.user, status='c')
        return offers

    def multi_offers_to_other_users_under_consideration(self):
        offers = MultiOffer.objects.filter(author=self.user, status='c')
        return offers

    def history_of_offers_by_user(self):
        history = MultiOffer.objects.filter((Q(author=self.user) | Q(responder=self.user)) & Q(status='d'))
        return history

    def active_coins(self):
        return self.user.coins.filter(status='a')

    def exchanged_coins(self):
        return self.user.coins.filter(status='e')

    def coins_wait_for_delivery(self):
        return self.user.coins.filter(status='w')

    def coins_sent(self):
        return self.user.coins.filter(status='s')

    def unread_messages_count(self):
        return self.user.received_messages.filter(is_read=False).count()

    # New Methods
    # def total_coins_sent(self):
    #     return self.user.coins.filter(status='s').count()

    # def total_trades(self):
    #     return Offer.objects.filter(author=self.user, status='d').count() + MultiOffer.objects.filter(author=self.user, status='d').count()

    # def total_cost(self):
    #     photo_fee = self.total_coins_sent() * 0.15
    #     exchange_fee = self.total_trades() * 0.35
    #     additional_services_cost = (self.coin_holders * 0.50) + (self.holder_pages * 1.00) + (self.albums * 10.00)
    #     return photo_fee + exchange_fee + additional_services_cost + self.postage_fee

    def __str__(self):
        return self.user.username


class Continent(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Continent"
        verbose_name_plural = "Continents"

    def get_coins(self):
        return Coin.objects.filter(country__continent=self)

    def get_active_coins(self):
        return Coin.objects.filter(country__continent=self, status="a")

    def get_coutries_has_coins(self):
        return self.countries.filter(coins__isnull=False).distinct().order_by('name')

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=150, unique=True)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name="countries")

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


safety_choices = [('v', 'v'), ('vf', 'vf'), ('f', 'f'), ('xf', 'xf')]
material_choices = [
    ("gold", "au"),
    ("silver", "ag"),
    ("platinum", "pt"),
    ("palladium", "pd"),
    ("copper", "cu"),
    ("nickel", "ni"),
    ("zinc", "zn"),
    ("tin", "sn"),
    ("bronze", "bronze"),  # bronze is a metal alloy, not a pure element
    ("brass", "brass"),  # brass is also a metal alloy
    ("cupronickel", "cupronickel"),  # cupronickel is a metal alloy
    ("aluminum", "al"),
    ("iron", "fe"),
    ("lead", "pb"),
    ("magnesium", "mg"),
    ("magnetic metals", "magnetic metals"),  # general category, not a specific metal
    ("titanium", "ti")
]

status_choices_coin = [('a', 'active'), ('n', 'not active'), ('e', 'exchanged'), ('w', 'wait for delivery'), ('s', 'sent')]


class Coin(models.Model):
    img_front = models.ImageField(upload_to='products_image', blank=True)
    img_back = models.ImageField(upload_to='products_image', blank=True)
    img_add_1 = models.ImageField(upload_to='products_image', blank=True)
    img_add_2 = models.ImageField(upload_to='products_image', blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='coins')  # Reference to Country
    denomination = models.CharField(max_length=150)  # Denomination
    year = models.IntegerField()  # Year
    material = models.CharField(max_length=15, blank=True, choices=material_choices)  # Material
    safety = models.CharField(max_length=2, blank=True, choices=safety_choices)  # Optional field for admin use
    weight = models.FloatField(blank=True, null=True)  # Weight
    diameter = models.FloatField(blank=True, null=True)  # Diameter
    thickness = models.FloatField(blank=True, null=True)  # Thickness
    circulation = models.IntegerField(blank=True, null=True)  # Circulation
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coins')
    box = models.ForeignKey('Box', on_delete=models.SET_NULL, blank=True, null=True, related_name='coins')
    status = models.CharField(max_length=1, choices=status_choices_coin, default='a')
    views_counter = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Coin'
        verbose_name_plural = 'Coins'

    def __str__(self):
        return f'{self.country.name} - {self.denomination} - {self.year}'


class Box(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


status_choices = [('с', 'under consideration'), ('d', 'done')]


class Offer(models.Model):
    coin_to_get = models.ForeignKey(Coin, related_name='offer_get', on_delete=models.CASCADE)
    coin_to_give = models.ForeignKey(Coin, related_name='offer_give', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='offers_made', on_delete=models.CASCADE)
    responder = models.ForeignKey(User, related_name='offers_look', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=status_choices, default='c')
    created = models.DateTimeField(auto_now_add=True)


class MultiOffer(models.Model):
    coins_to_get = models.ManyToManyField(Coin, related_name='offers_get')
    coins_to_give = models.ManyToManyField(Coin, related_name='offers_give')
    message = models.TextField(blank=True, help_text='Message')
    author = models.ForeignKey(User, related_name='multi_offers_made', on_delete=models.CASCADE)
    responder = models.ForeignKey(User, related_name='multi_offers_look', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=status_choices, default='c')
    created = models.DateTimeField(auto_now_add=True)

    def valid_offer(self):
        if self.coins_to_get.all().exclude(owner=self.responder).exists():
            return False
        if self.coins_to_give.all().exclude(owner=self.author).exists():
            return False
        return True


class Message(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name="created_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    topic = models.CharField(default='without topic', max_length=128)

    def __str__(self):
        return f"{self.author}: {self.topic}"

    class Meta:
        ordering = ['-created']
