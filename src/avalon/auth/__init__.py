"""Authentication guards and middleware (M7)."""

from __future__ import annotations

from avalon.auth.authenticatable import AuthenticatableMixin
from avalon.auth.contracts import Authenticatable, UserProvider
from avalon.auth.events import (
    Attempting,
    Authenticated,
    Failed,
    Login,
    Logout,
    OtherDeviceLogout,
    PasswordReset,
    Validated,
    dispatch,
    forget,
    listen,
)
from avalon.auth.guard import (
    AuthManager,
    Guard,
    SessionGuard,
    TokenGuard,
    auth,
    guest,
    pull_intended_url,
    store_intended_url,
)
from avalon.auth.middleware import (
    Authenticate,
    AuthenticateWithBasicAuth,
    RedirectIfAuthenticated,
    RequirePassword,
    StartAuth,
    mark_password_confirmed,
)
from avalon.auth.passwords import Password
from avalon.auth.providers import ArticulateUserProvider, MemoryUserProvider

__all__ = [
    "ArticulateUserProvider",
    "Attempting",
    "AuthManager",
    "Authenticate",
    "AuthenticateWithBasicAuth",
    "Authenticated",
    "Authenticatable",
    "AuthenticatableMixin",
    "Failed",
    "Guard",
    "Login",
    "Logout",
    "MemoryUserProvider",
    "OtherDeviceLogout",
    "Password",
    "PasswordReset",
    "RedirectIfAuthenticated",
    "RequirePassword",
    "SessionGuard",
    "StartAuth",
    "TokenGuard",
    "UserProvider",
    "Validated",
    "auth",
    "dispatch",
    "forget",
    "guest",
    "listen",
    "mark_password_confirmed",
    "pull_intended_url",
    "store_intended_url",
]
