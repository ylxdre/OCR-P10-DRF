from rest_framework.permissions import BasePermission
from support.models import Project

class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, object):
        return bool(request.user
                    and request.user.is_authenticated
                    and request.user == object.author
                    )


class IsContributor(BasePermission):

    def has_object_permission(self, request, view, object):
        return bool(request.user
                    and request.user.is_authenticated
                    and request.user in object.contributors.all()
                    )