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

    contributor = StringRelatedField(many=False)

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
        fields = ['id',
                  'author',
                  'contributors',
                  'title',
                  'type',
                  'date_created']

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


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'title']


class IssueSerializer(ModelSerializer):
    author = StringRelatedField(many=False)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'project', 'date_created', 'priority',
                  'tag', 'status', 'author']


class IssueDetailSerializer(ModelSerializer):
    comments = SerializerMethodField()
    author = StringRelatedField(many=False)

    class Meta:
        model = Issue
        fields = ['title', 'project', 'date_created', 'priority',
                  'tag', 'status', 'author', 'comments']

    def get_comments(self, instance):
        queryset = Comment.objects.filter(issue=instance.id)
        serializer = CommentListSerializer(queryset, many=True)
        return serializer.data


class CommentListSerializer(ModelSerializer):
    issue = IssueListSerializer(many=False)
    author = StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = ['id', 'title', 'date_created', 'author', 'issue']


class CommentDetailSerializer(ModelSerializer):
    author = StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = ['title', 'date_created', 'description', 'issue', 'author']
