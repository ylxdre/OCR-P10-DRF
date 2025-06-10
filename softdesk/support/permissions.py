from rest_framework.permissions import BasePermission

class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, object):
        return bool(request.user
                    and request.user.is_authenticated
                    and request.user == object.author
                    )


class IsContributor(BasePermission):

    def has_object_permission(self, request, view, object):
        print(object.contributors.all())
        return bool(request.user.is_authenticated
                    and request.user in object.contributors.all()
                    )
