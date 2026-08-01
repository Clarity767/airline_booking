from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django import forms
from django import forms
from django.contrib.auth import get_user_model
from .models import Booking
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
User = get_user_model()

class FlightSearchForm(forms.Form):
    from_city = forms.CharField(
        label="Звідки",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Місто вильоту"}
        ),
    )
    to_city = forms.CharField(
        label="Куди",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Місто прильоту"}
        ),
    )
    date = forms.DateField(
        label="Дата",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["full_name", "email", "seats"]
        labels = {
            "full_name": "ПІБ пасажира",
            "email": "Email",
            "seats": "Кількість місць",
        }
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Іван Іванов"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@mail.com"}
            ),
            "seats": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, flight=None, **kwargs):
        self.flight = flight
        super().__init__(*args, **kwargs)

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if not full_name:
            raise forms.ValidationError("Вкажіть ПІБ пасажира.")
        return full_name

    def clean_seats(self):
        seats = self.cleaned_data["seats"]
        if seats < 1:
            raise forms.ValidationError("Кількість місць має бути не менше 1.")
        if self.flight is not None and seats > self.flight.available_seats:
            raise forms.ValidationError(
                f"Недостатньо вільних місць. Доступно лише "
                f"{self.flight.available_seats}."
            )
        return seats
    
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Ім'я користувача"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Пароль"}
        )
 
 
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@mail.com"}
        ),
    )
 
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Ім'я користувача"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Пароль"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Повторіть пароль"}
        )
        for field in self.fields.values():
            field.label_suffix = ""
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ім'я",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Прізвище",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "email@example.com",
            }),
        }
        labels = {
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "email": "Email",
        }
 
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email:
            raise forms.ValidationError("Email обов'язковий.")
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Цей email вже використовується іншим користувачем.")
        return email
    

class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})