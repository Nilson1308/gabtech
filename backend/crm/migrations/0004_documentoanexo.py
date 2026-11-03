import crm.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0003_tag_tipo_cidadao_marcadores'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoAnexo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(upload_to=crm.models.documento_cidadao_upload_to, verbose_name='arquivo')),
                ('nome_original', models.CharField(max_length=255, verbose_name='nome original')),
                ('content_type', models.CharField(blank=True, max_length=120, verbose_name='tipo MIME')),
                ('tamanho', models.PositiveIntegerField(verbose_name='tamanho (bytes)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='enviado em')),
                (
                    'cidadao',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='documentos',
                        to='crm.cidadao',
                        verbose_name='cidadão',
                    ),
                ),
                (
                    'enviado_por',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='documentos_crm_enviados',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='enviado por',
                    ),
                ),
            ],
            options={
                'verbose_name': 'documento anexo',
                'verbose_name_plural': 'documentos anexos',
                'ordering': ('-created_at',),
            },
        ),
    ]
