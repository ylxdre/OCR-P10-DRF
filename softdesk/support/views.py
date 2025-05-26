from django.shortcuts import render
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.viewsets import ModelViewSet
from support.models import Project, ProjectContributor, Issue, Comment
from authentication.models import User
from support.serializers import ProjectSerializer, ContributorSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from support.permissions import IsAuthor
from rest_framework.decorators import action


class ProjectViewSet(ModelViewSet):
    permission_classes=[IsAuthenticatedOrReadOnly]

    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(active=True)

    def perform_create(self, serializer):
        """set authenticated user as author and contributor on creation"""
        test = serializer.save(author=self.request.user)
        data = {'contributor': self.request.user.id, 'project': test.id}
        contributor_serializer = ContributorSerializer(data=data)
        if contributor_serializer.is_valid():
            contributor_serializer.save()

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthor],
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
    serializer =