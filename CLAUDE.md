# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**SIT – Sistema Integral de Titulación.** A full-stack web application for managing the graduation (titulación) process at a TECNM campus. Coordinators register graduates, academics review documents, and graduates track their own process through several administrative milestones.

## Tech Stack

- **Backend:** Kotlin + Spring Boot 4.0.3, Java 21, MongoDB (remote at 77.37.74.122:27017), JWT (JJWT 0.12.6)
- **Frontend:** Angular 18, TypeScript 5.4, sessionStorage-based JWT auth
- **Infra (prod):** Nginx reverse proxy + systemd service on Linux; no Docker

## Commands

### Backend
```bash
# Development (port 8081)
./gradlew bootRun --args='--spring.profiles.active=dev'

# Build JAR for production
./gradlew bootJar
# → build/libs/sit-0.0.1-SNAPSHOT.jar

# Tests
./gradlew test
```

### Frontend
```bash
cd frontend
npm install

# Development server (port 4200, proxies /api → localhost:8081)
npm start

# Production build
npm run build
# → frontend/dist/sit-frontend/browser/
```

## Architecture

### Auth Flow
1. `POST /api/auth/login` → backend validates BCrypt password → returns `{username, rol, access_token}`
2. Token stored in `sessionStorage` (per-tab, intentionally not shared across tabs)
3. Angular `authInterceptor` (`frontend/src/app/interceptors/auth.interceptor.ts`) adds `Authorization: Bearer <token>` to every request
4. `JwtAuthenticationFilter` validates the token and populates Spring's `SecurityContext`
5. `GET /api/auth/me` is used by Angular guards to verify session and get current role

### Role-Based Routing
Roles: `coordinador`, `academico`, `egresado`, `apoyo_titulacion`, `servicios_escolares`.
Route guards in `frontend/src/app/guards/auth.guard.ts` call `auth.me()` and redirect based on role. Each role has its own set of pages; unauthorized access goes to `/login`.

### Backend Layer Structure
```
domain/       → MongoDB @Document models (Egresado → "registro", Usuario → "usuarios", Revision → "revisiones")
repository/   → Spring Data interfaces
service/      → Business logic (EgresadoService, EmailService, HtmlAnexoPdfService, etc.)
security/     → JwtService + JwtAuthenticationFilter
web/api/      → REST controllers (AuthController, EgresadoController) + DTOs + GlobalExceptionHandler
config/       → SecurityConfig (CORS, CSRF-off, stateless session), MongoConfig, seed runners
```

### Key Domain Entity
`Egresado` is the central document. It embeds `DatosPersonales`, `DatosProyecto`, `Documentos`, `DocumentoAdjunto`, `SinodalesTribunal`, and holds 10+ `Instant` timestamp fields that track each milestone in the titulación process.

### Dev Proxy
`frontend/proxy.conf.js` proxies `/api` → `http://localhost:8081` and rewrites `Set-Cookie` Domain headers so cookies work on `localhost` during development. The `dev` Spring profile enables compatible cookie settings.

## Configuration

`src/main/resources/application.properties` contains:
- MongoDB URI with the remote host
- JWT secret (env var `SIT_JWT_SECRET`, defaults to a dev placeholder)
- Gmail SMTP credentials for email notifications
- Path to LibreOffice binary for PDF generation (`sit.soffice.path`)

Default users are seeded on startup by `SeedCoordinadorRunner` and `SeedAcademicoRunner`.

## Docs
- `docs/ESTRUCTURA.md` — detailed architecture reference
- `docs/DEPLOY.md` — step-by-step production deployment (SCP, systemd, Nginx config)
- `docs/MONGODB-PERSISTENCIA.md` — database backup strategy
- `docs/USUARIO-COORDINADOR.md` — default users and roles
