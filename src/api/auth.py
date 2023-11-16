__all__ = ["requires_auth", "UnauthenticatedException", "UnauthorizedException"]

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from starlette.requests import Request

from models import Profile
from services import auth, get_service
from services.profile import ProfileService


class UnauthenticatedException(HTTPException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class requires_auth(HTTPBearer):
    """
    Requires a request to have a valid Auth0 token in order to access an endpoint.
    If the request is authenticated, the corresponding profile record will be returned.

    Activate for an endpoint by annotating its path operation function's argument with
    :py:func:`fastapi.Security`.

    Example::

       @router.get("/auth/me")
       async def get_own_profile(
           profile: Annotated[
               Profile,
               Security(requires_auth(), scopes=["profile"])
           ]
       )
    """

    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes = None,
    ) -> Profile:
        token: HTTPAuthorizationCredentials | None = await super().__call__(request)

        if not token:
            raise UnauthenticatedException()

        auth_service: auth.AuthService = get_service(auth.AuthService)

        try:
            access_token = auth_service.authenticate(
                token.credentials, security_scopes.scopes
            )
        except auth.MalformedCredentials as e:
            raise UnauthenticatedException(str(e)) from e
        except auth.InvalidCredentials as e:
            raise UnauthorizedException(str(e)) from e
        else:
            profile_service: ProfileService = get_service(ProfileService)

            async with profile_service.session() as session:
                profile = await profile_service.get_by_external_id(
                    session, access_token.sub
                )

                if not profile:
                    id_token: auth.BaseIDToken = await auth_service.fetch_id_token(
                        access_token
                    )

                    profile = Profile(
                        external_id=id_token.get_external_id(),
                        username=id_token.get_email(),
                        password="",
                        gender="",
                        full_name=id_token.get_name(),
                        street_address="",
                        email=id_token.get_email(),
                    )

                session.add(profile)
                await session.commit()

            return profile
