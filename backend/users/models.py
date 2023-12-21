from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = (
        'id',
        'first_name',
        'last_name',
        'is_teacher',
    )

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=100,
        blank=False
    )

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=100,
        blank=False
    )

    patronymic = models.CharField(
        verbose_name="Отчество",
        max_length=100,
        blank=True,
    )

    username = models.CharField(
        verbose_name="Логин",
        max_length=100,
        unique=True,
        blank=False
    )

    course = models.CharField(
        verbose_name="Курс",
        max_length=15,
        blank=False,
    )

    direction_specialty = models.CharField(
        verbose_name="Направление/специальность",
        max_length=100,
        blank=False,
    )

    group = models.CharField(
        verbose_name="Группа",
        max_length=30,
        blank=False,
    )

    email = models.CharField(
        verbose_name="Электронная почта",
        max_length=100,
        blank=True,
    )

    first_password = models.CharField(
        verbose_name="Пароль до регистрации пользователя",
        max_length=50,
        blank=False,
    )

    is_teacher = models.BooleanField(
        verbose_name="Состояния преподавателя",
        max_length=10,
        blank=True,
    )

    faculty = models.CharField(
        verbose_name="Факультет",
        max_length=100,
        blank=True,
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
