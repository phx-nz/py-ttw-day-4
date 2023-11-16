__all__ = [
    "Auth0AccessToken",
    "Auth0IDToken",
    "BaseIDToken",
    "GoogleIDToken",
    "RawIDToken",
    "id_token_factory",
    "id_token_registry",
]

import typing
from abc import abstractmethod
from functools import cached_property
from inspect import isabstract

from class_registry import ClassRegistry, RegistryKeyError
from pydantic import BaseModel, ConfigDict


class Auth0AccessToken(BaseModel):
    """
    Structure of claims in an Auth0 access token issued by Auth0.
    :see: https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-token-claims
    """

    raw_token: str
    """
    The raw/encoded token that was decoded to create this access token.
    """

    aud: list[str]
    """
    Recipient(s) for which the JWT is intended.
    
    Could have multiple values (e.g., if the access token has 'profile' scope, then
    ``aud`` will also include the Auth0 endpoint to request user profile).
    
    One of the values must match `<ConfigService>.auth0_audience`.
    """

    azp: str
    """
    Auth0 client ID of the application that initiated the authorisation flow.
    """

    exp: int
    """
    Unix timestamp after which the JWT expires.
    
    .. note:: Denominated in seconds, not milliseconds.
    """

    iat: int
    """
    Unix timestamp when the JWT was issued.  Can be used to determine the age of the
    JWT.
    
    .. note:: Denominated in seconds, not milliseconds.
    """

    iss: str
    """
    Issuer of the JWT.  Must match ``<ConfigService>.auth0_domain`` to be valid.
    """

    scope: str
    """
    Space-delineated list of scopes that this token has access to.
    """

    sub: str
    """
    The unique identifier of the subject (i.e., user) in Auth0's database.
    
    This value can be used as the user ID for corresponding records in the application
    database.
    """

    @cached_property
    def scopes(self) -> set[str]:
        """
        :returns: ``self.scope`` as a set.
        """
        return set(self.scope.split(" "))


id_token_registry = ClassRegistry(attr_name="SUB_PREFIX")


class RawIDToken(BaseModel):
    """
    Minimal information needed to construct an ID token.
    """

    model_config = ConfigDict(extra="allow")

    sub: str
    """
    The unique identifier of the subject (i.e., user) in Auth0's database.
    
    This value can be used as the user ID for corresponding records in the application
    database.
    """

    @property
    def id_token_type(self) -> str:
        """
        :returns: the type of ID token associated with this account.
        """
        return self.sub.split("|", 1)[0]

    def get_external_id(self) -> str:
        """
        Returns the external ID that maps the ID token to a Profile record.
        """
        return self.sub


class BaseIDToken(RawIDToken):
    SUB_PREFIX: typing.ClassVar[str]
    """
    The prefix on the ``sub`` value that identifies what type of ID token it is.
    """

    def __init_subclass__(cls, **kwargs):
        """
        Workaround for https://github.com/todofixthis/class-registry/issues/14
        """
        super().__init_subclass__(**kwargs)
        if not isabstract(cls):
            id_token_registry.register(cls)

    @abstractmethod
    def get_email(self) -> str:
        """
        Returns the email address associated with the ID token.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the user's name (or as much of it as the ID provider knows.
        """


class Auth0IDToken(BaseIDToken):
    """
    ID token for a user who signed in to Auth0 directly using username and password
    (i.e., not via a social login).
    """

    SUB_PREFIX = "auth0"

    email: str
    """
    User's email address.
    
    .. important::
    
       This value will only be present if the access token includes the "email" scope.
    """

    name: str
    """
    User's username.
    
    This value is likely the same as their email address, but this behaviour should not
    be relied upon!  If you need the user's email address, use :py:attr:`email` instead.
    """

    nickname: str
    """
    User's name, not used for auth purposes (i.e., first name).
    """

    picture: str
    """
    URL of the user's avatar.
    """

    def get_email(self) -> str:
        return self.email

    def get_name(self) -> str:
        return self.nickname


class GoogleIDToken(BaseIDToken):
    """
    ID token for a user who signed in to Auth0 using their Google account.
    """

    SUB_PREFIX = "google-oauth2"

    email: str
    """
    User's email address.
    
    .. important::
    
       This value will only be present if the access token includes the "email" scope.
    """

    emailVerified: bool
    """
    Whether the user's email address has been verified (i.e., whether the user clicked
    the magic link in the email that Auth0 sent after they created their account).
    """

    familyName: str
    """
    User's last/family name.
    """

    givenName: str
    """
    User's first/given name.
    """

    locale: str
    """
    User's preferred locale, formatted as an IETF BCP 47 language tag (e.g., "en-NZ").
    
    :see: https://en.wikipedia.org/wiki/IETF_language_tag
    """

    name: str
    """
    User's full name.
    """

    nickname: str
    """
    User's username, usually the username part of their email address.
    
    E.g., if ``email = 'alice@example.com'``, then ``nickname = 'alice'``.
    """

    picture: str
    """
    URL of the user's avatar.
    """

    updatedAt: str
    """
    ISO-formatted timestamp when the user account was last modified (I think; not 100%
    sure about this one).
    """

    def get_email(self) -> str:
        return self.email

    def get_name(self) -> str:
        return self.name


def id_token_factory[T: BaseIDToken](token: RawIDToken) -> T:
    """
    Returns an ID token with the correct type, corresponding to
    :py:attr:`RawIDToken.id_token_type`.
    """
    try:
        return id_token_registry.get(token.id_token_type, **dict(token))
    except RegistryKeyError as e:
        raise KeyError(f"Unknown ID token type: {str(e)}") from e
