from django.core.cache import cache
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsAdmin

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

import logging
logger = logging.getLogger(__name__)


class StudentListView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['registration_date']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'id']


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')
        cache_key = f'student_profile_{student_id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Данные из кэша для студента {student_id}")
            return Response(cached_data)

        logger.info(f"Кэш отсутствует. Загружаем из базы для студента {student_id}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
    def update(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')
        cache_key = f'student_profile_{student_id}'
        cache.delete(cache_key)

        return super().update(request, *args, **kwargs)
