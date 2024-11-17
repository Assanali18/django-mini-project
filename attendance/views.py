from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance
from .serializers import AttendanceSerializer, BulkAttendanceSerializer, BulkUpdateAttendanceSerializer
from users.permissions import IsTeacher, IsAdmin


class BaseAttendanceView:
    """
    Базовый класс для обработки фильтрации по ролям.
    """
    def get_queryset_by_role(self):
        user = self.request.user
        if user.role == 'student':
            return Attendance.objects.filter(student_id=user)
        elif user.role == 'teacher':
            return Attendance.objects.filter(teacher_id=user)
        elif user.role == 'admin':
            return Attendance.objects.all()
        return Attendance.objects.none()


class AttendanceListView(BaseAttendanceView, generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_queryset_by_role()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'teacher':
            raise PermissionError("Only teachers can mark attendance.")
        serializer.save()


class BulkAttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Attendance records created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceDetailView(BaseAttendanceView, generics.RetrieveUpdateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_queryset_by_role()

    def perform_update(self, serializer):
        user = self.request.user
        attendance = self.get_object()

        if user.role == 'student' and attendance.student_id != user:
            raise PermissionError("Students can only update their own attendance records.")

        if user.role == 'teacher' and attendance.course_id.teacher_id != user:
            raise PermissionError("Teachers can only update attendance for their own courses.")

        serializer.save()


class BulkUpdateAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def put(self, request):
        serializer = BulkUpdateAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            updated_records = serializer.update(serializer.validated_data)
            return Response(
                {"detail": f"{len(updated_records)} attendance records updated successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
