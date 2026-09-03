"""Application configuration."""

from avalon.config import env

config = {
    "name": env("APP_NAME", "Progress"),
    "env": env("APP_ENV", "local"),
    "debug": env("APP_DEBUG", True),
    "url": env("APP_URL", "http://127.0.0.1:3000"),    "providers": [
        "app.Providers.AppServiceProvider.AppServiceProvider",
    ],
}
