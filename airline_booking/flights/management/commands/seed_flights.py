"""
Положите файл в: flights/management/commands/seed_flights.py
(нужны пустые __init__.py в flights/management/ и flights/management/commands/)

Запуск:
    python manage.py seed_flights
    python manage.py seed_flights --days 30 --clear
"""

import random
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from flights.models import Airport, Flight


AIRPORTS = [
    # (name, city, country, code)
    ("Бориспіль", "Київ", "Україна", "KBP"),
    ("Львів", "Львів", "Україна", "LWO"),
    ("Одеса", "Одеса", "Україна", "ODS"),
    ("Харків", "Харків", "Україна", "HRK"),
    ("Дніпро", "Дніпро", "Україна", "DNK"),
    ("Шопен", "Варшава", "Польща", "WAW"),
    ("Тегель", "Берлін", "Німеччина", "TXL"),
    ("Шарль де Голль", "Париж", "Франція", "CDG"),
    ("Фьюмічіно", "Рим", "Італія", "FCO"),
    ("Ель-Прат", "Барселона", "Іспанія", "BCN"),
    ("Ататюрк", "Стамбул", "Туреччина", "IST"),
    ("Швехат", "Відень", "Австрія", "VIE"),
    ("Вацлав Гавел", "Прага", "Чехія", "PRG"),
    ("Хітроу", "Лондон", "Великобританія", "LHR"),
    ("Схіпгол", "Амстердам", "Нідерланди", "AMS"),
]

AIRLINES = [
    "Ukraine International Airlines",
    "Wizz Air",
    "Ryanair",
    "LOT Polish Airlines",
    "Turkish Airlines",
    "Lufthansa",
]

AIRCRAFTS = ["Boeing 737", "Airbus A320", "Embraer 195", "Airbus A321"]


class Command(BaseCommand):
    help = "Наполняет базу аэропортами и рейсами по ВСЕМ парам городов в обе стороны"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30,
                             help="На сколько дней вперёд генерировать рейсы (для каждой пары)")
        parser.add_argument("--clear", action="store_true",
                             help="Удалить старые рейсы перед заполнением")

    def handle(self, *args, **options):
        # 1. Аэропорты
        airports = []
        for name, city, country, code in AIRPORTS:
            airport, _ = Airport.objects.get_or_create(
                code=code,
                defaults={"name": name, "city": city, "country": country},
            )
            airports.append(airport)
        self.stdout.write(self.style.SUCCESS(f"Аэропортов в базе: {len(airports)}"))

        if options["clear"]:
            Flight.objects.all().delete()
            self.stdout.write("Старые рейсы удалены.")

        # 2. Все упорядоченные пары (A->B и B->A), без A->A
        pairs = [
            (a, b) for a in airports for b in airports if a.pk != b.pk
        ]
        self.stdout.write(f"Пар маршрутов: {len(pairs)}")

        today = timezone.now().replace(minute=0, second=0, microsecond=0)
        created = 0
        flights_to_create = []

        for dep_airport, arr_airport in pairs:
            # на каждую пару — по 1 рейсу в день на N дней вперёд (гарантированное покрытие)
            for d in range(options["days"]):
                day = today + datetime.timedelta(days=d)

                dep_hour = random.randint(5, 22)
                dep_minute = random.choice([0, 15, 30, 45])
                departure_time = day.replace(hour=dep_hour, minute=dep_minute)

                duration_minutes = random.randint(60, 240)
                arrival_time = departure_time + datetime.timedelta(minutes=duration_minutes)

                flights_to_create.append(Flight(
                    departure_airport=dep_airport,
                    arrival_airport=arr_airport,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    airline=random.choice(AIRLINES),
                    aircraft=random.choice(AIRCRAFTS),
                    price=round(random.uniform(800, 6500), 2),
                    available_seats=random.randint(0, 180),
                ))

        Flight.objects.bulk_create(flights_to_create)
        created = len(flights_to_create)

        self.stdout.write(self.style.SUCCESS(f"Создано рейсов: {created}"))