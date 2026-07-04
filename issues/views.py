from rest_framework import viewsets

from accounts.models import User

from .models import Category, Issue
from .permissions import IsAdminRoleOrReadOnly, IsIssueOwnerOrStaffOrAdmin
from .serializers import CategorySerializer, IssueSerializer


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
        serializer.save(reported_by=self.request.user)