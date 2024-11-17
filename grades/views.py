from rest_framework import generics, permissions
from .models import Grade
from .serializers import GradeSerializer
from users.permissions import IsTeacher, IsAdmin


class BaseGradeView:
    """
    Базовый класс для обработки фильтрации по ролям.
    """
    def get_queryset_by_role(self):
        user = self.request.user
        if user.role == 'student':
            return Grade.objects.filter(student_id=user)
        elif user.role == 'teacher':
            return Grade.objects.filter(teacher_id=user)
        elif user.role == 'admin':
            return Grade.objects.all()
        return Grade.objects.none()


class GradeListView(BaseGradeView, generics.ListCreateAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_queryset_by_role()


class GradeDetailView(BaseGradeView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher | IsAdmin]

    def get_queryset(self):
        return self.get_queryset_by_role()
