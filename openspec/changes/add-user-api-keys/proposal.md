# Change: Add Personal Access Tokens (API Keys) for Programmatic Access

## Why
Enable safe programmatic access for integrations, automation, and headless clients without sharing user passwords or UI JWTs. This also supports CI jobs and service-to-service traffic with revocable, scoped credentials.

## What Changes
- New API endpoints under `/api/auth/api-keys`:
  - `POST /api/auth/api-keys` — create a token (name, scopes, optional expiration); returns plaintext token once
  - `GET /api/auth/api-keys` — list tokens for current user (no plaintext, metadata only)
  - `DELETE /api/auth/api-keys/{id}` — revoke a token (soft delete)
- Authentication middleware updates:
  - Accept `Authorization: Bearer <api_key>` or `X-API-Key: <api_key>` for API routes
  - Enforce scopes per endpoint group (e.g., `chat:read`, `kb:write`, `graph:read`, `admin:*`)
  - PATs do not create UI sessions and cannot be used to log in to the web app
- Database: new `api_keys` table with `id, user_id, name, hashed_key, scopes[], created_at, expires_at, revoked_at`
- Rate limiting: apply per API key as well as per IP for protected endpoints
- Audit logging: record create/revoke events with actor and IP

## Impact
- Affected specs: `auth` capability
- Affected code: `server/routers/auth_router.py`, `server/utils/auth_middleware.py`, `src/storage/db/models.py`, `server/utils/migrate.py`, tests under `test/api`
