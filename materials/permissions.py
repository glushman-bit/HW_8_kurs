from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """ Проверка, состоит ли пользователь в группе "moderators". """
    message = "Вы не состоите в группе 'moderators'."

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsNotModerator(BasePermission):
    """ Проверка, что пользователь не состоит в группе "moderators". """

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="moderators").exists()













# class IsModer(BasePermission):
#     """ Проверка, состоит ли пользователь в группе "moders". """
#     message = "Вы не состоите в группе Moders."
#
#     def has_permission(self, request, view):
#         return request.user.groups.filter(name='moders').exists()
#
#
# class IsNoModer(BasePermission):
#     """ Проверка, что пользователь не состоит в группе "moders". """
#
#     def has_permission(self, request, view):
#         return not request.user.groups.filter(name='moders').exists()
#
#
# class IsOwner(BasePermission):
#     """ Проверяет, является ли пользователь владельцем. """
#     message = "Вы не являетесь владельцем."
#
#     def has_object_permission(self, request, view, obj):
#         if obj.owner == request.user:
#             return True
#         return False
