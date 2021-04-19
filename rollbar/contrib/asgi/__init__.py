__all__ = ['ASGIMiddleware']

import rollbar

try:
    from starlette.types import ASGIApp as ASGIAppType, Receive, Scope, Send
except ImportError:
    STARLETTE_INSTALLED = False
else:
    STARLETTE_INSTALLED = True


# Optional class annotations must be statically declared because
# IDEs cannot infer type hinting for arbitrary dynamic code
# TODO: Use typing directly, avoid Starlette
def ASGIApp(cls):
    async def _asgi_app(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception:
            if scope['type'] == 'http':
                rollbar.report_exc_info()
            raise

    cls._asgi_app = _asgi_app
    return cls


if STARLETTE_INSTALLED is True:

    @ASGIApp
    class ASGIMiddleware:
        def __init__(self, app: ASGIAppType) -> None:
            self.app = app

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            await self._asgi_app(scope, receive, send)


else:

    @ASGIApp
    class ASGIMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self._asgi_app(scope, receive, send)


def _hook(request, data):
    data['framework'] = 'asgi'


rollbar.BASE_DATA_HOOK = _hook
