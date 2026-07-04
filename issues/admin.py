from django.contrib import admin

from .models import Category, Issue


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'reported_by',
        'assigned_to',
        'status',
        'priority',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'category',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'location_text',
        'reported_by__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )