from django.contrib import admin
from support.models import Project, Issue, Comment, Contributor
from authentication.models import User

class AdminUser:
    pass

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comment)
admin.site.register(Contributor)

