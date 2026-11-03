from django.contrib import admin

from .models import Anexo, Atendimento, ConfiguracaoSla, Despacho, Macrotema


@admin.register(Macrotema)
class MacrotemaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'icone')


class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 0
    fields = ('despacho', 'arquivo', 'nome_original', 'tamanho', 'enviado_por', 'created_at')
    readonly_fields = ('nome_original', 'tamanho', 'created_at')
    autocomplete_fields = ('despacho',)


class DespachoInline(admin.TabularInline):
    model = Despacho
    extra = 0
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'assunto', 'status', 'macrotema', 'responsavel', 'created_at')
    list_filter = ('status', 'macrotema', 'prioridade', 'tags')
    search_fields = ('protocolo', 'assunto', 'cidadao__nome')
    filter_horizontal = ('tags',)
    inlines = (AnexoInline, DespachoInline)


class DespachoAnexoInline(admin.TabularInline):
    model = Anexo
    fk_name = 'despacho'
    extra = 0
    fields = ('arquivo', 'nome_original', 'tamanho', 'enviado_por', 'created_at')
    readonly_fields = ('nome_original', 'tamanho', 'created_at')


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('atendimento', 'tipo', 'autor', 'created_at')
    list_filter = ('tipo',)
    search_fields = ('atendimento__protocolo', 'conteudo')
    autocomplete_fields = ('atendimento', 'autor')
    inlines = (DespachoAnexoInline,)


@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ('nome_original', 'atendimento', 'despacho', 'tamanho', 'enviado_por', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nome_original', 'atendimento__protocolo')
    autocomplete_fields = ('atendimento', 'despacho', 'enviado_por')
    readonly_fields = ('nome_original', 'content_type', 'tamanho', 'created_at')


@admin.register(ConfiguracaoSla)
class ConfiguracaoSlaAdmin(admin.ModelAdmin):
    list_display = (
        'horas_baixa',
        'horas_media',
        'horas_alta',
        'horas_urgente',
        'updated_at',
    )

    def has_add_permission(self, request):
        if ConfiguracaoSla.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
