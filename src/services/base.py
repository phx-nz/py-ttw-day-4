__all__ = ["BaseService", "ServiceRegistry", "get_service", "registry"]

import typing
from abc import abstractmethod
from inspect import signature
from typing import Self

from class_registry import AutoRegister, ClassRegistry, ClassRegistryInstanceCache


class ServiceRegistry(ClassRegistry):
    """
    Registry of all services for the application.
    """

    def __init__(self):
        super().__init__(attr_name="provides", unique=True)

    def create_instance(
        self, class_: "typing.Type[BaseService]", *args, **kwargs
    ) -> object:
        # Intuit dependencies from the method's kwargs.
        dependencies = {
            param.name: get_service(param.annotation)
            for param in signature(class_.factory).parameters.values()
        }

        # Call the factory method and pass in dependencies.
        return class_.factory(**dependencies)


# Wrap the service registry in a cache, so that we only instantiate each service
# instance once.
_registry = ServiceRegistry()
registry = ClassRegistryInstanceCache(_registry)


class BaseService(metaclass=AutoRegister(_registry)):
    """
    Base class for application services.

    .. important::

       Make sure to activate your service by importing it in ``services/__init__.py``!

       :see: https://class-registry.readthedocs.io/en/latest/advanced_topics.html
    """

    @property
    @abstractmethod
    def provides(self) -> str:
        """
        Returns the service's key in the service registry.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def factory(cls) -> Self:
        """
        Returns an instance of the service.

        :param env: the app's environment setting ("development", "test", etc.).

        Declare dependency services for this method as kwargs, where each kwarg
        corresponds to a service instance.  The service registry will inject these
        automatically at runtime (using :py:func:`get_service`).

        Example::

           class DatabaseService(BaseService):
               @classmethod
               def factory(cls, config: ConfigService):
                   return DatabaseService(config)

        .. important::

           Each kwarg must have an annotation (type hint) indicating a
           :py:class:`BaseService` class.  You can call each kwarg whatever name you'd
           like::

              def factory(cls,
                  # Correct
                  config: ConfigService,
                  any_name_you_want: DatabaseService,

                  # Incorrect - missing annotation, or not a BaseService class
                  config,
                  config: dict,
              )
        """
        raise NotImplementedError()


def get_service[S: BaseService](service: typing.Type[S]) -> S:
    """
    Returns the specified service instance from the registry.
    """
    return registry[service.provides]
