## ADDED Requirements

### Requirement: Personal Access Tokens (API Keys)
The system SHALL allow users to create and use Personal Access Tokens (PATs) for programmatic API access. PATs are scoped, revocable, optionally expiring, and stored only as hashes.

#### Scenario: Create a token successfully
- WHEN an authenticated user submits a request with a name, scopes, and optional expiration
- THEN the system SHALL create a token, return the plaintext token exactly once, and persist only its hash

#### Scenario: List tokens (metadata only)
- WHEN a user lists their tokens
- THEN the system SHALL return token metadata (id, name, created_at, expires_at, revoked_at, scopes) without the plaintext token

#### Scenario: Revoke a token
- WHEN a user revokes a token
- THEN the token SHALL no longer authenticate requests and SHALL be marked revoked

#### Scenario: Authenticate with API key
- WHEN a client provides `Authorization: Bearer <token>` or `X-API-Key: <token>`
- THEN the request SHALL be authenticated as the token’s owner if valid, not expired, and not revoked

#### Scenario: Enforce scopes
- WHEN a token without the required scope accesses a protected endpoint
- THEN the system SHALL respond with 403 Forbidden

#### Scenario: Expired or invalid token
- WHEN a token is expired or unrecognized
- THEN the system SHALL respond with 401 Unauthorized

#### Scenario: Audit logs
- WHEN a token is created or revoked
- THEN the system SHALL write an audit record including actor, action, token id, and source IP

#### Scenario: Rate limiting
- WHEN a token is used repeatedly on rate‑limited endpoints
- THEN the system SHALL apply rate limits per token (in addition to any IP limits)
