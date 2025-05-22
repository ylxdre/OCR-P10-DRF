from django.db import models


class Project(models.Model):
    author = 
    contributor = 


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

    contributors = models.ManyToManyField(
            settings.AUTH_USER_MODEL, through='IssueContributors', related_name='contributors')
    assigned_to =  


class Comment(models.Model):
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)




class IssueContributors(models.Model):
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)
    issue = "ToDo"
