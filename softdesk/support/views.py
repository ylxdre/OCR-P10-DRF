from django.shortcuts import render
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.viewsets import ModelViewSet
from support.models import Project, ProjectContributor, Issue, Comment
from authentication.models import User
from support.serializers import (ProjectSerializer,
                                 ProjectDetailSerializer,
                                 ContributorSerializer,
                                 IssueSerializer,
                                 CommentListSerializer,
                                 CommentDetailSerializer)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from support.permissions import IsAuthor, IsContributor
from rest_framework.decorators import action


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer

    queryset = Project.objects.filter(active=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """set authenticated user as author and contributor on creation"""
        test = serializer.save(author=self.request.user)
        data = {'contributor': self.request.user.id, 'project': test.id}
        contributor_serializer = ContributorSerializer(data=data)
        if contributor_serializer.is_valid():
            contributor_serializer.save()

    @action(detail=True, methods=['patch'],
            permission_classes=[IsContributor],
            basename='add_contributor')
    def add_contributor(self, request, pk):
        """Create the user/project contributor's relation"""
        if 'contributor' in request.data:
            contributor = User.objects.get(username=request.data['contributor'])
            data = {'contributor': contributor.id, 'project': pk}
            serializer = ContributorSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(f"User {contributor} added",
                                status=status.HTTP_202_ACCEPTED)
            return Response("This user is already contributing",
                            status=status.HTTP_226_IM_USED)
        return Response(f"Key error;`contributor` is expected, "
                        f"not `{list(request.data)[0]}`",
                        status=status.HTTP_400_BAD_REQUEST)


class IssueViewSet(ModelViewSet):
    permission_classes = [IsContributor]

    serializer_class = IssueSerializer


    def get_queryset(self):
        project_id = int(self.request.GET.get('project'))
        project = Project.objects.get(id=project_id)
        self.check_object_permissions(self.request, project)
        return Issue.objects.filter(project=project_id)


    def get_contributors(self, project):
        queryset = ProjectContributor.objects.filter(project=project)
        contributors_serializer = ContributorSerializer(queryset, many=True)
        return contributors_serializer.data


    def create(self, request, *args, **kwargs):
        print(request.data['project'])
        project = Project.objects.get(id=request.data['project'])
        serializer = IssueSerializer(data=request.data)


        print(request.data['project'], type(request.data['project']))
        print(self.get_contributors(request.data['project']))

        if self.request.user in project.contributors:
            if serializer.is_valid(raise_exception=True):
                serializer.author = self.request.user
                serializer.save()
                response = {
                    "message": f"Issue created for project {project}",
                    "data": serializer.data
                }
                return Response(response, status = status.HTTP_201_CREATED)

    #def perform_create(self, serializer):
    #    """set authenticated user as author and contributor on creation"""
    #    serializer.save(author=self.request.user)


class ContributorViewSet(ModelViewSet):
    serializer_class = ContributorSerializer
    queryset = ProjectContributor.objects.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer

    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()
