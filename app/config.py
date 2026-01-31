import os

from werkzeug.middleware.proxy_fix import ProxyFix


def parse_bool(value):
    return str(value).lower() in ("1", "true", "yes")


def parse_cors_origins(value):
    if not value:
        return None
    value = value.strip()
    if value == "*":
        return "*"
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def configure_app(app):
    app_env = os.environ.get("APP_ENV", "development").lower()
    is_production = app_env == "production"

    secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key and is_production:
        raise RuntimeError("FLASK_SECRET_KEY must be set in production.")
    if not secret_key:
        secret_key = os.urandom(24)

    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["IS_PRODUCTION"] = is_production
    if is_production:
        app.config["SESSION_COOKIE_SECURE"] = True

    if parse_bool(os.environ.get("USE_PROXY_FIX")):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    return is_production


def get_socketio_cors_origins():
    return parse_cors_origins(os.environ.get("SOCKETIO_CORS_ORIGINS"))


def get_runtime_options(app):
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug_flag = parse_bool(os.environ.get("FLASK_DEBUG"))
    if app.config.get("IS_PRODUCTION"):
        debug_flag = False
    return host, port, debug_flag
