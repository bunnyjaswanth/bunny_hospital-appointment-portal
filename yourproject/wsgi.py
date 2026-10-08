"""
WSGI compatibility shim for Render deployments referencing 'yourproject.wsgi:application'.
Redirects to 'sbj.wsgi:application'.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sbj.settings')

from sbj.wsgi import application  # noqa: E402
