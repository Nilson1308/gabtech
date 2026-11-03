from django.contrib import admin

from .models import CandidaturaTalento, EixoServico, VagaEmprego


@admin.register(EixoServico)
class EixoServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'cor')


@admin.register(VagaEmprego)
class VagaEmpregoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa_parceira', 'eixo', 'status', 'created_at')
    list_filter = ('status', 'eixo')


@admin.register(CandidaturaTalento)
class CandidaturaTalentoAdmin(admin.ModelAdmin):
    list_display = ('candidato', 'vaga', 'status_processo', 'updated_at')
    list_filter = ('status_processo',)
