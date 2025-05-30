from rest_framework.serializers import (ModelSerializer,
                                        StringRelatedField,
                                        SlugRelatedField,
                                        SerializerMethodField,
                                        ValidationError)
from support.models import Project, ProjectContributor, Issue, Comment


class ContributorSerializer(ModelSerializer):

    class Meta:
        model = ProjectContributor
        fields = ['contributor', 'project', 'data']


class ContributorListSerializer(ModelSerializer):

    class Meta:
        model = ProjectContributor
        fields = ['contributor']



class ProjectSerializer(ModelSerializer):

    author = StringRelatedField(many=False)
    contributors = SlugRelatedField(many=True,
                                    read_only='True',
                                    slug_field='username')
    class Meta:
        model = Project
        fields = ['id', 'author', 'contributors', 'title', 'type', 'date_created']

    def validate_title(self, value):
        if Project.objects.filter(title=value).exists():
            raise ValidationError("Project already exists.")
        return value

class ProjectDetailSerializer(ModelSerializer):

    contributors = SlugRelatedField(many=True,
                                    read_only='True',
                                    slug_field='username')
    author = StringRelatedField(many=False)
    issues = SerializerMethodField()

    class Meta:
        model = Project
        fields = ['title',
                  'date_created', 'type',
                  'author', 'contributors', 'description', 'issues']

    def get_issues(self, instance):
        queryset = Issue.objects.filter(project=instance.pk)
        serializer = IssueSerializer(queryset, many=True)
        return serializer.data


class IssueSerializer(ModelSerializer):

    author = StringRelatedField(many=False)


    class Meta:
        model = Issue
        fields = ['id', 'title', 'project', 'date_created', 'priority',
                  'tag', 'status', 'author']
        read_only_field = ['author']


    def validate_author(self, data):
        if Project.objects.filter(contributors=data.author).exists():
            raise ValidationError("Requestor isn't contributor")
        return data

    def validate_project(self, data):
    #    if data['user'] not in data['project'].contributors:
    #        raise ValidationError("User must be a contributor to the project")
        #print(data.project)
        #if self.context['request'].user not in data.contributors:
        #    raise ValidationError("User must be a contributor to the project")
        #print(self.get_contributors(data))

        return data


class CommentListSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['title', 'date_created', 'author']

class CommentDetailSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['title', 'date_created', 'author', 'description']