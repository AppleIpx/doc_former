from django.db import models
from users.models import User


class Assignment(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название работы",
        blank=False,
    )
    sample_document_report = models.FileField(
        verbose_name="Отчет по практике",
        upload_to='assignment_documents/',
        null=True,
        blank=True,
    )
    sample_document_diary_practices = models.FileField(
        verbose_name="Дневник практики",
        upload_to='assignment_documents/',
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        verbose_name="Описание к работе",
        blank=True,
    )
    deadline = models.DateTimeField(
        verbose_name="Крайний срок сдачи"
    )
    teacher = models.ForeignKey(
        User,
        verbose_name="Преподаватель",
        max_length=150,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title


class StudentSolution(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='solutions',
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    report_file = models.FileField(
        upload_to='student_solutions/',
    )
    diary_practices = models.FileField(
        upload_to="student_solutions/",
    )
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"работа {self.assignment} студент:{self.student}"


class TeacherFeedback(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        verbose_name="тема задания",
        on_delete=models.CASCADE,
        related_name='feedback',
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    grade = models.PositiveIntegerField(
        verbose_name="Оценка",
        null=True,
        blank=True,
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        blank=True,
    )
    feedback_file = models.FileField(
        verbose_name="файл отзыва",
        upload_to='teacher_feedback/',
        null=True,
        blank=True,
    )
    submission_date = models.DateTimeField(
        verbose_name="дата публикации",
        auto_now_add=True,
    )

    def __str__(self):
        return f"работа:{self.assignment} студент: {self.student}"

