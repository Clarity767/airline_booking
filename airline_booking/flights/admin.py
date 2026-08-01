from django.contrib import admin
from django.contrib import admin

from .models import Airport, Booking, Flight


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city", "country")
    search_fields = ("code", "name", "city", "country")
    list_filter = ("country",)
    ordering = ("city",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "airline",
        "departure_time",
        "arrival_time",
        "price",
        "available_seats",
    )
    list_filter = ("airline", "departure_airport", "arrival_airport")
    search_fields = (
        "airline",
        "aircraft",
        "departure_airport__city",
        "arrival_airport__city",
        "departure_airport__code",
        "arrival_airport__code",
    )
    date_hierarchy = "departure_time"
    ordering = ("departure_time",)
    autocomplete_fields = ("departure_airport", "arrival_airport")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "flight", "seats", "created_at")
    list_filter = ("flight__airline", "created_at")
    search_fields = ("full_name", "email", "flight__airline")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)