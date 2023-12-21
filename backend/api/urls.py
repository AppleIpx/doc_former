from django.conf.urls.static import static
from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from doc_former import settings
from . import views

router = DefaultRouter()
router.register(r'users', views.UserView, basename="users")
router.register(r'assignments', views.AssignmentView, basename="users")

urlpatterns = [
    path(r'auth/', include('djoser.urls.authtoken')),
    path("assignments/<int:id>/download_assignment/",
         views.DownloadFileView.as_view(), name="download"),

    # загрузка решений студента
    path('assignments/<int:pk>/loading_solution/',
         views.StudentSolutionView.as_view(), name='load_student-solution'),

    # students_solutions для просмотра всех отправленных решений учителю,
    path("assignments/<int:id>/students_solutions/",
         views.StudentsListSolutionsView.as_view({'get': 'list'}), name="students_solutions"),

    # для просмотра решения и фидбека конкретного студента
    path('assignments/<int:assignment_pk>/student_solution/<int:student_pk>/',
         views.AssignmentSolutionFeedbackView.as_view(), name="assignment-solution_info"),

    # отправка решения конкретному студенту
    path('assignments/<int:assignment_pk>/student_solution/<int:student_pk>/feedback/',
         views.TeacherFeedbackView.as_view(), name='teacher-feedback'),

    # path('assignments/<int:pk>/feedback/', views.TeacherFeedbackView.as_view(), name='teacher-feedback'),
    path("", include(router.urls)),
] + (static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))