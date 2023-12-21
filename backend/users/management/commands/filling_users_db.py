from django.core.management.base import BaseCommand
from users.models import User
import string
import secrets
from django.contrib.auth.hashers import make_password


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("info_users.csv", 'r', encoding="utf-8") as file:
            for line in file:
                password = generate_random_string(8)
                element = line.split(",")
                User.objects.get_or_create(
                    pk=element[0],
                    last_name=element[1],
                    first_name=element[2],
                    patronymic=element[3],
                    course=element[6],
                    direction_specialty=element[7],
                    group=element[9],
                    email=element[11],
                    first_password=password,
                    username=generate_random_string(12),
                    password=make_password(password),
                    is_teacher=False,
                    faculty="Факультет Компьютерных Наук",
                )
