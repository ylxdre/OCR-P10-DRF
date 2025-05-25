from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from support.models import Project, Contributor, Issue, Comment
from support.serializers import ProjectSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()