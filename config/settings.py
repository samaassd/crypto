"""
Secure Configuration Management Module

This module provides a centralized configuration management system for the crypto application.
All sensitive configuration values are loaded from environment variables to prevent hardcoding
of secrets and API keys in the codebase.

Environment Variables Required:
- DEBUG: Application debug mode (default: False)
- SECRET_KEY: Django secret key for cryptographic operations
- ALLOWED_HOSTS: Comma-separated list of allowed hosts
- DATABASE_URL: Database connection string
- API_KEY: Application API key for external services
- API_SECRET: Application API secret
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- CORS_ALLOWED_ORIGINS: Comma-separated list of CORS allowed origins
- CACHE_URL: Cache backend URL (e.g., redis://localhost:6379/0)
- ETHEREUM_RPC_URL: Ethereum RPC endpoint URL
- ETHERSCAN_API_KEY: Etherscan API key for blockchain data
"""

import os
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class Settings:
    """
    Secure settings configuration class.
    
    Loads all configuration from environment variables with proper validation,
    type hints, and sensible defaults where appropriate.
    """

    # Application Settings
    DEBUG: bool = _get_bool_env("DEBUG", False)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALLOWED_HOSTS: List[str] = _parse_comma_separated_env("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
    CORS_ALLOWED_ORIGINS: List[str] = _parse_comma_separated_env(
        "CORS_ALLOWED_ORIGINS",
        ["http://localhost:3000", "http://localhost:8000"]
    )
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
    
    # API Configuration
    API_KEY: str = os.getenv("API_KEY")
    API_SECRET: str = os.getenv("API_SECRET")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.example.com")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_RETRY_ATTEMPTS: int = int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    API_RETRY_DELAY: int = int(os.getenv("API_RETRY_DELAY", "5"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    
    # Cache Configuration
    CACHE_URL: str = os.getenv("CACHE_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    
    # Blockchain Configuration
    ETHEREUM_RPC_URL: str = os.getenv("ETHEREUM_RPC_URL")
    ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY")
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL")
    BSC_RPC_URL: str = os.getenv("BSC_RPC_URL")
    
    # Feature Flags
    ENABLE_CACHING: bool = _get_bool_env("ENABLE_CACHING", True)
    ENABLE_RATE_LIMITING: bool = _get_bool_env("ENABLE_RATE_LIMITING", True)
    ENABLE_MONITORING: bool = _get_bool_env("ENABLE_MONITORING", True)
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))
    
    # Timeout Configuration
    SOCKET_TIMEOUT: int = int(os.getenv("SOCKET_TIMEOUT", "30"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
    
    @staticmethod
    def _get_bool_env(key: str, default: bool = False) -> bool:
        """
        Parse boolean environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not set
            
        Returns:
            Boolean value from environment variable
        """
        value = os.getenv(key, str(default)).lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        else:
            raise ConfigurationError(
                f"Invalid boolean value for {key}: {value}. "
                f"Expected one of: true, false, 1, 0, yes, no, on, off"
            )
    
    @staticmethod
    def _parse_comma_separated_env(
        key: str,
        default: Optional[List[str]] = None
    ) -> List[str]:
        """
        Parse comma-separated environment variable into a list.
        
        Args:
            key: Environment variable name
            default: Default list if not set
            
        Returns:
            List of strings from comma-separated environment variable
        """
        value = os.getenv(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(",") if item.strip()]
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate all required configuration settings.
        
        Raises:
            ConfigurationError: If any required configuration is missing or invalid
        """
        required_settings = [
            ("SECRET_KEY", cls.SECRET_KEY),
            ("DATABASE_URL", cls.DATABASE_URL),
            ("API_KEY", cls.API_KEY),
            ("API_SECRET", cls.API_SECRET),
        ]
        
        missing_settings = [key for key, value in required_settings if not value]
        
        if missing_settings:
            raise ConfigurationError(
                f"Missing required configuration: {', '.join(missing_settings)}. "
                f"Please set these environment variables."
            )
        
        # Validate database URL format
        cls._validate_database_url(cls.DATABASE_URL)
        
        # Validate API configuration
        cls._validate_api_configuration()
        
        # Validate blockchain configuration
        cls._validate_blockchain_configuration()
        
        logger.info(f"Configuration validated successfully for {cls.ENVIRONMENT} environment")
    
    @staticmethod
    def _validate_database_url(url: str) -> None:
        """
        Validate database URL format.
        
        Args:
            url: Database URL to validate
            
        Raises:
            ConfigurationError: If URL format is invalid
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                raise ConfigurationError(
                    f"Invalid DATABASE_URL: Missing scheme (e.g., postgresql://, mysql://)"
                )
            if not parsed.netloc and not parsed.path:
                raise ConfigurationError(
                    f"Invalid DATABASE_URL: Missing host or path"
                )
        except Exception as e:
            raise ConfigurationError(f"Invalid DATABASE_URL: {str(e)}")
    
    @classmethod
    def _validate_api_configuration(cls) -> None:
        """
        Validate API configuration settings.
        
        Raises:
            ConfigurationError: If API configuration is invalid
        """
        if cls.API_TIMEOUT <= 0:
            raise ConfigurationError(
                f"API_TIMEOUT must be positive, got: {cls.API_TIMEOUT}"
            )
        
        if cls.API_RETRY_ATTEMPTS < 0:
            raise ConfigurationError(
                f"API_RETRY_ATTEMPTS must be non-negative, got: {cls.API_RETRY_ATTEMPTS}"
            )
        
        if cls.API_RETRY_DELAY <= 0:
            raise ConfigurationError(
                f"API_RETRY_DELAY must be positive, got: {cls.API_RETRY_DELAY}"
            )
    
    @classmethod
    def _validate_blockchain_configuration(cls) -> None:
        """
        Validate blockchain configuration settings.
        
        Raises:
            ConfigurationError: If blockchain URLs are invalid
        """
        blockchain_urls = {
            "ETHEREUM_RPC_URL": cls.ETHEREUM_RPC_URL,
            "POLYGON_RPC_URL": cls.POLYGON_RPC_URL,
            "BSC_RPC_URL": cls.BSC_RPC_URL,
        }
        
        for key, url in blockchain_urls.items():
            if url:
                try:
                    parsed = urlparse(url)
                    if not parsed.scheme or not parsed.netloc:
                        raise ConfigurationError(
                            f"Invalid {key}: Must be a valid URL"
                        )
                except Exception as e:
                    raise ConfigurationError(
                        f"Invalid {key}: {str(e)}"
                    )
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """
        Get all configuration settings as a dictionary (excluding sensitive values).
        
        Returns:
            Dictionary of non-sensitive configuration settings
        """
        sensitive_keys = {
            "SECRET_KEY", "API_KEY", "API_SECRET", "ETHERSCAN_API_KEY",
            "DATABASE_URL"
        }
        
        config = {}
        for key in dir(cls):
            if not key.startswith("_") and key.isupper():
                value = getattr(cls, key)
                if not callable(value) and key not in sensitive_keys:
                    config[key] = value
        
        return config
    
    @classmethod
    def log_configuration(cls, mask_sensitive: bool = True) -> None:
        """
        Log current configuration settings.
        
        Args:
            mask_sensitive: Whether to mask sensitive values in logs
        """
        logger.info("=" * 50)
        logger.info("Current Configuration:")
        logger.info("=" * 50)
        
        config = cls.get_config_dict()
        for key, value in sorted(config.items()):
            logger.info(f"{key}: {value}")
        
        if mask_sensitive:
            logger.info("SECRET_KEY: ***MASKED***")
            logger.info("API_KEY: ***MASKED***")
            logger.info("API_SECRET: ***MASKED***")
            logger.info("ETHERSCAN_API_KEY: ***MASKED***")
        
        logger.info("=" * 50)


def _get_bool_env(key: str, default: bool = False) -> bool:
    """
    Module-level helper function to parse boolean environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        Boolean value from environment variable
    """
    return Settings._get_bool_env(key, default)


def _parse_comma_separated_env(
    key: str,
    default: Optional[List[str]] = None
) -> List[str]:
    """
    Module-level helper function to parse comma-separated environment variables.
    
    Args:
        key: Environment variable name
        default: Default list if not set
        
    Returns:
        List of strings from comma-separated environment variable
    """
    return Settings._parse_comma_separated_env(key, default)


# Initialize and validate settings on module import
try:
    Settings.validate()
except ConfigurationError as e:
    logger.error(f"Configuration validation failed: {str(e)}")
    if Settings.DEBUG:
        raise
    else:
        logger.warning("Running with incomplete configuration in production mode")


# Export settings instance for use throughout the application
config = Settings()
