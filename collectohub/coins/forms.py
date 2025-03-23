from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Message


class MyUserCreationForm(UserCreationForm):
    user_picture = forms.ImageField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=70)
    phone = forms.CharField(max_length=20)
    postcode = forms.CharField(max_length=10)
    addres = forms.CharField(max_length=150)
    city = forms.CharField(max_length=20)

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', ]
        labels = {'text': ""}
