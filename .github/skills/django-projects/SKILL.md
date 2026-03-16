---
name: django-projects
description: 'Plan, scaffold, implement, and verify Django projects and features. Use for new Django apps, CRUD modules, API + template flows, model/schema changes, migrations, forms, auth, and production-ready quality checks.'
argument-hint: 'What Django feature or project outcome do you want to build?'
user-invocable: true
---

# Django Projects Workflow

## What This Skill Produces
- A complete, repeatable workflow to build or extend Django projects safely.
- Clear decision points for app structure, API vs template-first delivery, and data modeling choices.
- A done checklist that confirms migrations, tests, and runtime behavior are correct.
- Opinionated defaults for templates + DRF, JWT auth, Celery jobs, and Docker/Postgres delivery.

## Default Stack Profile
- Web: Django templates + forms for server-rendered user journeys.
- API: DRF serializers + API views/viewsets for programmatic access.
- Auth: JWT for API authentication, session auth for template flows when needed.
- Async: Celery for background tasks and scheduled jobs.
- Runtime: Dockerized services with Postgres as the primary database.

## When to Use
- Creating a new Django project or adding a new app.
- Building model-driven CRUD features.
- Adding Django REST Framework APIs.
- Introducing auth, forms, admin, and template pages.
- Refactoring with schema changes that require migrations and data safety.

## Inputs to Gather First
- Product goal: exact user-visible outcome.
- Delivery mode: server-rendered templates, API-first, or hybrid.
- Data entities and relationships.
- Access rules: public, authenticated, staff/admin.
- Non-functional constraints: performance, security, deployment target.

## Decision Points
1. Template-first or API-first?
- Template-first: prioritize views, forms, templates, URL routes, and server-side validation.
- API-first: prioritize serializers, viewsets/views, API routing, auth, pagination, and filtering.
- Hybrid: implement shared domain logic in models/services, then expose both surfaces.
- Default: hybrid, unless product constraints require one surface only.

2. Single app or multiple apps?
- Single app: use when scope is small and tightly cohesive.
- Multiple apps: split by domain boundaries (accounts, properties, enquiries, etc.) when models and permissions differ.

3. Business logic placement?
- Keep invariants near models when strongly data-coupled.
- Use service/helper layer for multi-model workflows.
- Keep views/controllers thin and orchestration-focused.

4. Data migration strategy?
- Backward-compatible additive change: deploy in one migration sequence.
- Breaking change: use staged migrations and compatibility windows.

5. Auth and async boundaries?
- JWT: required on API mutating endpoints unless explicitly public.
- Session auth: acceptable for template-only authenticated pages.
- Celery: use for non-request-critical work (emails, heavy processing, scheduled jobs).

## Procedure
1. Define scope and acceptance criteria
- Write 3-7 acceptance checks in behavior terms.
- Map each check to URL/API endpoints, models, and permissions.

2. Model and schema design
- Draft entities, fields, constraints, indexes, and relationships.
- Define validation boundaries and default values.
- Create/update models and generate migrations.

3. Implement domain logic
- Add model methods/managers for reusable query logic.
- Add service functions for multi-step business workflows when needed.

4. Build delivery layer
- Template flow: forms, class/function views, URL patterns, templates, success/error states.
- API flow: serializers, API views/viewsets, routers/urls, status codes, pagination/filtering.
- Ensure authorization checks exist in every mutating path.
- Add JWT auth configuration and permission classes for protected API endpoints.

5. Admin and operability
- Register/admin-tune models for internal operations.
- Add useful list display/search/filter fields in admin when relevant.

6. Background jobs and integrations
- Define Celery tasks for non-blocking operations.
- Keep tasks idempotent and retry-safe where side effects exist.
- Trigger tasks from service layer or post-commit hooks when appropriate.

7. Test and verify
- Add tests for models, permissions, happy path, and edge cases.
- Run migrations locally and validate no regressions in existing endpoints/pages.
- Validate form and serializer error behavior.
- Validate JWT-protected endpoints for both authorized and unauthorized requests.
- Validate Celery task behavior for success, retry, and failure paths.

8. Final hardening
- Check settings split/environment variables and secrets handling.
- Review static/media handling and upload safety.
- Confirm logging and error pages are acceptable for environment.
- Verify Docker Compose services and Postgres connectivity for local run.

## Completion Criteria
- All acceptance criteria are mapped to implemented code paths.
- Migrations apply cleanly on a fresh and existing database.
- Permissions are enforced for all protected operations.
- Tests pass for changed areas and key regressions.
- API/template behavior matches documented success and failure responses.
- No obvious security regressions (CSRF, auth checks, unsafe file handling, debug leakage).
- JWT auth behavior is explicit and tested for protected endpoints.
- Celery tasks are observable and safe to retry.
- Docker/Postgres local environment starts cleanly for the affected feature.

## Quick Invocation Examples
- /django-projects Build a new enquiries module with create/list/detail and staff-only update/delete.
- /django-projects Add REST endpoints for properties with filtering, pagination, and token auth.
- /django-projects Refactor wishlist model with a staged migration and regression tests.
