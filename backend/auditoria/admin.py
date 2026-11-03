from django.contrib import admin

from .models import EventoAuditoria


@admin.register(EventoAuditoria)
class EventoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('ocorrido_em', 'acao', 'object_repr', 'usuario', 'content_type')
    list_filter = ('acao', 'content_type')
    search_fields = ('object_repr', 'object_id')
    readonly_fields = (
        'acao',
        'content_type',
        'object_id',
        'object_repr',
        'usuario',
        'ocorrido_em',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
