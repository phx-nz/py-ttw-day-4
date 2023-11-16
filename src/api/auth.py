__all__ = ["requires_auth", "UnauthenticatedException", "UnauthorizedException"]

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from starlette.requests import Request

import services.auth.types
from services import auth, get_service


class UnauthenticatedException(HTTPException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class requires_auth(HTTPBearer):
    """
    Requires a request to have a valid Auth0 token in order to access an endpoint.

    Activate for an endpoint by annotating its path operation function's argument with
    :py:func:`fastapi.Security`.

    Example::

       @router.get("/auth/me")
       async def get_own_profile(
           token: Annotated[
               Auth0AccessToken,
               Security(requires_auth(), scopes=["profile"])
           ]
       )
    """

    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes = None,
    ) -> services.auth.types.Auth0AccessToken:
        token: HTTPAuthorizationCredentials | None = await super().__call__(request)

        if not token:
            raise UnauthenticatedException()

        auth_service: auth.AuthService = get_service(auth.AuthService)

        try:
            return auth_service.authenticate(token.credentials, security_scopes.scopes)
        except auth.MalformedCredentials as e:
            raise UnauthenticatedException(str(e)) from e
        except auth.InvalidCredentials as e:
            raise UnauthorizedException(str(e)) from e
