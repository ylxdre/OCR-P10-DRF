from django.db import models


class Project(models.Model):

    class Type(models.TextChoices):
        BACKEND = 'BackEnd'
        FRONTEND = 'FrontEnd'
        IOS = 'iOS'
        ANDROID = 'Android'


    title = models.CharField(length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=Type.choices, max_length=10)
    description = models.CharField(length=4000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='ProjectContributor', related_name='contributor')


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


    title = models.CharField(max_lenght=255, verbose_name='title')
    description = models.TextField()
    project = models.ForeignKey(Project, null=True, on_delete=models.SET_NULL, blank=True)
    status = models.CharField(Status.choices, max_length=15)
    priority = models.CharField(Priority.choices, max_lenght=15)
    tag = models.CharField(Tag.choices, max_length=15)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    contributors = models.ManyToManyField(
            settings.AUTH_USER_MODEL, through='IssueContributors', related_name='contributors')


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=DO_NOTHING)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)


class ProjectContributors(models.Model):
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    data = models.CharField(max_length=255, blank=True)

