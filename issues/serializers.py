from rest_framework import serializers

from accounts.models import User
from .models import Category, Issue, IssueComment, IssueStatusHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]


class IssueSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    reported_by_email = serializers.EmailField(
        source='reported_by.email',
        read_only=True
    )

    assigned_to_email = serializers.EmailField(
        source='assigned_to.email',
        read_only=True
    )

    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'description',
            'category',
            'category_name',
            'reported_by',
            'reported_by_email',
            'assigned_to',
            'assigned_to_email',
            'status',
            'priority',
            'location_text',
            'latitude',
            'longitude',
            'image',
            'resolution_note',
            'resolved_at',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'reported_by',
            'reported_by_email',
            'assigned_to',
            'assigned_to_email',
            'status',
            'priority',
            'resolution_note',
            'resolved_at',
            'created_at',
            'updated_at',
        ]


class AssignIssueSerializer(serializers.Serializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.STAFF)
    )

    priority = serializers.ChoiceField(
        choices=Issue.Priority.choices,
        required=False
    )


class UpdateIssueStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Issue.Status.choices
    )

    resolution_note = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):
        status = attrs.get('status')
        resolution_note = attrs.get('resolution_note', '')

        if status == Issue.Status.RESOLVED and not resolution_note.strip():
            raise serializers.ValidationError(
                "Resolution note is required when marking issue as resolved."
            )

        return attrs


class IssueCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(
        source='author.email',
        read_only=True
    )

    author_role = serializers.CharField(
        source='author.role',
        read_only=True
    )

    class Meta:
        model = IssueComment
        fields = [
            'id',
            'issue',
            'author',
            'author_email',
            'author_role',
            'message',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'issue',
            'author',
            'author_email',
            'author_role',
            'created_at',
        ]


class IssueStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(
        source='changed_by.email',
        read_only=True
    )

    class Meta:
        model = IssueStatusHistory
        fields = [
            'id',
            'issue',
            'changed_by',
            'changed_by_email',
            'previous_status',
            'new_status',
            'note',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'issue',
            'changed_by',
            'changed_by_email',
            'previous_status',
            'new_status',
            'note',
            'created_at',
        ]