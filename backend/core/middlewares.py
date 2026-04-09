from channels.middleware import BaseMiddleware


class TokenAuthMiddleware(BaseMiddleware):
    """Channels middleware that authenticates a websocket connection from
    a JWT passed as `?token=<access>` in the query string."""

    async def __call__(self, scope, receive, send):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.exceptions import TokenError
        from rest_framework_simplejwt.tokens import UntypedToken

        query_string = scope["query_string"].decode()
        token_key = None
        if "token=" in query_string:
            token_key = query_string.split("token=")[-1].split("&")[0]

        scope["user"] = AnonymousUser()
        if token_key:
            try:
                validated = UntypedToken(token_key)
                user_id = validated["user_id"]
                User = get_user_model()
                scope["user"] = await User.objects.aget(pk=user_id)
            except (TokenError, KeyError, Exception):
                scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
