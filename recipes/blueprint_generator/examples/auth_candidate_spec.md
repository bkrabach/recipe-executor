# Authentication Component Specification

## Overview

We need an authentication component for our FastAPI service that will handle user authentication using Auth0 in production environments. It should also provide a mock implementation for development and testing environments that simulates the same behavior without requiring an actual Auth0 connection.

## Features

- Authenticate users via Auth0 in production
- Provide a mock authentication service for development
- Verify JWT tokens
- Extract user information from tokens
- Support role-based access control

## Implementation Details

The component should provide FastAPI middleware and dependency functions for protecting routes. It should verify tokens from Auth0 and extract user claims. The mock implementation should generate tokens that have the same structure and can be verified locally.

We should support different roles like "admin", "user", etc. and have decorators or utilities to check permissions.

## Dependencies

- FastAPI
- Auth0 Python SDK
- PyJWT

## Configuration

The component should be configurable via environment variables:

- AUTH_MODE: "auth0" or "mock"
- AUTH0_DOMAIN
- AUTH0_API_AUDIENCE
- AUTH0_ALGORITHMS

## Expected API

```python
# Example usage
from auth import requires_auth, get_user, requires_role

@app.get("/protected")
@requires_auth
def protected_route():
    user = get_user()
    return {"message": f"Hello, {user.name}"}

@app.get("/admin")
@requires_role("admin")
def admin_route():
    return {"message": "Admin access granted"}
```
