from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView, View
from rest_framework import generics


import os
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required

from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator

from .forms import *
from .sterializers import *


class IndexView(ListView):
    model = Coin
    context_object_name = "coin_list"
    template_name = 'coins/index.html'
    extra_context = {
        "continent_list": Continent.objects.all().order_by("name"),
    }
    paginate_by = 12

    def get_queryset(self):
        queryset = Coin.objects.filter(status='a').order_by('-views_counter')
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(owner=self.request.user)

        return queryset
    
    
class AboutView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, 'coins/about.html', {'success': True})
    
    
class OwnerPublicView(DetailView):
    model = User
    template_name = 'coins/owner-public.html'
    
    def get_context_data(self, **kwargs):
        
        owner = User.objects.get(id=self.kwargs["pk"])
        
        coins = Coin.objects.filter(status='a', owner__id=owner.id)
            
        paginator = Paginator(coins, 12)
        page = self.request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
            
        context = { 'coins': coins, 'owner': owner }
            
        return context


class CoinDetailView(DetailView):
    model = Coin
    extra_context = {
        'form': MessageForm(),
    }

    def get_object(self, queryset=None):
        object = super().get_object(queryset=queryset)
        object.views_counter += 1
        object.save()
        return object


def signin(request):
    context = { 'errors': None }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request=request, username=username, password=password)
        context = { 'errors': None }
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('coins:index'))
        else:
            context['errors'] = 'User found, check username or password'
    return render(
        request,
        'coins/sing_in.html',
        context
    )


def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('coins:index'))


def offer_detail(request):
    coin_id = request.POST.get('coin_id')
    return HttpResponseRedirect(reverse('coins:coin-make-offer', kwargs={"pk": coin_id}))


class CoinMakeOfferView(DetailView):
    model = Coin
    template_name = 'coins/coin_make_offer.html'


def make_offer(request):
    coin_to_get_id = request.POST.get('coin_to_get_id')
    coin_to_give_id = request.POST.get('coin_to_give_id')
    if coin_to_get_id and coin_to_give_id:
        coin_to_get = Coin.objects.get(id=coin_to_get_id)
        coin_to_give = Coin.objects.get(id=coin_to_give_id)
        new_offer = Offer(
            coin_to_get=coin_to_get,
            coin_to_give=coin_to_give,
            author=coin_to_give.owner,
            responder=coin_to_get.owner,
        )
        new_offer.save()

    return HttpResponseRedirect(reverse('coins:index'))


def offers_by_user(request):
    context = {
        'object_list': Offer.objects.filter(responder=request.user, status='c')
    }
    return render(request=request, template_name="coins/ofers_by_user.html", context=context)


def multi_offers_by_user(request):
        
    offers = MultiOffer.objects.filter(responder=request.user, status='c')
        
    paginator = Paginator(offers, 12)
    page = request.GET.get("page", 1)

    try:
        offers = paginator.page(page)
    except PageNotAnInteger:
        offers = paginator.page(1)
    except EmptyPage:
        offers = paginator.page(paginator.num_pages)
        
    context = { 'offers': offers }
    return render(request=request, template_name="coins/ofers_by_user.html", context=context)


def accept_multi_offer(request, pk):
    multi_offer = MultiOffer.objects.get(id=pk)
    coins_to_get = multi_offer.coins_to_get.all().update(
        owner = multi_offer.author,
        status = 'e'
    )
    coins_to_give = multi_offer.coins_to_give.all().update(
        owner = multi_offer.responder,
        status = 'e'
    )
    multi_offer.status = 'd'
    multi_offer.save()
    
    # Отримуємо сторінку, з якої прийшов запит
    referer_url = request.META.get('HTTP_REFERER')
    
    # Якщо немає `HTTP_REFERER`, перенаправляємо на сторінку за замовчуванням
    redirect_url = referer_url if referer_url else reverse('coins:user-cabinet-coins')
    
    return HttpResponseRedirect(redirect_url)


