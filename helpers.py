import logging
import os
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration


def DB_ENABLED() -> bool:
    return os.getenv('DATABASE_URL') is not None


def in_production() -> bool:
    return os.getenv('BOT_NAME', None) is not None


def enable_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def init_sentry() -> None:
    sentry_dsn = os.getenv('SENTRY_DSN', None)

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                AsyncioIntegration(),
            ],
        )


__all__ = [
    'DB_ENABLED',
    'enable_logging',
    'in_production',
    'init_sentry',
]
