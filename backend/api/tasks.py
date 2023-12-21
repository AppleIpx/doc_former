from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def notify_teacher_about_solution(
        student_first_name, student_last_name,
        student_patronymic, teacher_email
):
    subject = 'Student Solution Submission'
    message = f'Студент {student_first_name} {student_last_name} {student_patronymic} ' \
              f'отправил/а вам решение. Пожалуйста проверьте его и отправьте результат.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [teacher_email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def notify_student_about_feedback(
        teacher_first_name, teacher_last_name,
        teacher_patronymic, student_email, grage,
):
    subject = 'Teacher Feedback'
    message = f'Преподаватель {teacher_first_name} {teacher_last_name} {teacher_patronymic} ' \
              f'проверил вашу работу. Ваша оценка {grage}. Ознакомьтесь с результатами.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student_email]

    send_mail(subject, message, from_email, recipient_list)
