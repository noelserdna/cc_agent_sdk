"""
Core configuration management using pydantic-settings.

This module provides centralized configuration for the CV Cybersecurity Analyzer API,
loading environment variables and validating them using Pydantic BaseSettings.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port", ge=1, le=65535)
    api_workers: int = Field(default=4, description="Number of API workers", ge=1, le=16)

    # Authentication
    api_keys: str = Field(
        ..., description="Comma-separated list of valid API keys for authentication"
    )

    # Claude Agent SDK Configuration
    anthropic_api_key: str = Field(
        ..., description="Anthropic API key for Claude Agent SDK"
    )
    claude_model: str = Field(
        default="claude-sonnet-4-5-20250929", description="Claude model to use"
    )
    claude_max_tokens: int = Field(
        default=8192, description="Maximum tokens per request", ge=1000, le=100000
    )

    # Agent SDK Advanced Configuration
    agent_setting_sources: list[str] = Field(
        default=["user", "project"],
        description="Sources for loading Agent SDK settings and skills"
    )
    agent_allowed_tools: list[str] = Field(
        default=["Skill"],
        description="Tools allowed for the Agent SDK"
    )
    agent_cwd: str = Field(
        default=".",
        description="Working directory for Agent SDK"
    )

    # File Upload Configuration
    max_file_size_mb: int = Field(
        default=10, description="Maximum file size in megabytes", ge=1, le=100
    )
    allowed_extensions: str = Field(
        default="pdf", description="Comma-separated allowed file extensions"
    )

    # Retry Configuration
    retry_max_attempts: int = Field(
        default=3, description="Maximum retry attempts for API calls", ge=1, le=10
    )
    retry_delays: str = Field(
        default="1,2,4", description="Comma-separated retry delays in seconds"
    )
    retry_max_total_seconds: int = Field(
        default=30, description="Maximum total retry time in seconds", ge=10, le=120
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: Literal["json", "console"] = Field(
        default="json", description="Log output format"
    )
    log_pii_redaction: bool = Field(
        default=True, description="Enable PII redaction in logs"
    )

    # Performance & Limits
    analysis_timeout_seconds: int = Field(
        default=30, description="Timeout for CV analysis", ge=10, le=120
    )
    concurrent_requests_limit: int = Field(
        default=10, description="Maximum concurrent requests", ge=1, le=100
    )

    # Development/Testing
    debug: bool = Field(default=False, description="Enable debug mode")
    test_mode: bool = Field(default=False, description="Enable test mode with mocked responses")
    vcr_record_mode: Literal["none", "once", "new_episodes", "all", "rewrite"] = Field(
        default="once", description="VCR cassette recording mode for tests"
    )

    @field_validator("api_keys")
    @classmethod
    def validate_api_keys(cls, v: str) -> str:
        """Validate that API keys are properly formatted."""
        keys = [k.strip() for k in v.split(",") if k.strip()]
        if not keys:
            raise ValueError("At least one API key must be provided")
        for key in keys:
            if len(key) < 16:
                raise ValueError(f"API key '{key}' is too short (minimum 16 characters)")
        return v

    @field_validator("retry_delays")
    @classmethod
    def validate_retry_delays(cls, v: str) -> str:
        """Validate retry delays format."""
        try:
            delays = [float(d.strip()) for d in v.split(",") if d.strip()]
            if not delays:
                raise ValueError("At least one retry delay must be provided")
            if any(d <= 0 for d in delays):
                raise ValueError("All retry delays must be positive numbers")
        except ValueError as e:
            raise ValueError(f"Invalid retry_delays format: {e}") from e
        return v

    @property
    def api_keys_list(self) -> list[str]:
        """Get API keys as a list."""
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Get allowed extensions as a list."""
        return [e.strip().lower() for e in self.allowed_extensions.split(",") if e.strip()]

    @property
    def retry_delays_list(self) -> list[float]:
        """Get retry delays as a list of floats."""
        return [float(d.strip()) for d in self.retry_delays.split(",") if d.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.

    This function exists to support FastAPI dependency injection
    and to allow for easier testing with overrides.

    Returns:
        Settings: The global settings instance
    """
    return settings


def validate_settings() -> dict[str, str]:
    """
    Validate all settings and return a summary.

    Returns:
        dict: Validation summary with status and messages
    """
    try:
        # Force validation by accessing properties
        _ = settings.api_keys_list
        _ = settings.retry_delays_list
        _ = settings.allowed_extensions_list

        return {
            "status": "valid",
            "message": "All settings validated successfully",
            "api_keys_count": str(len(settings.api_keys_list)),
            "claude_model": settings.claude_model,
            "log_level": settings.log_level,
            "debug_mode": str(settings.debug),
        }
    except Exception as e:
        return {"status": "invalid", "message": str(e)}


if __name__ == "__main__":
    """CLI for validating configuration."""
    import sys

    result = validate_settings()
    print(f"Configuration Validation: {result['status'].upper()}")

    if result["status"] == "valid":
        print(f"  API Keys: {result['api_keys_count']} configured")
        print(f"  Claude Model: {result['claude_model']}")
        print(f"  Log Level: {result['log_level']}")
        print(f"  Debug Mode: {result['debug_mode']}")
        sys.exit(0)
    else:
        print(f"  Error: {result['message']}")
        sys.exit(1)
