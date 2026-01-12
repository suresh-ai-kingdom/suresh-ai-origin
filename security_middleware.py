"""Security middleware for Flask app - adds security headers to responses."""
from flask import g
import time


def add_security_headers(response):
    """Add security headers to all responses."""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy (adjust based on your needs)
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'"
    )
    
    # Permissions Policy (formerly Feature-Policy)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=()"
    )
    
    return response


def add_response_time_header(response):
    """Add X-Response-Time header for monitoring."""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{elapsed:.3f}s"
    return response


def init_security_middleware(app):
    """Initialize security middleware for the Flask app."""
    
    @app.before_request
    def before_request():
        """Record request start time."""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Add security headers and response time to all responses."""
        response = add_security_headers(response)
        response = add_response_time_header(response)
        return response
    
    app.logger.info("Security middleware initialized")
