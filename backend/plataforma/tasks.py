from celery import shared_task

from plataforma.services import executar_provisionamento


@shared_task(name='plataforma.provisionar_cadastro', bind=True, max_retries=2)
def provisionar_cadastro_task(self, cadastro_id: str, senha_admin: str) -> None:
    try:
        executar_provisionamento(cadastro_id, senha_admin)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc
