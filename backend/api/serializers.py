from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from assignment.models import (
    Assignment,
    StudentSolution,
    TeacherFeedback,
)
from django.utils import timezone


User = get_user_model()

# --------------USERS---------


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "patronymic",
            "is_teacher",
            "group",
            "email",
        )


# class UserFullInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = "__all__"


class TokenSerializer(serializers.ModelSerializer):
    # source="key" означает, что в таблице token будет заполнено key
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ("token",)


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        label="Текущий пароль",
        required=True
    )
    new_password = serializers.CharField(
        label="Новый пароль",
        required=True
    )
    confirm_password = serializers.CharField(
        label="Повторите новый пароль",
        required=True,
    )

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        new_password, confirm_password = validated_data['new_password'], validated_data['confirm_password']
        if not instance.check_password(validated_data['current_password'] and new_password == confirm_password):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
                == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


# ----------END_USERS---------

# ----------ASSIGNMENT-------


class ShowAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class StudentSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSolution
        fields = (
            "report_file",
            "diary_practices",
        )


class StudentsListSolutionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSolution
        fields = "__all__"


class TeacherFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherFeedback
        fields = (
            "feedback_file",
            "comment",
            "grade",
        )


class CreateAssignmentSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "title",
            "description",
            "deadline",
            "sample_document_report",
            "sample_document_diary_practices",
            "teacher",
        )

    def validate(self, data):
        required_fields = [
            'title',
            'deadline',
        ]
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f'{field} - Обязательное поле.')

        deadline = data.get('deadline')
        if deadline and deadline < timezone.now():
            raise serializers.ValidationError('Выбранное время не может быть прошедшим.')

        return data

    @transaction.atomic
    def create(self, validated_data):
        assignment = Assignment.objects.create(
            teacher=self.context['request'].user,
            **validated_data)
        return assignment

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.description = validated_data.get('description', instance.description)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.sample_document_report = validated_data.get(
            'sample_document_report', instance.sample_document_report
        )
        instance.sample_document_diary_practices = validated_data.get(
            'sample_document_diary_practices', instance.sample_document_diary_practices
        )
        instance.save()
        return instance


# ------END_ASSIGNMENT-------
