"""
Settings compatibility shim for deployments referencing 'yourproject.settings'.
Redirects to 'sbj.settings'.
"""
from sbj.settings import *  # noqa: F401, F403