def cancel_multi_offer(request, pk):
    multi_offer = get_object_or_404(MultiOffer, pk=pk)
    if request.method == 'POST':
        multi_offer.delete()
    
    # Отримуємо сторінку, з якої прийшов запит
    referer_url = request.META.get('HTTP_REFERER')
    
    # Якщо немає `HTTP_REFERER`, перенаправляємо на сторінку за замовчуванням
    redirect_url = referer_url if referer_url else reverse('coins:user-cabinet-coins')
    
    return HttpResponseRedirect(redirect_url)


def cancel_offer(request, pk):
    offer = Offer.objects.get(id=pk)
    offer.delete()
    return HttpResponseRedirect(reverse('coins:index'))


def accept_offer(request, pk):
    offer = Offer.objects.get(id=pk)
    coin_to_get = offer.coin_to_get
    coin_to_give = offer.coin_to_give
    coin_to_get.owner = offer.author
    coin_to_get.status = 'e'
    coin_to_get.save()
    coin_to_give.owner = offer.responder
    coin_to_give.status = 'e'
    coin_to_give.save()
    offer.status = 'd'
    offer.save()
    return HttpResponseRedirect(reverse('coins:index'))


class CreateUserView(TemplateView):
    template_name = 'coins/create_account.html'
    extra_context = {
        'form': MyUserCreationForm(),

    }


def create_new_account(request):
    username = request.POST.get('username')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    postcode = request.POST.get('postcode')
    addres = request.POST.get('addres')
    city = request.POST.get('city')
    
    errors = {}
    
     # Валідація полів
    if not username:
        errors['username'] = 'Username is required.'
    elif len(username) < 4:
        errors['username'] = 'Username must be at least 4 characters long.'
    elif len(username) > 30:
        errors['username'] = 'Username cannot exceed 30 characters.'
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors['username'] = 'Username can only contain letters, numbers, and underscores (_).'
    elif User.objects.filter(username=username).exists():
        errors['username'] = 'A user with this username already exists.'

    # Password validation
    if not password1:
        errors['password1'] = 'Password is required.'
    elif not password2:
        errors['password2'] = 'Password is required.'
    elif password1 != password2:
        errors['password2'] = 'Passwords do not match.'
    else:
        try:
            validate_password(password1)  # Validate password according to Django standards
        except ValidationError as e:
            errors['password1'] = ', '.join(e.messages)

    # Email validation
    if not email:
        errors['email'] = 'Email is required.'
    else:
        try:
            validate_email(email)  # Validate email format
            if User.objects.filter(email=email).exists():
                errors['email'] = 'A user with this email already exists.'
        except ValidationError:
            errors['email'] = 'Invalid email format.'

    # Phone validation
    if not phone:
        errors['phone'] = 'Phone number is required.'
    elif not re.match(r'^\+?\d{10,15}$', phone):  # Simple phone number format
        errors['phone'] = 'Invalid phone number format. Use only digits.'

    # Additional field validation
    if not first_name:
        errors['first_name'] = 'First name is required.'
    if not last_name:
        errors['last_name'] = 'Last name is required.'

    # Перевірка інших полів за необхідності
    
    if errors:
        # Передаємо помилки назад у шаблон
        return render(request, 'coins/create_account.html', {'errors': errors, 'form_data': request.POST})

    new_user = User.objects.create_user(username=username, password=password2)
    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.email = email
    new_user.save()
    UserProfile.objects.create(user=new_user, phone=phone, postcode=postcode, addres=addres, city=city,
                                user_pic=request.FILES.get('user_picture'))
    login(request, new_user)

    return HttpResponseRedirect(reverse('coins:index'))

