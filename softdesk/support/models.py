from django.db import models
from django.conf import settings


class Project(models.Model):

    class Type(models.TextChoices):
        BACKEND = 'BackEnd'
        FRONTEND = 'FrontEnd'
        IOS = 'iOS'
        ANDROID = 'Android'


    title = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=Type.choices, max_length=10)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=4000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.DO_NOTHING,
                               related_name='project_author', null=True)
    
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          through='ProjectContributor',
                                          related_name='contribution')

    def __str__(self):
        return self.title

class ProjectContributor(models.Model):
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=True)
    project = models.ForeignKey('Project',
                                on_delete=models.CASCADE,
                                related_name='project')
    data = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('contributor', 'project')

    def __str__(self):
        return self.contributor.username

class Issue(models.Model):

    class Priority(models.TextChoices):
        LOW = 'L'
        MEDIUM = 'M'
        HIGH = 'H'
    

    class Status(models.TextChoices):
        TODO = 'ToDo'
        INPROGRESS = 'InProgress'
        FINISHED = 'Finished'


    class Tag(models.TextChoices):
        BUG = 'Bug'
        FEATURE = 'Feature'
        TASK = 'Task'


    title = models.CharField(max_length=255, verbose_name='title')
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    status = models.CharField(Status.choices, max_length=15)
    priority = models.CharField(Priority.choices, max_length=15)
    tag = models.CharField(Tag.choices, max_length=15)
    project = models.ForeignKey(Project,
                                null=True,
                                on_delete=models.CASCADE,
                                blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.DO_NOTHING,
                               related_name='issue_author', null=True)


class Comment(models.Model):
    title = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=4000)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.DO_NOTHING,
                               related_name='comment_author', null=True)

