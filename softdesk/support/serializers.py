from rest_framework.serializers import (ModelSerializer,
                                        StringRelatedField,
                                        SlugRelatedField)
from support.models import Project, ProjectContributor, Issue, Comment


class ContributorSerializer(ModelSerializer):

    class Meta:
        model = ProjectContributor
        fields = ['contributor', 'project', 'data']


class ProjectSerializer(ModelSerializer):

    contributors = SlugRelatedField(many=True,
                                    read_only='True',
                                    slug_field='username')
    author = StringRelatedField(many=False)

    class Meta:
        model = Project
        fields = ['id', 'title', 'date_created', 'type', 'description', 'author',
                  'contributors']

class ProjectDetailSerializer(ModelSerializer):
    pass

class IssueSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['title', 'date_created', 'priority', 'tag', 'status', 'author']