@login_required
def update_account(request):
    user = request.user
    user_profile = None
    try:
        user_profile = user.profile
    except:
        user_profile = UserProfile.objects.create(
            user=user
        )

    if request.method == 'POST':
        username = request.POST.get('username', user.username)
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        phone = request.POST.get('phone', user_profile.phone)
        postcode = request.POST.get('postcode', user_profile.postcode)
        addres = request.POST.get('addres', user_profile.addres)
        city = request.POST.get('city', user_profile.city)
        user_pic = request.FILES.get('user_pic', user_profile.user_pic)
        remove_pic = request.POST.get('remove_pic')

        errors = {}

        # Username validation
        if not username:
            errors['username'] = 'Username is required.'
        elif len(username) < 4:
            errors['username'] = 'Username must be at least 4 characters long.'
        elif len(username) > 30:
            errors['username'] = 'Username cannot exceed 30 characters.'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors['username'] = 'Username can only contain letters, numbers, and underscores (_).'
        elif username != user.username and User.objects.filter(username=username).exists():
            errors['username'] = 'A user with this username already exists.'

        # Email validation
        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
                if email != user.email and User.objects.filter(email=email).exists():
                    errors['email'] = 'A user with this email already exists.'
            except ValidationError:
                errors['email'] = 'Invalid email format.'

        # Phone validation
        if not phone:
            errors['phone'] = 'Phone number is required.'
        elif not re.match(r'^\+?\d{10,15}$', phone):
            errors['phone'] = 'Invalid phone number format. Use only digits.'

        # First name and Last name validation
        if not first_name:
            errors['first_name'] = 'First name is required.'
        if not last_name:
            errors['last_name'] = 'Last name is required.'

        # If errors exist, return them to the template
        if errors:
            return render(request, 'coins/user_cabinet/user_cabinet.html', {'errors': errors, 'form_data': request.POST})

        # Update user data
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        user.save()

        # Update UserProfile data
        user_profile.phone = phone
        user_profile.postcode = postcode
        user_profile.addres = addres
        user_profile.city = city

        # Remove profile picture if requested
        if remove_pic and user_profile.user_pic:
            old_user_pic_path = user_profile.user_pic.path
            if os.path.isfile(old_user_pic_path):
                os.remove(old_user_pic_path)
            print('remove pic')
            user_profile.user_pic.delete(save=False)  # Очищення поля user_pic
            user_profile.user_pic = None

        # Remove old profile picture if a new one is uploaded
        if user_pic and user_profile.user_pic and user_profile.user_pic != user_pic:
            old_user_pic_path = user_profile.user_pic.path
            if os.path.isfile(old_user_pic_path):
                os.remove(old_user_pic_path)

        if user_pic:
            user_profile.user_pic = user_pic

        print('save profile')
        user_profile.save()

        return render(request, 'coins/user_cabinet/user_cabinet.html', {'success': True})  # Redirect to a profile page after successful update

    # If GET request, prefill the form with the user's current data
    context = {
        'form_data': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user_profile.phone,
            'postcode': user_profile.postcode,
            'addres': user_profile.addres,
            'city': user_profile.city,
        }
    }
    return render(request, 'coins/user_cabinet/user_cabinet.html', context)


class UserCabinetView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        return render(request, 'coins/user_cabinet/user_cabinet.html')


class UserCabinetMyOffersView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        offers = request.user.profile.multi_offers_to_other_users_under_consideration()
            
        paginator = Paginator(offers, 12)
        page = request.GET.get("page", 1)

        try:
            offers = paginator.page(page)
        except PageNotAnInteger:
            offers = paginator.page(1)
        except EmptyPage:
            offers = paginator.page(paginator.num_pages)
            
        context = { 'offers': offers }
        return render(request, 'coins/user_cabinet/my_offers.html', context)


class UserCabinetOffersForMeView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        offers = request.user.profile.multi_offers_under_consideration()
            
        paginator = Paginator(offers, 12)
        page = request.GET.get("page", 1)

        try:
            offers = paginator.page(page)
        except PageNotAnInteger:
            offers = paginator.page(1)
        except EmptyPage:
            offers = paginator.page(paginator.num_pages)
            
        context = { 'offers': offers }
        return render(request, 'coins/user_cabinet/offers_for_me.html', context)


class UserCabinetCoinsView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        coins = Coin.objects.filter(owner=request.user, status='a')
            
        paginator = Paginator(coins, 12)
        page = request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
            
        context = { 'coins': coins }
            
        return render(request, 'coins/user_cabinet/my_coins.html', context)


class UserCabinetExchangedCoinsView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        coins = request.user.profile.exchanged_coins()
            
        paginator = Paginator(coins, 12)
        page = request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
            
        context = { 'coins': coins }
            
        return render(request, 'coins/user_cabinet/exchanged_coins.html', context)


