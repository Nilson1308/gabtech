#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, '.venv', 'bin', 'python')


def _deps_available() -> bool:
    try:
        import django_tenants  # noqa: F401
        import corsheaders  # noqa: F401
        return True
    except ImportError:
        return False


def _reexec_with_venv_if_needed() -> None:
    if not os.path.isfile(VENV_PYTHON):
        return
    if os.path.realpath(sys.executable) == os.path.realpath(VENV_PYTHON):
        return
    if _deps_available():
        return
    os.execv(VENV_PYTHON, [VENV_PYTHON, *sys.argv])


def main():
    """Run administrative tasks."""
    _reexec_with_venv_if_needed()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    if not _deps_available():
        print(
            'Dependências do backend ausentes (django-tenants / django-cors-headers).\n'
            f'Ative o venv: source .venv/bin/activate\n'
            f'Instale: {VENV_PYTHON} -m pip install -r requirements.txt\n'
            f'Ou execute: {VENV_PYTHON} manage.py <comando>'
        )
        sys.exit(1)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
