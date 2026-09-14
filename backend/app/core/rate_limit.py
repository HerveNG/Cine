"""Rate limiting — protects /auth/login and /auth/register from brute
force / credential-stuffing (see docs/known-issues.md). Keyed by remote
IP; in-memory storage is fine for a single-process MVP deployment.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
