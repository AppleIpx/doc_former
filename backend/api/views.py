import os
import tempfile
import zipfile

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import RetrieveUpdateAPIView
from .tasks import (
    notify_teacher_about_solution,
    notify_student_about_feedback,
)
from rest_framework.views import APIView
from rest_framework import viewsets, status, generics
from users.models import User
from assignment.models import (
    Assignment,
    StudentSolution,
    TeacherFeedback,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from docxtpl import DocxTemplate
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.http import (
    HttpResponseServerError,
    HttpResponse,
    Http404,
)
from .serializers import (
    UserSerializer,
    SetPasswordSerializer,
    ShowAssignmentSerializer,
    CreateAssignmentSerializer,
    StudentSolutionSerializer,
    TeacherFeedbackSerializer,
    StudentsListSolutionsSerializer,
)
from users.permissions import (
    IsStudent,
    IsTeacher,
)

# ---------------USERS---------------------


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(is_teacher=False)

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsTeacher,))
    def users_list(self, request, *args, **kwargs):
        students = User.objects.filter(is_teacher=False)
        student_data = []

        for student in students:
            has_solution = StudentSolution.objects.filter(student=student).exists()
            has_feedback = TeacherFeedback.objects.filter(student=student).exists()

            data = {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'patronymic': student.patronymic,
                'group': student.group,
                'email': student.email,
                'has_solution': has_solution,
                'has_feedback': has_feedback,
            }

            if has_solution and has_feedback:
                feedback = TeacherFeedback.objects.get(student=student)
                data['grade'] = feedback.grade

            student_data.append(data)

        return Response(student_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        if "password" in self.request.data:
            password = make_password(self.request.data["password"])
            serializer.save(password=password)
        else:
            serializer.save()

    @action(
        ["post"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)


# -----------END_USERS---------------------


# ------------------ASSIGNMENT----------------
"""Просмотр заданий"""
class AssignmentView(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    permission_classes = [AllowAny, ]
    pagination_class = None

    def get_serializer_class(self):
        method = self.request.method
        if method == "POST" or method == "PATCH":
            return CreateAssignmentSerializer
        return ShowAssignmentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


"""показ всех присланных решений студентов отфильтрованные по новизне и дате"""
class StudentsListSolutionsView(viewsets.ModelViewSet):
    queryset = StudentSolution.objects.all()
    serializer_class = StudentsListSolutionsSerializer
    permission_classes = [IsTeacher, ]
    pagination_class = None

    # def get_queryset(self):
    #     return StudentSolution.objects.all()

    def list(self, request, *args, **kwargs):
        solutions = self.get_queryset()
        feedbacks = TeacherFeedback.objects.filter(student__in=solutions.values('student'))
        newer_solution_ids = []
        for solution in solutions:
            student_feedbacks = feedbacks.filter(student=solution.student)
            if not student_feedbacks:
                newer_solution_ids.append(solution.id)
                continue
            for feedback in student_feedbacks:
                if feedback.submission_date < solution.submission_date:
                    newer_solution_ids.append(solution.id)
        queryset = solutions.filter(id__in=newer_solution_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


"""просмотр решения и фидбэка"""
class AssignmentSolutionFeedbackView(APIView):
    queryset_assignment = Assignment.objects.all()
    queryset_solution = StudentSolution.objects.all()
    queryset_feedback = TeacherFeedback.objects.all()
    permission_classes = [IsAuthenticated, ]

    def get(self, request, assignment_pk, student_pk, **kwargs):
        try:
            assignment = self.queryset_assignment.get(id=assignment_pk)
        except Assignment.DoesNotExist:
            raise Http404("Задание не было найдено")

        user_id = request.user.id
        if request.user.is_teacher or user_id == int(student_pk):

            solutions = self.queryset_solution.filter(assignment=assignment, student=student_pk)
            feedbacks = self.queryset_feedback.filter(assignment=assignment, student=student_pk)

            if not solutions.exists() and not feedbacks.exists():
                assignment_serializer = ShowAssignmentSerializer(assignment)
                data = {'assignment': assignment_serializer.data}
                return Response(data)

            assignment_serializer = ShowAssignmentSerializer(assignment)
            solution_serializer = StudentSolutionSerializer(solutions, many=True)
            feedback_serializer = TeacherFeedbackSerializer(feedbacks, many=True)

            data = {
                'assignment': assignment_serializer.data,
                'solutions': solution_serializer.data,
                'feedbacks': feedback_serializer.data,
            }
            return Response(data)
        else:
            return Response({"detail": "Недостаточно прав для доступа к этим данным."},
                            status=status.HTTP_403_FORBIDDEN)


"""скачка файла"""
class DownloadFileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        user = get_object_or_404(User, id=request.user.id)
        assignment = get_object_or_404(Assignment, pk=id)
        try:
            temp_dir = tempfile.mkdtemp()

            # Отчет
            report_filepath = f"media/{assignment.sample_document_report}"
            if os.path.exists(report_filepath):
                doc_report = DocxTemplate(report_filepath)
                context_report = {
                    'faculty': user.faculty,
                    "direction": user.direction_specialty,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "input_supervisor": assignment.teacher,
                }
                doc_report.render(context_report)

                report_filename = os.path.join(temp_dir, "Отчет.docx")
                doc_report.save(report_filename)
            else:
                return HttpResponseServerError("File not found: sample_document_report")

            # Дневник практики
            diary_filepath = f"media/{assignment.sample_document_diary_practices}"
            if os.path.exists(diary_filepath):
                doc_diary_practices = DocxTemplate(diary_filepath)
                context_diary_practices = {
                    "course": user.course,
                    "group": user.group,
                    "direction": user.direction_specialty,
                    "last_name": user.last_name,
                    "first_name": user.first_name,
                    "faculty": user.faculty,
                    "input_supervisor": assignment.teacher,
                }
                doc_diary_practices.render(context_diary_practices)

                diary_filename = os.path.join(temp_dir, "Дневник практики.docx")
                doc_diary_practices.save(diary_filename)
            else:
                return HttpResponseServerError("File not found: sample_document_diary_practices")

            # Создание zip файла
            zip_filename = os.path.join(temp_dir, "documents.zip")
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                zip_file.write(report_filename, "Отчет.docx")
                zip_file.write(diary_filename, "Дневник практики.docx")

            # Создание запроса zip файла
            with open(zip_filename, 'rb') as zip_file:
                response = HttpResponse(zip_file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename=documents.zip'

            return response

        except Exception as e:
            print(f"Error: {e}")
            return HttpResponseServerError("Internal Server Error")


"""отправка решения"""
class StudentSolutionView(generics.CreateAPIView):
    serializer_class = StudentSolutionSerializer
    permission_classes = [IsStudent, ]

    def create(self, request, *args, **kwargs):
        if 'report_file' not in request.data:
            return Response(
                {'error': 'Отсутствует файл отчета'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif "diary_practices" not in request.data:
            return Response(
                {'error': 'Отсутствует файл дневника практики'},
                status=status.HTTP_400_BAD_REQUEST
            )

        assignment_id = self.kwargs.get('pk')
        student = self.request.user
        report_file = request.data['report_file']
        diary_practices = request.data['diary_practices']

        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {'error': 'Assignment с указанным ID не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )

        teacher = assignment.teacher
        teacher_email = teacher.email

        student_solution = StudentSolution(
            assignment=assignment,
            student=student,
            report_file=report_file,
            diary_practices=diary_practices,
        )
        student_solution.save()

        notify_teacher_about_solution.delay(
            student.first_name, student.last_name,
            student.patronymic, teacher_email
        )
        return Response({'success': 'Решение успешно отправлено'}, status=status.HTTP_201_CREATED)

    # Проверка типа файла (если необходимо)
            # solution_file = request.data['solution_file']
            # if not solution_file.content_type.startswith('application/pdf'):
            #     return Response({'error': 'Invalid file type. Only PDF files are allowed.'},
            #                     status=status.HTTP_400_BAD_REQUEST)


"""отправка фидбэка"""
class TeacherFeedbackView(generics.CreateAPIView):
    serializer_class = TeacherFeedbackSerializer
    permission_classes = [IsTeacher, ]

    def create(self, request, *args, **kwargs):
        if 'feedback_file' not in request.data:
            return Response(
                {'error': 'Отсутствует файл отзыва'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if "grade" not in request.data:
            return Response(
                {'error': 'Отсутствует оценка'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            student = User.objects.get(id=kwargs.get("student_pk"))
            assignment = Assignment.objects.get(id=kwargs.get("assignment_pk"))

        except StudentSolution.DoesNotExist:
            return Response(
                {'error': 'Assignment с указанным ID не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        feedback_file = request.data['feedback_file']
        grade = request.data['grade']
        comment = request.data['comment']

        teacher_feedback = TeacherFeedback(
            assignment=assignment,
            student=student,
            grade=grade,
            comment=comment,
            feedback_file=feedback_file
        )
        teacher_feedback.save()

        # student_email = student.email
        student_email = "alex.petr2410@mail.ru"
        teacher = self.request.user

        notify_student_about_feedback.delay(
            teacher.first_name, teacher.last_name,
            teacher.patronymic, student_email, grade
        )

        # for email in student_email:
        #     notify_student_about_feedback.delay(
        #         teacher.first_name, teacher.last_name,
        #         teacher.patronymic, email, grade
        #     )

        return Response({'success': 'Отзыв успешно создан'}, status=status.HTTP_201_CREATED)


# ------------- END_ASSIGNMENT----------------
