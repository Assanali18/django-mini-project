from rest_framework import serializers

from users.models import User
from .models import Course, Enrollment


class CourseSerializer(serializers.ModelSerializer):
    teacher_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'))

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'teacher_id', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    student_id = serializers.StringRelatedField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course_id', 'student_id', 'enrollment_date']
        read_only_fields = ['student_id', 'enrollment_date']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is missing.")

        student = request.user
        course = validated_data['course_id']

        if Enrollment.objects.filter(student_id=student, course_id=course).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")

        validated_data['student_id'] = student
        return super().create(validated_data)