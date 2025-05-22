from django.contrib import admin
from support.models import Project, Issue, Comment, ProjectContributor


admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.comment.register(Comment, CommentAdmin)
admin.ProjectContributor.register(ProjectContributor, ProjectContributorAdmin)

