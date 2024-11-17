from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from users.permissions import IsTeacher, IsTeacherOrReadOnly, IsCourseOwner, IsAdmin


class CourseListView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['teacher_id']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']


def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Course.objects.filter(enrollments__student=user)
        elif user.role == 'teacher':
            return Course.objects.filter(teacher=user)
        elif user.role == 'admin':
            return Course.objects.all()
        else:
            return Course.objects.none()


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher | IsAdmin]

    def perform_update(self, serializer):
        serializer.save()


class EnrollmentView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
