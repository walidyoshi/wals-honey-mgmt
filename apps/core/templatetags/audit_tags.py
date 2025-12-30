"""
Custom template tags for audit trail display
"""

from django import template
from django.contrib.contenttypes.models import ContentType
from apps.batches.models import AuditLog

register = template.Library()


@register.inclusion_tag('partials/change_history.html')
def show_change_history(obj, limit=10):
    """Display change history for any model instance"""
    content_type = ContentType.objects.get_for_model(obj)
    changes = AuditLog.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).select_related('changed_by').order_by('-changed_at')[:limit]
    
    return {'changes': changes, 'object': obj}
