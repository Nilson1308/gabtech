from django.contrib import admin

from .models import Espaco, Evento, TipoEvento


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'icone', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Espaco)
class EspacoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'capacidade', 'ativo', 'created_at')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data', 'hora_inicio', 'hora_fim', 'tipo', 'espaco', 'status')
    list_filter = ('status', 'data', 'tipo')
    search_fields = ('titulo',)
    filter_horizontal = ('convidados',)
    autocomplete_fields = ('tipo', 'espaco', 'criado_por')
