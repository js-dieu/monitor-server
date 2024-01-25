class ConfigurationError(Exception):
    """Base error for configuration"""


class ConfigurationHolderNotFound(ConfigurationError):
    """Error raised when a configuration file is expected but cannot be found."""


class ConfigurationKeyNotFound(ConfigurationError):
    """Error raised when a config key does not map to any model."""


class ConfigurationRefUnsolvable(ConfigurationError):
    """Error raised when an object ref another object but the associated declaration cannot be found."""


class ConfigurationKeyAlreadyExists(ConfigurationError):
    """Error raised when a key is declared but another object use the same declaration key."""


class ConfigurationKeyIsInvalid(ConfigurationError):
    """Error raised when a configuration model has an invalid configuration key."""
