from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Modulo, Perfil, Permissao, User


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('codename', 'nome', 'cor')
    search_fields = ('codename', 'nome')


@admin.register(Permissao)
class PermissaoAdmin(admin.ModelAdmin):
    list_display = ('codename', 'nome', 'modulo')
    list_filter = ('modulo',)
    search_fields = ('codename', 'nome')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nome', 'is_admin', 'cor', 'created_at')
    filter_horizontal = ('permissoes',)
    search_fields = ('nome',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            'Gabinete',
            {'fields': ('avatar', 'status', 'perfil')},
        ),
    )
    list_display = (
        'username',
        'email',
        'get_cargo',
        'status',
        'is_staff',
        'is_active',
    )
    list_filter = ('status', 'is_staff', 'is_active', 'perfil')

    @admin.display(description='cargo')
    def get_cargo(self, obj: User) -> str:
        return obj.cargo
