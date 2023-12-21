# Generated by Django 5.0 on 2023-12-20 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название работы')),
                ('sample_document_report', models.FileField(blank=True, null=True, upload_to='sample_document/')),
                ('sample_document_diary_practices', models.FileField(blank=True, null=True, upload_to='sample_document/')),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, verbose_name='Описание к работе')),
                ('deadline', models.DateTimeField(verbose_name='Крайний срок сдачи')),
            ],
        ),
        migrations.CreateModel(
            name='StudentSolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solution_file', models.FileField(upload_to='student_solutions/')),
                ('submission_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeacherFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveIntegerField(blank=True, null=True, verbose_name='Оценка')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('feedback_file', models.FileField(blank=True, null=True, upload_to='teacher_feedback/', verbose_name='файл отзыва')),
                ('submission_date', models.DateTimeField(auto_now_add=True, verbose_name='дата публикации')),
            ],
        ),
    ]
