from django.contrib import admin
from django.contrib.admin import register
from .models import (
    Assignment,
    StudentSolution,
    TeacherFeedback,
)


@register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    readonly_fields = ('pub_date',)
    fields = (
        "title",
        "description",
        "pub_date",
        "deadline",
        "sample_document_report",
        "sample_document_diary_practices",
        "teacher",
        # "solution_file",
        # "feedback_file",
        # "grade",
        # "comment",
    )
    list_display = (
        "pk",
        "title",
        "description",
        "deadline",
        "teacher",
    )


@register(StudentSolution)
class StudentSolutionAdmin(admin.ModelAdmin):
    readonly_fields = ('submission_date',)
    fields = (
        "assignment",
        "student",
        "report_file",
        "diary_practices",
        "submission_date",
    )
    list_display = (
        "pk",
        "assignment",
        "submission_date",
    )


@register(TeacherFeedback)
class TeacherFeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ('submission_date',)
    fields = (
        "assignment",
        "grade",
        "student",
        "comment",
        "feedback_file",
        "submission_date",
    )
    list_display = (
        "pk",
        "assignment",
        "student",
        "grade",
        "submission_date",
    )
