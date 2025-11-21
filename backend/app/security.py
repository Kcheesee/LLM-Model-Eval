"""
Rate limiting and security middleware for Model Eval Studio.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    "evaluation_create": "10/minute",  # Max 10 evaluations per minute
    "quick_eval": "30/minute",  # Max 30 quick evals per minute
    "list": "100/minute",  # Max 100 list requests per minute
    "default": "60/minute",  # Default: 60 requests per minute
}


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceeded errors with user-friendly message."""
    logging.warning(
        f"Rate limit exceeded for {request.client.host} on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down.",
            "detail": str(exc.detail),
            "retry_after": exc.headers.get("Retry-After", "60")
        },
        headers=exc.headers
    )


def get_security_headers() -> dict:
    """Get security headers to add to all responses."""
    return {
        # Prevent clickjacking
        "X-Frame-Options": "DENY",
        
        # Prevent MIME type sniffing
        "X-Content-Type-Options": "nosniff",
        
        # Enable XSS protection
        "X-XSS-Protection": "1; mode=block",
        
        # Referrer policy
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Content Security Policy (adjust for your needs)
        "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; script-src 'self'",
        
        # Permissions policy
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }


async def add_security_headers_middleware(request: Request, call_next):
    """Middleware to add security headers to all responses."""
    response = await call_next(request)
    
    # Add security headers
    for header, value in get_security_headers().items():
        response.headers[header] = value
    
    return response
