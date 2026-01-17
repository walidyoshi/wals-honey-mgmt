"""
Audit Template Tags

Custom template tags for rendering audit trail and change history information in templates.

Tags:
    show_change_history: Renders a list of recent changes for a specific object.
"""

from django import template
from django.contrib.contenttypes.models import ContentType
from apps.batches.models import AuditLog

register = template.Library()


@register.inclusion_tag('partials/change_history.html')
def show_change_history(obj, limit=10):
    """
    Inclusion tag to display the change history for any model instance.
    
    Queries the AuditLog for records matching the object's ContentType and ID.
    
    Args:
        obj (Model): The model instance to show history for.
        limit (int, optional): Maximum number of history entries to show. Defaults to 10.
    
    Returns:
        dict: Context dictionary containing:
            - 'changes': QuerySet of AuditLog entries.
            - 'object': The original object.
    
    Example:
        {% load audit_tags %}
        {% show_change_history current_batch 5 %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    
    # Retrieve recent audit logs for this specific object
    changes = AuditLog.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).select_related('changed_by').order_by('-changed_at')[:limit]
    
    return {'changes': changes, 'object': obj}
