from django.contrib import admin

from .models import Cidadao, DocumentoAnexo, Endereco, PerfilProfissional, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'tipo')


class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 0


class PerfilProfissionalInline(admin.TabularInline):
    model = PerfilProfissional
    extra = 0


class DocumentoAnexoInline(admin.TabularInline):
    model = DocumentoAnexo
    extra = 0
    readonly_fields = ('nome_original', 'tamanho', 'content_type', 'created_at')


@admin.register(Cidadao)
class CidadaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'cpf')
    search_fields = ('nome', 'cpf', 'telefone', 'email')
    filter_horizontal = ('marcadores',)
    inlines = (EnderecoInline, PerfilProfissionalInline, DocumentoAnexoInline)
