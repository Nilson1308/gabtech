from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from core.models import Dominio, Gabinete
from plataforma.models import CadastroGabinete, OperadorPlataforma

SESSION_OPERADOR_KEY = 'platform_operador_id'


def operador_logado(request) -> OperadorPlataforma | None:
    operador_id = request.session.get(SESSION_OPERADOR_KEY)
    if not operador_id:
        return None
    try:
        return OperadorPlataforma.objects.get(pk=operador_id, is_active=True)
    except OperadorPlataforma.DoesNotExist:
        return None


class PlatformAdminSite(AdminSite):
    site_header = 'GabTech — Administração da plataforma'
    site_title = 'GabTech Plataforma'
    index_title = 'Gabinetes e cadastros'

    def has_permission(self, request):
        return operador_logado(request) is not None

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('login/', self.login, name='login'),
            path('logout/', self.logout, name='logout'),
        ]
        return custom + urls

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        if operador_logado(request):
            return HttpResponseRedirect(reverse('platform_admin:index'))

        erro = ''
        if request.method == 'POST':
            email = (request.POST.get('email') or '').strip().lower()
            senha = request.POST.get('senha') or ''
            try:
                op = OperadorPlataforma.objects.get(email__iexact=email, is_active=True)
            except OperadorPlataforma.DoesNotExist:
                op = None
            if op and op.verificar_senha(senha):
                request.session[SESSION_OPERADOR_KEY] = op.pk
                request.session.set_expiry(60 * 60 * 8)
                return HttpResponseRedirect(request.GET.get('next') or reverse('platform_admin:index'))
            erro = 'E-mail ou senha inválidos.'

        context = {
            **self.each_context(request),
            'title': 'Entrar',
            'erro': erro,
            'app_path': request.get_full_path(),
        }
        return render(request, 'plataforma/admin/login.html', context)

    def logout(self, request):
        request.session.flush()
        return HttpResponseRedirect(reverse('platform_admin:login'))


platform_admin_site = PlatformAdminSite(name='platform_admin')


class DominioInline(admin.TabularInline):
    model = Dominio
    extra = 0
    fields = ('domain', 'is_primary')


@admin.register(Gabinete, site=platform_admin_site)
class GabineteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'schema_name', 'created_on')
    search_fields = ('nome', 'schema_name')
    inlines = (DominioInline,)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('schema_name', 'created_on', 'logo')
        return ('created_on',)


@admin.register(Dominio, site=platform_admin_site)
class DominioAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__schema_name', 'tenant__nome')
    autocomplete_fields = ('tenant',)


@admin.register(CadastroGabinete, site=platform_admin_site)
class CadastroGabineteAdmin(admin.ModelAdmin):
    list_display = (
        'nome_gabinete',
        'slug',
        'status',
        'domain',
        'admin_email',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('nome_gabinete', 'slug', 'admin_email', 'domain')
    readonly_fields = (
        'id',
        'logo',
        'schema_name',
        'domain',
        'erro_mensagem',
        'tentativas',
        'ip_origem',
        'created_at',
        'updated_at',
        'concluido_em',
    )


class OperadorPlataformaForm(forms.ModelForm):
    senha_nova = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        required=False,
        help_text='Deixe em branco para manter ao editar.',
    )

    class Meta:
        model = OperadorPlataforma
        fields = ('email', 'nome', 'is_active')

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and not cleaned.get('senha_nova'):
            raise forms.ValidationError({'senha_nova': 'Informe a senha para novo operador.'})
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        senha = self.cleaned_data.get('senha_nova')
        if senha:
            instance.set_senha(senha)
        if commit:
            instance.save()
        return instance


@admin.register(OperadorPlataforma, site=platform_admin_site)
class OperadorPlataformaAdmin(admin.ModelAdmin):
    form = OperadorPlataformaForm
    list_display = ('email', 'nome', 'is_active', 'created_at')
    search_fields = ('email', 'nome')
    fields = ('email', 'nome', 'is_active', 'senha_nova')
