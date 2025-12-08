from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from ckeditor.fields import RichTextField

class Badge(models.Model):
    """Модель для значків (досягнень) користувачів"""
    name = models.CharField(max_length=100, verbose_name='Назва значка')
    description = models.TextField(verbose_name='Опис значка')
    icon = models.ImageField(upload_to='badges/', verbose_name='Іконка значка')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок відображення')
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    legendary = models.BooleanField(default=False, verbose_name='Легендарний')

    class Meta:
        verbose_name = 'Значок'
        verbose_name_plural = 'Значки'
        ordering = ['order']

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    user_pic = models.ImageField(blank=True, upload_to='coins/user_pic/')
    phone = models.CharField(max_length=20, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    addres = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=20, blank=True)
    badges = models.ManyToManyField(Badge, blank=True, related_name='users', verbose_name='Значки')

    # New Fields
    # coin_holders = models.PositiveIntegerField(default=0)
    # holder_pages = models.PositiveIntegerField(default=0)
    # albums = models.PositiveIntegerField(default=0)
    # postage_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def has_offers_under_consideration(self):
        offers = Offer.objects.filter(responder=self.user, status='c')
        return offers.exists()

    def has_multi_offers_under_consideration(self):
        offers = MultiOffer.objects.filter(responder=self.user, status__in=['c', 'a'])
        return offers.exists()

    def multi_offers_under_consideration(self):
        offers = MultiOffer.objects.filter(responder=self.user, status__in=['c', 'a'])
        return offers

    def multi_offers_to_other_users_under_consideration(self):
        offers = MultiOffer.objects.filter(author=self.user, status__in=['c', 'a'])
        return offers

    def history_of_offers_by_user(self):
        history = MultiOffer.objects.filter((Q(author=self.user) | Q(responder=self.user)) & Q(status='d'))
        return history

    def active_coins(self):
        return self.user.coins.filter(status='a')

    def coins_on_verification(self):
        return self.user.coins.filter(status='v')

    def exchanged_coins(self):
        return self.user.coins.filter(status='e')

    def coins_wait_for_delivery(self):
        return self.user.coins.filter(status='w')

    def coins_sent(self):
        return self.user.coins.filter(status='s')

    def unread_messages_count(self):
        return self.user.received_messages.filter(is_read=False).count()

    def earned_badges(self):
        """Повертає всі зароблені значки користувача"""
        return self.badges.filter(is_active=True)

    def add_badge(self, badge):
        """Додає значок користувачу"""
        if badge.is_active:
            self.badges.add(badge)

    def remove_badge(self, badge):
        """Видаляє значок у користувача"""
        self.badges.remove(badge)

    def has_badge(self, badge):
        """Перевіряє чи має користувач певний значок"""
        return self.badges.filter(id=badge.id, is_active=True).exists()
    
    def has_legendary_badge(self):
        """Перевіряє чи має користувач легендарні значки"""
        return self.badges.filter(legendary=True, is_active=True).exists()

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
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)

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
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']

    def get_active_coins(self):
        return Coin.objects.filter(country=self, status="a")

    def __str__(self):
        return self.name


class CoinCategory(models.Model):
    name = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    countries = models.ManyToManyField(Country, blank=True, related_name='coin_categories')
    continents = models.ManyToManyField(Continent, blank=True, related_name='coin_categories')
    ordering = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Категорія монет"
        verbose_name_plural = "Категорії монет"
        ordering = ['ordering']

    def get_all_subcategories(self):
        """Отримати всі підкатегорії рекурсивно"""
        subcategories = list(self.subcategories.all())
        for subcategory in self.subcategories.all():
            subcategories.extend(subcategory.get_all_subcategories())
        return subcategories

    def get_all_coins(self):
        """Отримати всі монети в цій категорії та підкатегоріях"""
        subcategories = self.get_all_subcategories()
        return Coin.objects.filter(
            (Q(category=self) | Q(category__in=subcategories)) & Q(status='a')
        ).distinct()

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    
class TypeObject(models.Model):
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    ordering = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Type Object"
        verbose_name_plural = "Types Objects"
        ordering = ['ordering']
        