class UserCabinetWaitForDeliveryView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        coins = request.user.profile.coins_wait_for_delivery()
            
        paginator = Paginator(coins, 12)
        page = request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
            
        context = { 'coins': coins }
            
        return render(request, 'coins/user_cabinet/wait_for_delivery.html', context)


class UserCabinetSentView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        coins = request.user.profile.coins_sent()
            
        paginator = Paginator(coins, 12)
        page = request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
            
        context = { 'coins': coins }
            
        return render(request, 'coins/user_cabinet/coins_sent.html', context)


class UserCabinetOffersHistoryView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')
        
        offers = request.user.profile.history_of_offers_by_user()
            
        paginator = Paginator(offers, 12)
        page = request.GET.get("page", 1)

        try:
            offers = paginator.page(page)
        except PageNotAnInteger:
            offers = paginator.page(1)
        except EmptyPage:
            offers = paginator.page(paginator.num_pages)
            
        context = { 'offers': offers }
        return render(request, 'coins/user_cabinet/offers_history.html', context)


def coin_change_status(request):
    coins = request.POST.getlist('coins', None)
    status = request.POST.get('status')
    
    if coins:
        coins = Coin.objects.filter(id__in=coins)
        if status == 'a' or status == 'w':
            coins.update(status=status)
    
    # Отримуємо сторінку, з якої прийшов запит
    referer_url = request.META.get('HTTP_REFERER')
    
    # Якщо немає `HTTP_REFERER`, перенаправляємо на сторінку за замовчуванням
    redirect_url = referer_url if referer_url else reverse('coins:user-cabinet-coins')
    
    return HttpResponseRedirect(redirect_url)


class ContinentDetailView(DetailView):
    model = Continent

    def get_context_data(self, **kwargs):
        # Отримуємо стандартний контекст від DetailView
        context = super().get_context_data(**kwargs)
        
        # Додаємо свій контекст
        coins = self.object.get_active_coins()
            
        paginator = Paginator(coins, 12)
        page = self.request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
        context['coins'] = coins
        
        return context


class CountryDetailView(DetailView):
    model = Country

    def get_context_data(self, **kwargs):
        # Отримуємо стандартний контекст від DetailView
        context = super().get_context_data(**kwargs)
        
        # Додаємо свій контекст
        coins = self.object.coins.all()
            
        paginator = Paginator(coins, 12)
        page = self.request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
        context['coins'] = coins
        
        return context


class CoinsToSendListView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("coins: index")
        
        users = User.objects.filter(coins__status='w').distinct()
            
        paginator = Paginator(users, 12)
        page = request.GET.get("page", 1)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
            
        context = { 'users': users }
            
        return render(request, 'coins/coins_to_send.html', context)


class CoinsToSendUserListView(DetailView):
    model = User
    template_name = 'coins/coins_to_send_user.html'
    
    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            return redirect("coins: index")
        
        owner = User.objects.get(id=self.kwargs["pk"])
        
        coins = Coin.objects.filter(status='w', owner__id=owner.id)
            
        paginator = Paginator(coins, 12)
        page = self.request.GET.get("page", 1)

        try:
            coins = paginator.page(page)
        except PageNotAnInteger:
            coins = paginator.page(1)
        except EmptyPage:
            coins = paginator.page(paginator.num_pages)
            
        context = { 'coins': coins, 'owner': owner }
            
        return context


def coin_sended(request):
    coins = request.POST.getlist('coins')
    coins = Coin.objects.filter(id__in=coins)
    coins.update(status='s')
    new_message = Message(
        text=f'Coin(s) have been sent to you: {coins.count} coins\nthis message was generated automatically',
        author=User.objects.get(id=1),
        recipient=coins[0].owner
    )
    new_message.save()
    return HttpResponseRedirect(reverse('coins:coins-to-send-user', kwargs={"pk": coins[0].owner.id}))


class MailBox(DetailView):
    model = User
    template_name = 'coins/mail_box.html'
    context_object_name = 'owner'


class MessageDetailView(DetailView):
    model = Message

    def get_object(self, queryset=None):
        object = super().get_object(queryset=queryset)
        if self.request.user == object.recipient:
            object.is_read = True
            object.save()
        return object


