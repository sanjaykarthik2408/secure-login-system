# Secure Login App

A small, production-minded authentication starter built with **Node.js, Express, SQLite, and plain HTML/CSS/JavaScript**. It uses Node.js 24's built-in SQLite support, so Windows users do not need to compile a native database addon. Plain frontend files keep the example easy to audit; React is useful when the UI grows, but is not necessary for these pages.

## Features

- Registration and login with email/username
- bcrypt password hashing with 12 salt rounds; plaintext passwords are never stored
- Input validation, prepared SQLite statements, security headers, request-size limits
- Server-side file-backed sessions using `httpOnly`, `sameSite=lax`, secure-in-production cookies and 30-minute rolling inactivity expiry
- Login and sensitive-action rate limits
- Optional TOTP 2FA setup, verification, and disable flow compatible with Authy/Google Authenticator
- Session ID regeneration after registration/login and proper session destruction on logout

## Quick start

1. Install Node.js 24+ (this project uses Node's built-in SQLite module).
2. Copy `.env.example` to `.env` and set a unique long `SESSION_SECRET` (at least 32 characters).
3. Install dependencies: `npm install`
4. Run locally: `npm start`
5. Visit `http://localhost:3000`.

For local HTTP development leave `COOKIE_SECURE=false`. In production, terminate TLS before the app or at a trusted proxy, set `NODE_ENV=production`, and set `COOKIE_SECURE=true`.

## Routes

| Route | Purpose |
| --- | --- |
| `POST /register` | Create account and sign in |
| `POST /login` | Password verification; may require 2FA |
| `POST /verify-2fa` | Complete login with TOTP |
| `POST /logout` | Destroy server-side session |
| `POST /enable-2fa` | Generate a pending secret and QR code |
| `POST /confirm-2fa` | Verify and activate generated 2FA secret |
| `POST /disable-2fa` | Disable 2FA after a valid TOTP code |
| `GET /api/me` | Current authenticated user |

## Database schema

The app creates `data/app.db` automatically. Its `users` table contains `email`, `username`, `hashed_password`, `two_factor_secret`, `two_factor_enabled`, and timestamps. All values in database queries are bound parameters; no user value is interpolated into SQL. Server-side session files are stored separately under `data/sessions`.

## Production checklist

- Enforce HTTPS and use a securely stored, rotated session secret.
- Add CSRF protection for cookie-authenticated state-changing endpoints (for example, synchronizer tokens or a vetted CSRF middleware) before cross-origin embedding/API use.
- Store TOTP secrets encrypted at rest with application-managed encryption keys; this demo stores the Base32 secret in SQLite for clarity.
- Use PostgreSQL and a shared session store such as Redis for multi-instance deployment.
- Add email verification, password-reset tokens that are hashed and short-lived, breach-password checks, audit logs, monitoring, backup codes, and account-recovery policies.
- Put the app behind a reverse proxy/WAF, configure CSP specifically for the deployed frontend, and regularly update dependencies.
