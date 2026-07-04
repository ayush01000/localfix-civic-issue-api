from rest_framework import serializers

from .models import Category, Issue


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