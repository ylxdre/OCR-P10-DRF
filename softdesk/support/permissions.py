from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, project):
        return bool(request.user
                    and request.user.is_authenticated
                    and request.user==project.author)