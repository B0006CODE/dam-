## 1. Implementation
- [ ] 1.1 DB: Add `api_keys` table (SQLite) and migration logic
- [ ] 1.2 Models: Pydantic schemas (create/list/item) and hashing utilities
- [ ] 1.3 Router: `POST/GET/DELETE /api/auth/api-keys` endpoints
- [ ] 1.4 Auth: Accept `X-API-Key` / `Bearer` in middleware, attach user + scopes to request
- [ ] 1.5 Scopes: Map endpoint groups to required scopes and enforce
- [ ] 1.6 Rate limiting: Track per API key in addition to per IP (where applicable)
- [ ] 1.7 Audit logs for create/revoke

## 2. Tests
- [ ] 2.1 Unit: token creation, hashing, scope parsing, expiration
- [ ] 2.2 API: create/list/revoke happy paths + error cases
- [ ] 2.3 Auth: use API key to access endpoints within scope; deny outside scope
- [ ] 2.4 Rate limit: ensure per‑key limits applied

## 3. Documentation
- [ ] 3.1 User guide: how to create/revoke/list PATs; show‑once behavior
- [ ] 3.2 API docs: headers, examples, scope list, HTTP statuses
- [ ] 3.3 Security notes: storage as hash, rotation, expiry, audits

## 4. Deployment
- [ ] 4.1 Add migration to startup path; verify idempotency
- [ ] 4.2 Backward‑compatible: JWT continues to work unchanged
