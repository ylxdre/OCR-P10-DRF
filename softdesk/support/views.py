from django.contrib.auth.checks import check_models_permissions
from django.shortcuts import render
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from support.models import Project, ProjectContributor, Issue, Comment
from authentication.models import User
from support.serializers import (ProjectSerializer,
                                 ProjectDetailSerializer,
                                 ContributorSerializer,
                                 ContributorListSerializer,
                                 IssueSerializer,
                                 IssueDetailSerializer,
                                 CommentListSerializer,
                                 CommentDetailSerializer)
from authentication.serializers import UserListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from support.permissions import IsAuthor, IsContributor
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.core.exceptions import PermissionDenied


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer

    queryset = Project.objects.filter(active=True)


    def retrieve(self, request, pk, *args, **kwargs):
        """
        check if requestor is in the project's contributor
        Raises exception or returns project detail
        """
        if not request.user in Project.objects.get(id=pk).contributors.all():
            raise PermissionDenied()
        queryset = Project.objects.get(id=pk)
        return Response(ProjectDetailSerializer(queryset).data)

    def partial_update(self, request, pk, *args, **kwargs):
        """
        check if requestor is author
        then save changes and returns project details
        """
        if not request.user == Project.objects.get(id=pk).author:
            raise PermissionDenied()
        queryset = Project.objects.get(id=pk)
        serialized = ProjectDetailSerializer(queryset, data=request.data, partial=True)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return Response(serialized.data)


    def perform_create(self, serializer):
        """set authenticated user as author and contributor on creation"""
        test = serializer.save(author=self.request.user)
        data = {'contributor': self.request.user.id, 'project': test.id}
        contributor_serializer = ContributorSerializer(data=data)
        if contributor_serializer.is_valid():
            contributor_serializer.save()


    @action(detail=True, methods=['get'], permission_classes=[IsContributor])
    def test(self, request, pk):
        """only for testing purpose, should be deleted not published"""
        if not request.user in Project.objects.get(id=pk).contributors.all():
            raise PermissionDenied()
        return Response("OK")

    @action(detail=True, methods=['patch'], permission_classes=[IsContributor])
    def contributor(self, request, pk):
        """Add a contributor to a project
        by creating a ProjectContributor's instance
        """
        #check if requestor is contributor
        if not request.user in Project.objects.get(id=pk).contributors.all():
            raise PermissionDenied()

        if request.data is None or not 'contributor' in request.data:
            return Response(f"Key error;`contributor` is expected",
                            status=status.HTTP_400_BAD_REQUEST)
        #get the user's instance
        contributor = User.objects.get(username=request.data['contributor'])
        data = {'contributor': contributor.id, 'project': int(pk)}
        serializer = ContributorSerializer(data=data)
        project = Project.objects.get(id=pk)
        if serializer.is_valid():
            serializer.save()
            return Response(f"User {contributor} "
                            f"added to project {project}",
                            status=status.HTTP_202_ACCEPTED)
        return Response("This user is already contributing",
                        status=status.HTTP_226_IM_USED)



class IssueViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()


    def get_queryset(self):
        """
        returns only the issues related to projects
        where requestor is contributor or empty list
        """
        if self.request.GET.get('project'):
            project_id = int(self.request.GET.get('project'))
            if not self.request.user in Project.objects.get(
                    id=project_id).contributors.all():
                raise PermissionDenied()
            return Issue.objects.filter(project=project_id)
        projects = Project.objects.filter(contributors=self.request.user).values('id')
        #query on a list
        return Issue.objects.filter(project__in=projects)


    def perform_update(self, serializer):
        if self.request.user == serializer.author:
            return Response("OK")
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=author)
            return Response(serializer.data)
        return Response("Data error", status=status.HTTP_400_BAD_REQUEST)



    @action(detail=True, methods=['get'])
    def contributors(self, request, pk):
        """
        check if requestor is contributor then returns the list
        of the contributors to the issue's project or raise unauthorized
        """
        issue = Issue.objects.get(id=pk)
        if ProjectContributor.objects.filter(project=issue.project).filter(contributor=request.user):
            return Response(UserListSerializer(issue.project.contributors.all(), many=True).data)
        else:
            raise PermissionDenied()


    def create(self, request, *args, **kwargs):
        if not 'project' in request.data:
            return Response("Need project")
        project = Project.objects.get(id=request.data['project'])
        serializer = IssueSerializer(data=request.data)
        if self.request.user not in project.contributors.all():
            return Response("Requestor isn't contributor for this project",
                            status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=self.request.user)
            response = {
                "message": f"Issue created for project {project}",
                "data": serializer.data
            }
            return Response(response, status = status.HTTP_201_CREATED)

    #def perform_create(self, serializer):
    #    """set authenticated user as author and contributor on creation"""
    #    serializer.save(author=self.request.user)


class ContributorViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = ContributorSerializer
    queryset = ProjectContributor.objects.all()

    def get_queryset(self):
        if self.request.GET.get('project'):
            serializer_class = ContributorListSerializer
            return (ProjectContributor.objects.
                    filter(project=self.request.GET.get('project')))
        elif self.request.GET.get('user'):
            user_id = User.objects.get(username=self.request.GET.get('user')).id
            return (ProjectContributor.objects.
                    filter(contributor=user_id))
        return self.queryset


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer

    queryset = Comment.objects.all()

    def get_queryset(self):
        """returns only comments associated with issue where the requestor
        is project's contributor
        """
        if self.request.GET.get('issue'):
            issue_id = int(self.request.GET.get('issue'))
            print(issue_id, type(issue_id))
            project = Issue.objects.get(id=issue_id).project
            if not self.request.user in Issue.objects.get(
                    id=issue_id).project.contributors.all():
                raise PermissionDenied()
            return Comment.objects.filter(issue=issue_id)
        if self.request.data:
            return Comment.objects.filter(issue=self.request.data['issue'])



    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()



    def create(self, request, *args, **kwargs):
        user = request.user
        issue = Issue.objects.get(id=request.data['issue'])
        project = issue.project
        if issue.project.contributors.filter(username=request.user.username):
            serializer = CommentDetailSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                #serializer.author = request.user.username
                serializer.save(author=request.user.username)
                response = {"message": "comment created",
                            "data": serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)
        return Response("Not allowed; "
                        f"{user} isn't contributor for project {project}",
                        status=status.HTTP_403_FORBIDDEN)