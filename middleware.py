"""
Smithery Config Middleware - Extracts configuration from HTTP requests

This middleware extracts Smithery session configuration from ASGI scope
and makes it available to the request context.
"""

import contextvars
from smithery.utils.config import parse_config_from_asgi_scope

# Context variable to store config for the current request
_request_config_var = contextvars.ContextVar('request_config', default={})


def get_current_request_config():
    """Get the config for the current request from context"""
    return _request_config_var.get()


class SmitheryConfigMiddleware:
    """Middleware to extract and store Smithery configuration from requests"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get('type') == 'http':
            try:
                config = parse_config_from_asgi_scope(scope)
                scope['smithery_config'] = config
                # Store in context variable for access by tools
                _request_config_var.set(config)
                print(f"SmitheryConfigMiddleware: Extracted config: {config}")
            except Exception as e:
                print(f"SmitheryConfigMiddleware: Error parsing config: {e}")
                scope['smithery_config'] = {}
                _request_config_var.set({})
        await self.app(scope, receive, send)
