__all__ = [
    "AuthService",
    "InvalidCredentials",
    "MalformedCredentials",
]

import typing
from datetime import timedelta
from typing import Self

from httpx import AsyncClient, Auth, Request, Response
from jwt import DecodeError, PyJWKClient, PyJWKClientError, PyJWTError, decode
from pydantic import ValidationError

from services.auth.types import (
    Auth0AccessToken,
    BaseIDToken,
    RawIDToken,
    id_token_factory,
)
from services.base import BaseService
from services.config import ConfigService


class MalformedCredentials(ValueError):
    """
    Indicates that the received JWT is not well-formed.
    """


class InvalidCredentials(ValueError):
    """
    Indicates that a well-formed JWT was received, but the credentials are invalid.
    """


class BearerAuth(Auth):
    """
    Provides simple interface for adding bearer auth to HTTPX requests.
    """

    def __init__(self, token: str):
        super().__init__()

        self.token = token

    def auth_flow(self, request: Request) -> typing.Generator[Request, Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class AuthService(BaseService):
    """
    Methods to authenticate incoming requests.

    Currently hard-coded to use Auth0+JWTs, since we don't yet know what would need to
    change in order to support a different provider.
    """

    provides = "auth"

    @classmethod
    def factory(cls, config: ConfigService = None) -> Self:
        return AuthService(config)

    def __init__(self, config: ConfigService):
        super().__init__()

        self.config = config
        self._jwks_client = PyJWKClient(self.jwks_url)

    def authenticate(
        self,
        encoded_jwt: str,
        scopes: list[str] = None,
    ) -> Auth0AccessToken:
        """
        Authenticates and decodes the specified JWT.

        :param encoded_jwt: the encoded JWT (i.e., should be a string, not a dict).
        :param scopes: required scopes that the JWT must have.
        """
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(encoded_jwt).key
        except (PyJWKClientError, DecodeError) as e:
            raise MalformedCredentials(str(e)) from e

        # If we are in a development environment, specify a generous leeway for token
        # expiration, so that developers don't have to keep logging in to test stuff in
        # the app.
        leeway = timedelta(days=365) if self.config.is_development else 0

        try:
            token = Auth0AccessToken(
                **decode(
                    jwt=encoded_jwt,
                    key=signing_key,
                    algorithms=self.config.auth0_algorithms,
                    audience=self.config.auth0_audience,
                    issuer=self.config.auth0_issuer,
                    leeway=leeway,
                ),
                raw_token=encoded_jwt,
            )
        except (PyJWTError, ValidationError) as e:
            raise InvalidCredentials(str(e)) from e

        if scopes and not all(s in token.scopes for s in scopes):
            raise InvalidCredentials(
                f"Missing scopes: {', '.join(set(scopes) - token.scopes)}"
            )

        return token

    async def fetch_id_token(self, access_token: Auth0AccessToken) -> BaseIDToken:
        """
        Given an access token, fetches the corresponding ID token from Auth0.
        """
        async with AsyncClient() as client:
            response = await client.get(
                f"https://{self.config.auth0_domain}/userinfo",
                auth=BearerAuth(access_token.raw_token),
            )

        return id_token_factory(RawIDToken(**response.json()))

    @property
    def jwks_url(self) -> str:
        """
        URL to fetch JWKS (JSON Web Key Sets), so that we can load public keys used to
        check JWT signatures.

        :see: https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-key-sets
        """
        return f"https://{self.config.auth0_domain}/.well-known/jwks.json"
