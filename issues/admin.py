from django.contrib import admin

from .models import Category, Issue, IssueComment, IssueStatusHistory


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
        'assigned_to__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'issue',
        'author',
        'created_at',
    )

    search_fields = (
        'issue__title',
        'author__email',
        'message',
    )

    list_filter = ('created_at',)


@admin.register(IssueStatusHistory)
class IssueStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'issue',
        'changed_by',
        'previous_status',
        'new_status',
        'created_at',
    )

    search_fields = (
        'issue__title',
        'changed_by__email',
        'note',
    )

    list_filter = (
        'new_status',
        'created_at',
    )