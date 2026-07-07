"""
Rate limiting configuration.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address


# SlowAPI reads ".env" with the platform default encoding when config_filename is
# omitted. Use a non-existent config file so application settings stay centralized
# in app.core.config, which reads .env as UTF-8.
limiter = Limiter(key_func=get_remote_address, config_filename=".slowapi.env")
