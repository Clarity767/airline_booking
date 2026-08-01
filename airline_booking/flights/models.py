from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Airport(models.Model):

    name = models.CharField("Назва", max_length=100)
    city = models.CharField("Місто", max_length=100)
    country = models.CharField("Країна", max_length=100)
    code = models.CharField(
        "Код IATA",
        max_length=3,
        unique=True,
        help_text="Трилітерний код аеропорту, наприклад KBP",
    )

    class Meta:
        verbose_name = "Аеропорт"
        verbose_name_plural = "Аеропорти"
        ordering = ["city"]

    def __str__(self):
        return f"{self.city} ({self.code})"

    def clean(self):
        if self.code:
            self.code = self.code.upper()


class Flight(models.Model):


    departure_airport = models.ForeignKey(
        Airport,
        verbose_name="Аеропорт вильоту",
        related_name="departures",
        on_delete=models.CASCADE,
    )
    arrival_airport = models.ForeignKey(
        Airport,
        verbose_name="Аеропорт прильоту",
        related_name="arrivals",
        on_delete=models.CASCADE,
    )
    departure_time = models.DateTimeField("Час вильоту")
    arrival_time = models.DateTimeField("Час прильоту")
    airline = models.CharField("Авіакомпанія", max_length=100)
    aircraft = models.CharField("Тип літака", max_length=100, blank=True)
    price = models.DecimalField(
        "Ціна",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    available_seats = models.PositiveIntegerField("Вільні місця")

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейси"
        ordering = ["departure_time"]

    def __str__(self):
        return (
            f"{self.airline}: {self.departure_airport.code} → "
            f"{self.arrival_airport.code} ({self.departure_time:%d.%m.%Y %H:%M})"
        )

    def clean(self):
        if (
            self.departure_airport_id
            and self.arrival_airport_id
            and self.departure_airport_id == self.arrival_airport_id
        ):
            raise ValidationError(
                "Аеропорт вильоту та прильоту не можуть збігатися."
            )
        if self.departure_time and self.arrival_time:
            if self.arrival_time <= self.departure_time:
                raise ValidationError(
                    "Час прильоту повинен бути пізніше часу вильоту."
                )

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    @property
    def is_available(self):
        return self.available_seats > 0


class Booking(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Користувач",
        related_name="bookings",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    full_name = models.CharField("ПІБ пасажира", max_length=150)
    email = models.EmailField("Email")
    flight = models.ForeignKey(
        Flight,
        verbose_name="Рейс",
        related_name="bookings",
        on_delete=models.CASCADE,
    )
    seats = models.PositiveIntegerField(
        "Кількість місць",
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        verbose_name = "Бронювання"
        verbose_name_plural = "Бронювання"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.flight} ({self.seats} місць)"

    @property
    def total_price(self):
        return self.flight.price * self.seats