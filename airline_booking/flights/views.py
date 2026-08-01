from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from .forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .forms import BookingForm, FlightSearchForm, ProfileEditForm
from .models import Booking, Flight
from .forms import RegisterForm

def home(request):
    form = FlightSearchForm(request.GET or None)

    if request.GET:
        query = request.GET.urlencode()
        url = reverse("flights:flight_list")
        return redirect(f"{url}?{query}" if query else url)

    return render(request, "flights/home.html", {"form": form})


def flight_list(request):
    form = FlightSearchForm(request.GET or None)
    flights = Flight.objects.select_related(
        "departure_airport", "arrival_airport"
    ).all()
    flights = flights.filter(departure_time__gte=timezone.now())

    from_city = request.GET.get("from_city", "").strip()
    to_city = request.GET.get("to_city", "").strip()
    date = request.GET.get("date", "").strip()
    airline = request.GET.get("airline", "").strip()
    sort = request.GET.get("sort", "").strip()

    if from_city:
        flights = flights.filter(departure_airport__city__icontains=from_city)
    if to_city:
        flights = flights.filter(arrival_airport__city__icontains=to_city)
    if date:
        flights = flights.filter(departure_time__date=date)
    if airline:
        flights = flights.filter(airline=airline)

    if sort in ("price", "-price"):
        flights = flights.order_by(sort)


    airlines = (
        Flight.objects.order_by("airline")
        .values_list("airline", flat=True)
        .distinct()
    )

    paginator = Paginator(flights, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
    context = {
        "form": form,
        "page_obj": page_obj,
        "flights": page_obj.object_list,
        "airlines": airlines,
        "current_airline": airline,
        "current_sort": sort,
        "elided_page_range": elided_page_range,
    }
    return render(request, "flights/flight_list.html", context)


def flight_detail(request, pk):
    flight = get_object_or_404(
        Flight.objects.select_related("departure_airport", "arrival_airport"),
        pk=pk,
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Щоб забронювати квиток, увійдіть у свій акаунт.")
            return redirect(f"{reverse('flights:login')}?next={request.path}")

        form = BookingForm(request.POST, flight=flight)
        if form.is_valid():
            seats_requested = form.cleaned_data["seats"]
            try:
                with transaction.atomic():
                    locked_flight = Flight.objects.select_for_update().get(pk=flight.pk)

                    if seats_requested > locked_flight.available_seats:
                        messages.error(
                            request,
                            f"На жаль, вільних місць лише "
                            f"{locked_flight.available_seats}. "
                            f"Спробуйте зменшити кількість квитків.",
                        )
                        return redirect("flights:flight_detail", pk=flight.pk)

                    booking = form.save(commit=False)
                    booking.flight = locked_flight
                    booking.user = request.user
                    booking.save()

                    locked_flight.available_seats -= seats_requested
                    locked_flight.save(update_fields=["available_seats"])
            except Flight.DoesNotExist:
                messages.error(request, "Цей рейс більше не доступний.")
                return redirect("flights:flight_list")

            messages.success(
                request,
                f"Бронювання успішне! Заброньовано {seats_requested} місць "
                f"на рейс {locked_flight}.",
            )
            return redirect("flights:booking_confirmation", pk=booking.pk)
    else:
        form = BookingForm(flight=flight)

    return render(
        request, "flights/flight_detail.html", {"flight": flight, "form": form}
    )


def booking_confirmation(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "flight", "flight__departure_airport", "flight__arrival_airport"
        ),
        pk=pk,
    )
    return render(request, "flights/confirmation.html", {"booking": booking})


def register(request):
    if request.user.is_authenticated:
        return redirect("flights:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Ласкаво просимо, {user.username}!")
            return redirect("flights:profile")
    else:
        form = RegisterForm()

    return render(request, "flights/register.html", {"form": form})


def profile(request):
    if not request.user.is_authenticated:
        return redirect("flights:login")

    now = timezone.now()

    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("flight", "flight__departure_airport", "flight__arrival_airport")
        .order_by("-created_at")
    )

    # ---------- Статистика ----------
    total_bookings = bookings.count()
    total_spent = sum((booking.total_price for booking in bookings), 0)

    nearest_booking = (
        bookings.filter(flight__departure_time__gte=now)
        .order_by("flight__departure_time")
        .first()
    )

    # ---------- Ініціали для аватара ----------
    if request.user.first_name:
        initials = request.user.first_name[0].upper()
        if request.user.last_name:
            initials += request.user.last_name[0].upper()
    else:
        initials = request.user.username[:2].upper()

    return render(
        request,
        "flights/profile.html",
        {
            "bookings": bookings,
            "now": now,
            "total_bookings": total_bookings,
            "total_spent": total_spent,
            "nearest_booking": nearest_booking,
            "initials": initials,
        },
    )


def profile_edit(request):
    if not request.user.is_authenticated:
        return redirect("flights:login")

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Дані профілю оновлено.")
            return redirect("flights:profile")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "flights/profile_edit.html", {"form": form})


def change_password(request):
    if not request.user.is_authenticated:
        return redirect("flights:login")

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успішно змінено.")
            return redirect("flights:profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "flights/change_password.html", {"form": form})


def cancel_booking(request, pk):
    if not request.user.is_authenticated:
        return redirect("flights:login")

    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == "POST":
        with transaction.atomic():
            flight = Flight.objects.select_for_update().get(pk=booking.flight_id)
            flight.available_seats += booking.seats
            flight.save(update_fields=["available_seats"])
            booking.delete()

        messages.success(request, "Бронювання скасовано.")
        return redirect("flights:profile")

    return render(request, "flights/cancel_booking_confirm.html", {"booking": booking})