"""
Smithery Config Middleware - Extracts configuration from HTTP requests

This middleware extracts Smithery session configuration from ASGI scope
and makes it available to the request context.
"""

from smithery.utils.config import parse_config_from_asgi_scope


class SmitheryConfigMiddleware:
    """Middleware to extract and store Smithery configuration from requests"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get('type') == 'http':
            try:
                scope['smithery_config'] = parse_config_from_asgi_scope(scope)
            except Exception as e:
                print(f"SmitheryConfigMiddleware: Error parsing config: {e}")
                scope['smithery_config'] = {}
        await self.app(scope, receive, send)
