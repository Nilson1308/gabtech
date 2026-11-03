from django.db.models.signals import post_save
from django.dispatch import receiver

from usuarios.models import User
from usuarios.rbac_utils import vincular_perfil_administrador


@receiver(post_save, sender=User)
def garantir_perfil_admin_superuser(sender, instance: User, **kwargs):
    vincular_perfil_administrador(instance)
