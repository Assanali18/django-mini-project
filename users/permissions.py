from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """
    Разрешение для преподавателей.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Преподаватели могут изменять данные, остальные только читать.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsCourseOwner(permissions.BasePermission):
    """
    Разрешение для владельцев курса (преподавателей, которые создали курс).
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.teacher == request.user


class IsAdmin(permissions.BasePermission):
    """
    Полный доступ для администраторов.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
