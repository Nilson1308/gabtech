from django.contrib import admin

from .models import (
    Documento,
    EtiquetaDocumento,
    PastaDocumento,
    TemplateDocumento,
    TipoDocumento,
    VersaoDocumento,
)


@admin.register(EtiquetaDocumento)
class EtiquetaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor')
    search_fields = ('nome',)


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'is_sistema', 'cor')
    search_fields = ('nome', 'slug')


@admin.register(TemplateDocumento)
class TemplateDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_documento', 'is_default')
    list_filter = ('tipo_documento', 'is_default')


@admin.register(PastaDocumento)
class PastaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'parent', 'created_at')
    search_fields = ('nome',)


class VersaoDocumentoInline(admin.TabularInline):
    model = VersaoDocumento
    extra = 0
    readonly_fields = ('numero_versao', 'autor', 'created_at')


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_documento', 'status', 'autor', 'updated_at')
    list_filter = ('status', 'tipo_documento')
    search_fields = ('titulo',)
    inlines = (VersaoDocumentoInline,)
