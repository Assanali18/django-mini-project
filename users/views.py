from rest_framework import generics
from rest_framework.permissions import AllowAny
from .permissions import IsAdmin
from .models import User
from .serializers import UserSerializer

import logging
from django.utils.timezone import now


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        logger = logging.getLogger('custom')
        logger.info(f"New user registered: {user.email} at {now()}")


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def list(self, request, *args, **kwargs):
        logger = logging.getLogger('custom')
        logger.info(f"Admin {request.user.email} requested user list.")
        return super().list(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


