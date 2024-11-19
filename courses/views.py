from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from users.permissions import IsTeacher, IsAdmin
from django.core.cache import cache
import logging


class CourseListView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['teacher_id', 'created_at']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']

    def get_queryset(self):
        user = self.request.user
        cache_key = f'courses_{user.id}'
        cached_data = cache.get(cache_key)
        logger = logging.getLogger('custom')

        if cached_data:
            logger.info(f"Cache hit for user {user.email} - courses")
            return Course.objects.filter(id__in=[item['id'] for item in cached_data])

        logger.info(f"Cache miss for user {user.email} - loading courses from DB")
        queryset = super().get_queryset()
        serialized_data = CourseSerializer(queryset, many=True).data
        cache.set(cache_key, serialized_data, timeout=300)
        return queryset


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher | IsAdmin]

    def perform_update(self, serializer):
        serializer.save()
        cache.delete_pattern('courses_*')


class EnrollmentView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        enrollment = serializer.save()
        logger = logging.getLogger('custom')
        logger.info(f"User {self.request.user.email} enrolled in course {enrollment.course_id.name}")