def create_new_message(request, pk):
    author_id = request.POST.get('author_id')
    recipient_id = request.POST.get('recipient_id')
    f = MessageForm(request.POST)
    new_message = f.save(commit=False)
    new_message.author_id = author_id
    new_message.recipient_id = recipient_id
    new_message.save()
    return HttpResponseRedirect(reverse('coins:coin-detail', args=[pk]))


def message_from_cabinet(request, pk):
    author_id = request.POST.get('author_id')
    recipient_id = request.POST.get('recipient_id')
    f = MessageForm(request.POST)
    new_message = f.save(commit=False)
    new_message.author_id = author_id
    new_message.recipient_id = recipient_id
    new_message.save()
    return HttpResponseRedirect(reverse('coins:user-cabinet', args=[pk]))


def multi_offer_view(request, pk):
    recipient = User.objects.get(id=pk)
    author = request.user
    context = {
        'recipient': recipient,
    }
    return render(
        request=request,
        template_name='coins/multi_offer.html',
        context=context
    )


def create_new_multi_offer(request):
    coins_to_get_ids = request.POST.getlist('coin_to_get_id')
    coins_to_give_ids = request.POST.getlist('coin_to_give_id')
    message = request.POST.get('message')

    coins_to_get = Coin.objects.filter(id__in=coins_to_get_ids)
    coins_to_give = Coin.objects.filter(id__in=coins_to_give_ids)
    # responder_id = request.POST.get('recipient_id')

    responder = User.objects.get(id=coins_to_get[0].owner.id)
    new_multi_offer = MultiOffer(
        author=request.user,
        responder=responder,
        message=message or ''
    )
    new_multi_offer.save()
    new_multi_offer.coins_to_get.add(*coins_to_get)
    new_multi_offer.coins_to_give.add(*coins_to_give)
    return HttpResponseRedirect(reverse('coins:index'))


# @login_required
# def cart_view(request):
#     user_profile = request.user.profile
#     context = {
#         'user_profile': user_profile,
#         'total_coins_sent': user_profile.total_coins_sent(),
#         'total_trades': user_profile.total_trades(),
#         'total_cost': user_profile.total_cost(),
#     }
#     return render(request, 'coins/cart.html', context)

# @require_POST
# @login_required
# def update_cart(request):
#     user_profile = request.user.profile
#     user_profile.coin_holders = request.POST.get('coin_holders', 0)
#     user_profile.holder_pages = request.POST.get('holder_pages', 0)
#     user_profile.albums = request.POST.get('albums', 0)
#     user_profile.save()
#     return HttpResponseRedirect(reverse('coins:cart'))

class MyPasswordChangeView(PasswordChangeView):
    template_name = "coins/password_change_form.html"
    success_url = reverse_lazy("coins:password-change-done")


class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "coins/password_change_done.html"


class MyPasswordResetView(PasswordResetView):
    template_name = "coins/password_reset_form.html"
    email_template_name = "coins/password_reset_email.html"
    subject_template_name = "coins/password_reset_subject.txt"
    success_url = reverse_lazy("coins:password-reset-done")


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "coins/password_reset_done.html"


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "coins/password_reset_confirm.html"
    success_url = reverse_lazy("coins:password-reset-complete")


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "coins/password_reset_complete.html"


class CoinListApiViewLatest(generics.ListAPIView):
    queryset = Coin.objects.order_by("-id")[:5]
    serializer_class = CoinsSerializer1


class CoinDetailApiView(generics.RetrieveAPIView):
    queryset = Coin.objects.all()
    serializer_class = CoinsSerializer2


class CoinUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Coin.objects.all()
    serializer_class = CoinsSerializer1


def search_coin(request):
    search_str = request.POST.get("search_field")
    search_option = request.POST.get("search_option")
    if search_str:
        if search_option == "1":
            coins = Coin.objects.filter(country__name__icontains=search_str)
        elif search_option == '2':
            coins = Coin.objects.filter(denomination__icontains=search_str)
        elif search_option == "0":
            coins = Coin.objects.filter(Q(country__name__icontains=search_str) | Q(denomination__icontains=search_str))

        return render(request, template_name="coins/search.html", context={"coin_list": coins, "pattern": search_str})

    else:
        return HttpResponseRedirect(reverse('coins:index'))
