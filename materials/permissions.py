from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверка, состоит ли пользователь в группе "moderators"."""

    message = "Вы не состоите в группе 'moderators'."

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """Проверка, что пользователь является владельцем."""

    message = "Вы не являетесь владельцем."

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
