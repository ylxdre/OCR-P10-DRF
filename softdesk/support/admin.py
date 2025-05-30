from django.contrib import admin
from support.models import Project, Issue, Comment, ProjectContributor
from authentication.models import User

class AdminProject(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'contributors')

    @admin.display(description='contributors')
    def contributors(self, obj):
        return obj.contributor

class AdminIssue(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'project')


admin.site.register(User)
admin.site.register(Project, AdminProject)
admin.site.register(Issue, AdminIssue)
admin.site.register(Comment)
admin.site.register(ProjectContributor)

