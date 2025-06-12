from rest_framework.viewsets import ModelViewSet
from support.models import Project, ProjectContributor, Issue, Comment
from authentication.models import User
from support.serializers import (ProjectSerializer,
                                 ProjectDetailSerializer,
                                 ContributorSerializer,
                                 IssueSerializer,
                                 IssueDetailSerializer,
                                 CommentListSerializer,
                                 CommentDetailSerializer)
from authentication.serializers import UserListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from support.permissions import IsContributor
from rest_framework.decorators import action
from django.core.exceptions import PermissionDenied


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        """
        add a filter on contributor or author in querystring
        """
        if self.request.GET.get('contributor'):
            requested_contributor = self.request.GET.get('contributor')
            try:
                user = User.objects.get(username=requested_contributor)
                return Project.objects.filter(contributors=user)
            except User.DoesNotExist:
                return User.objects.filter(username=requested_contributor)
        if self.request.GET.get('author'):
            requested_author = self.request.GET.get('author')
            try:
                user = User.objects.get(username=requested_author)
                return Project.objects.filter(author=user)
            except User.DoesNotExist:
                return User.objects.filter(username=requested_author)
        return Project.objects.filter(active=True)

    def retrieve(self, request, *args, **kwargs):
        """
        check if requestor is in the project's contributor
        Raises exception or returns project detail
        """
        project = self.get_object()
        if request.user not in project.contributors.all():
            raise PermissionDenied()
        return Response(ProjectDetailSerializer(project).data)

    def partial_update(self, request, *args, **kwargs):
        """
        check if requestor is author
        then save changes and returns project details
        """
        project = self.get_object()
        if request.user != project.author:
            raise PermissionDenied()
        serialized = ProjectDetailSerializer(project,
                                             data=request.data,
                                             partial=True)
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

    @action(detail=True, methods=['patch'], permission_classes=[IsContributor])
    def contributor(self, request, pk):
        """
        Add a contributor to a project
        by creating a ProjectContributor's instance
        """
        # check if requestor is contributor
        if request.user not in Project.objects.get(id=pk).contributors.all():
            raise PermissionDenied()
        if request.data is None or 'contributor' not in request.data:
            response = {"detail": "Key error;`contributor` is expected"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        requested_contributor = request.data['contributor']
        # get the user's instance
        try:
            user = User.objects.get(username=requested_contributor)
            data = {'contributor': user.id, 'project': int(pk)}
            serializer = ContributorSerializer(data=data)
            project = Project.objects.get(id=pk)
            if serializer.is_valid():
                serializer.save()
                response = {"detail": f"User {user} "
                                      f"added to project '{project}'"}
                return Response(response, status=status.HTTP_202_ACCEPTED)
            response = {"detail": "This user is already contributing"}
            return Response(response, status=status.HTTP_226_IM_USED)
        except User.DoesNotExist:
            response = {"detail": "User doesn't exist"}
            return Response(response, status=status.HTTP_404_NOT_FOUND)


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
            if self.request.user not in Project.objects.get(
                    id=project_id).contributors.all():
                raise PermissionDenied()
            return Issue.objects.filter(project=project_id)
        projects = Project.objects.filter(
            contributors=self.request.user).values('id')
        # query on a list
        return Issue.objects.filter(project__in=projects)

    def partial_update(self, request, *args, **kwargs):
        """
        Check if requestor is author allows him to partial update
        change the author to assign issue
        """
        issue = self.get_object()
        if self.request.user != issue.author:
            raise PermissionDenied()
        serializer = IssueSerializer(issue,
                                     data=request.data,
                                     partial=True)
        if serializer.is_valid():
            if 'author' in request.data:
                try:
                    author = User.objects.get(username=request.data['author'])
                    serializer.save(author=author)
                except User.DoesNotExist:
                    response = {
                        "detail": "Requested author isn't a valid user"}
                    return Response(response, status=status.HTTP_404_NOT_FOUND)
            serializer.save()
            return Response(serializer.data)

        response = {"detail": "Data error"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def contributors(self, request, pk):
        """
        Check if requestor is contributor then returns the list
        of the contributors to the issue's project or raise unauthorized
        """
        issue = Issue.objects.get(id=pk)
        if (ProjectContributor.objects.
                filter(project=issue.project).
                filter(contributor=request.user)):
            return Response(UserListSerializer(
                issue.project.contributors.all(), many=True).data)
        else:
            raise PermissionDenied()

    def create(self, request, *args, **kwargs):
        if 'project' not in request.data:
            return Response("A project id is required",
                            status=status.HTTP_400_BAD_REQUEST)
        project = Project.objects.get(id=request.data['project'])
        serializer = IssueSerializer(data=request.data)
        if self.request.user not in project.contributors.all():
            response = {
                "detail": "Requestor isn't contributor for this project"
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid(raise_exception=True):
            issue = serializer.save(author=self.request.user)
            response = {
                "detail": f"Issue {issue.id} created for project {project}",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        """
        Returns only comments associated with issue where the requestor
        is project's contributor
        """
        if self.request.GET.get('issue'):
            issue_id = int(self.request.GET.get('issue'))
            project = Issue.objects.get(id=issue_id).project
            if self.request.user not in project.contributors.all():
                raise PermissionDenied()
            return Comment.objects.filter(issue=issue_id)
        # or returns those from projects where requestor is contributing
        projects = Project.objects.filter(
            contributors=self.request.user).values('id')
        issues = Issue.objects.filter(project__in=projects)
        return Comment.objects.filter(issue__in=issues)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        issue = Issue.objects.get(id=request.data['issue'])
        project = issue.project
        if issue.project.contributors.filter(username=request.user.username):
            serializer = CommentDetailSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user)
                response = {"detail": "comment created",
                            "data": serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)
        response = {"detail": f"{user} isn't contributor for '{project}'"}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        """
        check if requestor is author
        then save changes and returns project details
        """
        comment = self.get_object()
        if request.user != comment.author:
            raise PermissionDenied()
        serialized = CommentDetailSerializer(comment,
                                             data=request.data,
                                             partial=True)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return Response(serialized.data)
