from django.contrib import admin

from .models import (
    ComunicacaoDisparo,
    ConvidadoEvento,
    Credenciado,
    EventoCerimonial,
    ItemChecklist,
    ItemChecklistPadrao,
)


@admin.register(EventoCerimonial)
class EventoCerimonialAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento_agenda', 'status_logistico', 'created_at')
    list_filter = ('status_logistico',)


admin.site.register(ItemChecklistPadrao)
admin.site.register(ItemChecklist)
admin.site.register(ConvidadoEvento)
admin.site.register(Credenciado)
admin.site.register(ComunicacaoDisparo)
