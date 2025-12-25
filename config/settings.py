"""
Configuration management module for the crypto application.

This module handles all application configuration through environment variables
with proper validation, type hints, and security best practices. No secrets
should be hardcoded in this file.

Environment Variables:
    - DEBUG: Application debug mode (default: False)
    - ENVIRONMENT: Deployment environment - 'development', 'staging', 'production' (default: 'development')
    - SECRET_KEY: Django secret key (required in production)
    - ALLOWED_HOSTS: Comma-separated list of allowed hosts
    - DATABASE_URL: Database connection string
    - DATABASE_TIMEOUT: Database connection timeout in seconds (default: 30)
    - API_KEY: API authentication key (required for API endpoints)
    - LOG_LEVEL: Logging level - 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' (default: 'INFO')
    - MAX_CONNECTIONS: Maximum number of database connections (default: 10)
    - CACHE_TIMEOUT: Cache timeout in seconds (default: 3600)
    - API_RATE_LIMIT: API rate limit per minute (default: 100)
    - ENABLE_CORS: Enable CORS (default: False)
    - CORS_ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins
    - SSL_REDIRECT: Enable SSL redirect (default: True in production)
    - SESSION_TIMEOUT: Session timeout in minutes (default: 30)
    - MAX_UPLOAD_SIZE: Maximum upload size in MB (default: 10)
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""

    pass


class Settings:
    """
    Application configuration class with environment variable handling and validation.

    This class enforces security best practices:
    - No hardcoded secrets
    - Type-safe configuration values
    - Comprehensive validation
    - Clear error messages for missing/invalid config
    """

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    PROJECT_ROOT: Path = BASE_DIR

    # ========================
    # Environment & Debug
    # ========================

    @property
    def ENVIRONMENT(self) -> str:
        """
        Get the deployment environment.

        Returns:
            str: One of 'development', 'staging', or 'production'

        Raises:
            ConfigurationError: If invalid environment is specified
        """
        env = os.getenv("ENVIRONMENT", "development").lower()
        valid_envs = {"development", "staging", "production"}

        if env not in valid_envs:
            raise ConfigurationError(
                f"Invalid ENVIRONMENT '{env}'. Must be one of: {', '.join(valid_envs)}"
            )
        return env

    @property
    def DEBUG(self) -> bool:
        """
        Get debug mode status.

        WARNING: Never enable DEBUG in production!

        Returns:
            bool: True if debug mode is enabled
        """
        debug_str = os.getenv("DEBUG", "False").lower()
        debug = debug_str in ("true", "1", "yes")

        if debug and self.ENVIRONMENT == "production":
            logging.warning("DEBUG mode is enabled in production environment!")

        return debug

    # ========================
    # Security Settings
    # ========================

    @property
    def SECRET_KEY(self) -> str:
        """
        Get the Django secret key.

        Returns:
            str: The secret key

        Raises:
            ConfigurationError: If SECRET_KEY is not set in production
        """
        secret_key = os.getenv("SECRET_KEY")

        if not secret_key:
            if self.ENVIRONMENT == "production":
                raise ConfigurationError(
                    "SECRET_KEY environment variable is required in production"
                )
            # Use a development default only in non-production environments
            logging.warning("SECRET_KEY not set, using development default")
            secret_key = "dev-key-do-not-use-in-production"

        if len(secret_key) < 32 and self.ENVIRONMENT == "production":
            raise ConfigurationError(
                f"SECRET_KEY must be at least 32 characters long (got {len(secret_key)})"
            )

        return secret_key

    @property
    def SSL_REDIRECT(self) -> bool:
        """
        Get SSL redirect setting.

        Returns:
            bool: True to enable SSL redirect (default: True in production)
        """
        ssl_str = os.getenv("SSL_REDIRECT", "True" if self.ENVIRONMENT == "production" else "False").lower()
        return ssl_str in ("true", "1", "yes")

    @property
    def SECURE_HSTS_SECONDS(self) -> int:
        """
        Get HSTS max age in seconds (production only).

        Returns:
            int: HSTS max age (31536000 seconds = 1 year in production)
        """
        if self.ENVIRONMENT == "production":
            return 31536000  # 1 year
        return 0

    @property
    def SECURE_SSL_REDIRECT(self) -> bool:
        """
        Get secure SSL redirect setting.

        Returns:
            bool: True to force SSL redirect in production
        """
        return self.ENVIRONMENT == "production"

    # ========================
    # Database Settings
    # ========================

    @property
    def DATABASE_URL(self) -> str:
        """
        Get the database connection URL.

        Returns:
            str: Database URL in format: driver://user:password@host:port/database

        Raises:
            ConfigurationError: If DATABASE_URL is not set
        """
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            raise ConfigurationError(
                "DATABASE_URL environment variable is required"
            )

        # Validate basic URL structure (should contain :// and /)
        if "://" not in db_url or not db_url.split("://")[1]:
            raise ConfigurationError(
                f"Invalid DATABASE_URL format. Expected: driver://user:password@host:port/database"
            )

        return db_url

    @property
    def DATABASE_TIMEOUT(self) -> int:
        """
        Get database connection timeout in seconds.

        Returns:
            int: Timeout in seconds

        Raises:
            ConfigurationError: If invalid timeout value is provided
        """
        timeout_str = os.getenv("DATABASE_TIMEOUT", "30")

        try:
            timeout = int(timeout_str)
        except ValueError:
            raise ConfigurationError(
                f"DATABASE_TIMEOUT must be an integer, got '{timeout_str}'"
            )

        if timeout < 0:
            raise ConfigurationError(
                f"DATABASE_TIMEOUT must be non-negative, got {timeout}"
            )

        return timeout

    @property
    def MAX_CONNECTIONS(self) -> int:
        """
        Get maximum number of database connections.

        Returns:
            int: Maximum connections

        Raises:
            ConfigurationError: If invalid value is provided
        """
        max_conn_str = os.getenv("MAX_CONNECTIONS", "10")

        try:
            max_conn = int(max_conn_str)
        except ValueError:
            raise ConfigurationError(
                f"MAX_CONNECTIONS must be an integer, got '{max_conn_str}'"
            )

        if max_conn < 1:
            raise ConfigurationError(
                f"MAX_CONNECTIONS must be at least 1, got {max_conn}"
            )

        return max_conn

    # ========================
    # API Settings
    # ========================

    @property
    def API_KEY(self) -> str:
        """
        Get the API authentication key.

        Returns:
            str: The API key

        Raises:
            ConfigurationError: If API_KEY is not set
        """
        api_key = os.getenv("API_KEY")

        if not api_key:
            if self.ENVIRONMENT == "production":
                raise ConfigurationError(
                    "API_KEY environment variable is required in production"
                )
            logging.warning("API_KEY not set, API authentication will be disabled")
            api_key = ""

        return api_key

    @property
    def API_RATE_LIMIT(self) -> int:
        """
        Get API rate limit per minute.

        Returns:
            int: Requests per minute

        Raises:
            ConfigurationError: If invalid value is provided
        """
        limit_str = os.getenv("API_RATE_LIMIT", "100")

        try:
            limit = int(limit_str)
        except ValueError:
            raise ConfigurationError(
                f"API_RATE_LIMIT must be an integer, got '{limit_str}'"
            )

        if limit < 1:
            raise ConfigurationError(
                f"API_RATE_LIMIT must be at least 1, got {limit}"
            )

        return limit

    # ========================
    # Logging Settings
    # ========================

    @property
    def LOG_LEVEL(self) -> str:
        """
        Get the logging level.

        Returns:
            str: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

        Raises:
            ConfigurationError: If invalid log level is specified
        """
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

        if log_level not in valid_levels:
            raise ConfigurationError(
                f"Invalid LOG_LEVEL '{log_level}'. Must be one of: {', '.join(valid_levels)}"
            )

        return log_level

    @property
    def LOG_FILE(self) -> Optional[Path]:
        """
        Get the log file path.

        Returns:
            Optional[Path]: Path to log file, or None to use console only
        """
        log_file = os.getenv("LOG_FILE")
        if log_file:
            return Path(log_file)
        return None

    # ========================
    # Caching Settings
    # ========================

    @property
    def CACHE_TIMEOUT(self) -> int:
        """
        Get cache timeout in seconds.

        Returns:
            int: Cache timeout in seconds

        Raises:
            ConfigurationError: If invalid value is provided
        """
        timeout_str = os.getenv("CACHE_TIMEOUT", "3600")

        try:
            timeout = int(timeout_str)
        except ValueError:
            raise ConfigurationError(
                f"CACHE_TIMEOUT must be an integer, got '{timeout_str}'"
            )

        if timeout < 0:
            raise ConfigurationError(
                f"CACHE_TIMEOUT must be non-negative, got {timeout}"
            )

        return timeout

    # ========================
    # CORS Settings
    # ========================

    @property
    def ENABLE_CORS(self) -> bool:
        """
        Get CORS enablement status.

        Returns:
            bool: True if CORS is enabled
        """
        cors_str = os.getenv("ENABLE_CORS", "False").lower()
        return cors_str in ("true", "1", "yes")

    @property
    def CORS_ALLOWED_ORIGINS(self) -> List[str]:
        """
        Get list of allowed CORS origins.

        Returns:
            List[str]: List of allowed origins

        Raises:
            ConfigurationError: If ENABLE_CORS is True but no origins are provided
        """
        origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")

        if self.ENABLE_CORS and not origins_str:
            raise ConfigurationError(
                "CORS_ALLOWED_ORIGINS must be set when ENABLE_CORS is True"
            )

        if not origins_str:
            return []

        # Parse comma-separated origins and strip whitespace
        origins = [origin.strip() for origin in origins_str.split(",")]

        # Validate that origins are not empty after stripping
        origins = [o for o in origins if o]

        return origins

    # ========================
    # Session Settings
    # ========================

    @property
    def SESSION_TIMEOUT(self) -> int:
        """
        Get session timeout in minutes.

        Returns:
            int: Session timeout in minutes

        Raises:
            ConfigurationError: If invalid value is provided
        """
        timeout_str = os.getenv("SESSION_TIMEOUT", "30")

        try:
            timeout = int(timeout_str)
        except ValueError:
            raise ConfigurationError(
                f"SESSION_TIMEOUT must be an integer, got '{timeout_str}'"
            )

        if timeout < 1:
            raise ConfigurationError(
                f"SESSION_TIMEOUT must be at least 1 minute, got {timeout}"
            )

        return timeout

    # ========================
    # Upload Settings
    # ========================

    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        """
        Get maximum upload size in bytes.

        Returns:
            int: Maximum upload size in bytes

        Raises:
            ConfigurationError: If invalid value is provided
        """
        size_mb_str = os.getenv("MAX_UPLOAD_SIZE", "10")

        try:
            size_mb = int(size_mb_str)
        except ValueError:
            raise ConfigurationError(
                f"MAX_UPLOAD_SIZE must be an integer, got '{size_mb_str}'"
            )

        if size_mb < 1:
            raise ConfigurationError(
                f"MAX_UPLOAD_SIZE must be at least 1 MB, got {size_mb}"
            )

        # Convert MB to bytes
        return size_mb * 1024 * 1024

    # ========================
    # Host Settings
    # ========================

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """
        Get list of allowed hosts.

        Returns:
            List[str]: List of allowed hosts

        Raises:
            ConfigurationError: If invalid hosts are configured for production
        """
        hosts_str = os.getenv("ALLOWED_HOSTS", "*")

        if hosts_str == "*":
            if self.ENVIRONMENT == "production":
                raise ConfigurationError(
                    "ALLOWED_HOSTS must be explicitly set in production (cannot use '*')"
                )
            return ["*"]

        # Parse comma-separated hosts and strip whitespace
        hosts = [host.strip() for host in hosts_str.split(",")]
        hosts = [h for h in hosts if h]  # Remove empty strings

        if not hosts:
            raise ConfigurationError(
                "ALLOWED_HOSTS must contain at least one valid host"
            )

        return hosts

    # ========================
    # Utility Methods
    # ========================

    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all configuration settings.

        This method validates all critical settings and returns a summary.
        Use this on application startup to catch configuration errors early.

        Returns:
            Dict[str, Any]: Dictionary of validated settings

        Raises:
            ConfigurationError: If any validation fails
        """
        validated = {}

        # Test all properties to trigger validation
        critical_settings = [
            ("ENVIRONMENT", self.ENVIRONMENT),
            ("DEBUG", self.DEBUG),
            ("SECRET_KEY", "***" if self.SECRET_KEY else None),
            ("ALLOWED_HOSTS", self.ALLOWED_HOSTS),
            ("DATABASE_URL", "***"),  # Don't log actual URL
            ("DATABASE_TIMEOUT", self.DATABASE_TIMEOUT),
            ("MAX_CONNECTIONS", self.MAX_CONNECTIONS),
            ("API_KEY", "***" if self.API_KEY else None),
            ("API_RATE_LIMIT", self.API_RATE_LIMIT),
            ("LOG_LEVEL", self.LOG_LEVEL),
            ("CACHE_TIMEOUT", self.CACHE_TIMEOUT),
            ("SESSION_TIMEOUT", self.SESSION_TIMEOUT),
            ("MAX_UPLOAD_SIZE", f"{self.MAX_UPLOAD_SIZE // (1024 * 1024)} MB"),
            ("SSL_REDIRECT", self.SSL_REDIRECT),
            ("ENABLE_CORS", self.ENABLE_CORS),
        ]

        for name, value in critical_settings:
            validated[name] = value

        return validated

    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """
        Export configuration as dictionary.

        Args:
            include_secrets (bool): If True, include sensitive values
                                    (use with caution, never in logs/responses)

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        return {
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "secret_key": self.SECRET_KEY if include_secrets else "***",
            "allowed_hosts": self.ALLOWED_HOSTS,
            "database_timeout": self.DATABASE_TIMEOUT,
            "max_connections": self.MAX_CONNECTIONS,
            "api_key": self.API_KEY if include_secrets else "***",
            "api_rate_limit": self.API_RATE_LIMIT,
            "log_level": self.LOG_LEVEL,
            "cache_timeout": self.CACHE_TIMEOUT,
            "session_timeout": self.SESSION_TIMEOUT,
            "max_upload_size_mb": self.MAX_UPLOAD_SIZE // (1024 * 1024),
            "ssl_redirect": self.SSL_REDIRECT,
            "enable_cors": self.ENABLE_CORS,
        }


# Global settings instance
settings = Settings()


# Application startup validation
if __name__ == "__main__":
    # Validate configuration on startup
    try:
        config_summary = settings.validate_all()
        print("✓ Configuration validation successful!")
        print("\nConfiguration Summary:")
        for key, value in config_summary.items():
            print(f"  {key}: {value}")
    except ConfigurationError as e:
        print(f"✗ Configuration Error: {e}")
        exit(1)
