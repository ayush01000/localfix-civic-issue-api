from django.utils import timezone

from rest_framework import status as drf_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from accounts.models import User

from .models import Category, Issue, IssueComment, IssueStatusHistory
from .permissions import IsAdminRoleOrReadOnly, IsIssueOwnerOrStaffOrAdmin
from .serializers import (
    AssignIssueSerializer,
    CategorySerializer,
    IssueCommentSerializer,
    IssueSerializer,
    UpdateIssueStatusSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminRoleOrReadOnly]

    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['name']


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsIssueOwnerOrStaffOrAdmin]

    filterset_fields = [
        'status',
        'priority',
        'category',
    ]

    search_fields = [
        'title',
        'description',
        'location_text',
    ]

    ordering_fields = [
        'id',
        'created_at',
        'updated_at',
        'status',
        'priority',
    ]

    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        queryset = Issue.objects.select_related(
            'category',
            'reported_by',
            'assigned_to',
        )

        if user.role == User.Role.ADMIN:
            return queryset

        if user.role == User.Role.STAFF:
            return queryset.filter(assigned_to=user)

        return queryset.filter(reported_by=user)

    def perform_create(self, serializer):
        issue = serializer.save(reported_by=self.request.user)

        IssueStatusHistory.objects.create(
            issue=issue,
            changed_by=self.request.user,
            previous_status=None,
            new_status=issue.status,
            note='Issue reported by citizen.'
        )

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        issue = self.get_object()

        if request.user.role != User.Role.ADMIN:
            return Response(
                {"detail": "Only admin can assign issues."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        serializer = AssignIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = issue.status
        assigned_staff = serializer.validated_data['assigned_to']

        issue.assigned_to = assigned_staff
        issue.status = Issue.Status.ASSIGNED

        if 'priority' in serializer.validated_data:
            issue.priority = serializer.validated_data['priority']

        issue.save()

        IssueStatusHistory.objects.create(
            issue=issue,
            changed_by=request.user,
            previous_status=old_status,
            new_status=issue.status,
            note=f"Issue assigned to {assigned_staff.email}."
        )

        return Response(
            IssueSerializer(issue, context={'request': request}).data,
            status=drf_status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        issue = self.get_object()

        if request.user.role not in [User.Role.ADMIN, User.Role.STAFF]:
            return Response(
                {"detail": "Only staff or admin can update issue status."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        if request.user.role == User.Role.STAFF and issue.assigned_to != request.user:
            return Response(
                {"detail": "Staff can update only assigned issues."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        serializer = UpdateIssueStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = issue.status
        new_status = serializer.validated_data['status']
        resolution_note = serializer.validated_data.get('resolution_note', '')

        issue.status = new_status

        if resolution_note:
            issue.resolution_note = resolution_note

        if new_status == Issue.Status.RESOLVED:
            issue.resolved_at = timezone.now()

        issue.save()

        IssueStatusHistory.objects.create(
            issue=issue,
            changed_by=request.user,
            previous_status=old_status,
            new_status=new_status,
            note=resolution_note or f"Status changed from {old_status} to {new_status}."
        )

        return Response(
            IssueSerializer(issue, context={'request': request}).data,
            status=drf_status.HTTP_200_OK
        )

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        issue = self.get_object()

        if request.method == 'GET':
            comments = issue.comments.select_related('author')
            serializer = IssueCommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = IssueCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            issue=issue,
            author=request.user
        )

        return Response(
            IssueCommentSerializer(comment).data,
            status=drf_status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        issue = self.get_object()

        timeline_items = []

        status_history = issue.status_history.select_related('changed_by')
        comments = issue.comments.select_related('author')

        for item in status_history:
            timeline_items.append({
                "type": "status_change",
                "previous_status": item.previous_status,
                "new_status": item.new_status,
                "note": item.note,
                "by": item.changed_by.email if item.changed_by else None,
                "created_at": item.created_at,
            })

        for comment in comments:
            timeline_items.append({
                "type": "comment",
                "message": comment.message,
                "by": comment.author.email,
                "role": comment.author.role,
                "created_at": comment.created_at,
            })

        timeline_items.sort(key=lambda item: item["created_at"])

        return Response(timeline_items)