class Topic(models.Model):
    name = models.CharField(max_length=150, unique=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    ordering = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ['ordering']


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

status_choices_coin = [('a', 'active'), ('n', 'not active'), ('e', 'exchanged'), ('v', 'sent for verification'), ('w', 'wait for delivery'), ('s', 'sent')]


class Coin(models.Model):
    type_object = models.ForeignKey(TypeObject, on_delete=models.SET_NULL, related_name='object_coins', blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, related_name='topic_coins', blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    img_front = models.ImageField(upload_to='products_image', blank=True)
    img_back = models.ImageField(upload_to='products_image', blank=True)
    img_add_1 = models.ImageField(upload_to='products_image', blank=True)
    img_add_2 = models.ImageField(upload_to='products_image', blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='coins')  # Reference to Country
    category = models.ManyToManyField(CoinCategory, blank=True, related_name='coins')
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
    sent_for_verification_date = models.DateTimeField(blank=True, null=True)
    views_counter = models.IntegerField(default=0)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True, help_text='Tracking number for coin verification shipment')
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Coin'
        verbose_name_plural = 'Coins'
        ordering = ['-id']

    def __str__(self):
        return f'{self.country.name} - {self.denomination} - {self.year}'
    
    def delete(self, *args, **kwargs):
        # Delete QR code image if it exists
        if self.qr_code:
            self.qr_code.delete(save=False)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.pk:
            try:
                old_coin = Coin.objects.get(pk=self.pk)
                # Delete QR code if field is cleared
                if old_coin.qr_code and not self.qr_code:
                    old_coin.qr_code.delete(save=False)
            except Coin.DoesNotExist:
                pass

        if not self.qr_code and self.pk:
            # Get the absolute URL for the coin
            base_url = getattr(settings, 'SITE_URL', 'https://collectohub.co.uk')
            absolute_url = f"{base_url}/coin/{self.pk}/"
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(absolute_url)
            qr.make(fit=True)
            
            # Create PIL image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code image
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            
            # Create Django file and save to model
            filename = f'qr_coin_{self.pk}.png'
            self.qr_code.save(
                filename,
                File(buffer),
                save=False
            )
            
        if self.pk:
            old_coin = Coin.objects.get(pk=self.pk)
            if old_coin.box is None and self.box is not None:
                # Check for active MultiOffers containing this coin
                multi_offers = MultiOffer.objects.filter(
                    (Q(coins_to_get=self) | Q(coins_to_give=self)),
                    status='a'
                ).distinct()
                
                for offer in multi_offers:
                    # Message for author
                    Message.objects.create(
                        text=f'Object {self.country.name} {self.denomination if self.denomination else self.name} {self.year} has been verified. The offer is ready for confirmation.',
                        author=User.objects.get(id=1),
                        recipient=offer.author,
                        topic='Offer Update'
                    )
                    
                    # Message for responder
                    Message.objects.create(
                        text=f'Object {self.country.name} {self.denomination if self.denomination else self.name} {self.year} has been verified. The offer is ready for confirmation.',
                        author=User.objects.get(id=1),
                        recipient=offer.responder,
                        topic='Offer Update'
                    )
        
        super().save(*args, **kwargs)


class Box(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


status_choices = [('с', 'under consideration'), ('a', 'accepted'), ('d', 'done')]


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
        if self.created < timezone.now() - timedelta(days=7):
            return False
        if self.coins_to_get.all().exclude(owner=self.responder).exists():
            return False
        if self.coins_to_give.all().exclude(owner=self.author).exists():
            return False
        return True

    def valid_offer_for_accept(self):
        if self.coins_to_get.all().filter(box__isnull=True).exists():
            return False
        if self.coins_to_give.all().filter(box__isnull=True).exists():
            return False
        return True

    def who_must_verify_coins(self):
        if self.coins_to_get.all().filter(box__isnull=True).exists() and self.coins_to_give.all().filter(box__isnull=True).exists():
            return 'author and responder'
        if self.coins_to_get.all().filter(box__isnull=True).exists():
            return 'author'
        if self.coins_to_give.all().filter(box__isnull=True).exists():
            return 'responder'
        return None


class Message(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name="created_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    topic = models.CharField(default='without topic', max_length=128)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            try:
                subject = f'New message on CollectoHub: {self.topic}'
                message = f'You have received a new message from {self.author.username}:\n\n{self.text}'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.recipient.email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            except Exception:
                pass  # Ігноруємо помилки відправки, щоб не блокувати збереження повідомлення

    def __str__(self):
        return f"{self.author}: {self.topic}"

    class Meta:
        ordering = ['-created']


class UserSurvey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    created = models.DateTimeField(auto_now_add=True)
    
    # Інтереси щодо монет
    year_from = models.IntegerField(blank=True, null=True, help_text='Рік початку діапазону')
    year_to = models.IntegerField(blank=True, null=True, help_text='Рік кінця діапазону')
    interested_materials = models.CharField(max_length=200, blank=True, choices=material_choices, help_text='Матеріали монет')
    interested_continents = models.ManyToManyField(Continent, blank=True, related_name='interested_users')
    interested_countries = models.ManyToManyField(Country, blank=True, related_name='interested_users')
    additional_notes = models.TextField(blank=True, help_text='Додаткові примітки')

    class Meta:
        verbose_name = 'Опитування користувача'
        verbose_name_plural = 'Опитування користувачів'
        ordering = ['-created']

    def __str__(self):
        return f'Опитування {self.user.username} від {self.created.strftime("%d.%m.%Y")}'
    
    
class PageSeo(models.Model):
    url = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    
class GlobalScript(models.Model):
    POSITION_CHOICES = [
        ('head', 'Inside <head>'),
        ('body_top', 'Top of <body>'),
        ('body_bottom', 'Bottom of <body>'),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='head'
    )
    content = models.TextField(help_text="Insert full <script>...</script> or inline JS")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_position_display()})"
