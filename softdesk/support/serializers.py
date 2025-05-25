from rest_framework.serializers import ModelSerializer
from support.models import Project, Contributor, Issue, Comment


class ProjectSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'date_created', 'type', 'description', 'author',
                  'contributors']


class ContributorSerialier(ModelSerializer):

    class Meta:
        model = Contributor
        Fields = ['']