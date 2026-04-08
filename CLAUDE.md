# CLAUDE.md — Backend (Cover: Mobile Cover E‑Commerce)

This file is the contract Claude must follow when working in `backend/`. It pairs with [../frontend/CLAUDE.md](../frontend/CLAUDE.md).

---

## 1. Stack

- **Django 5.2** + **Django REST Framework 3.16**
- **Auth:** `rest_framework.authtoken` (Token auth) + `django-allauth` for sessions/admin
- **DB:** PostgreSQL via `psycopg2-binary`, configured by `DATABASE_URL`
- **Media:** Pillow for image uploads, served from `MEDIA_URL` in dev
- **Schema:** `drf-spectacular` (OpenAPI), `drf-standardized-errors`
- **Filtering:** `django-filter`
- **Admin:** `jazzmin` themed
- **Tasks:** Celery + Redis (don't use unless asked)
- **Runs in Docker** via `docker-compose.local.yml`. The local `.venv/` is minimal — never assume a local `python manage.py` works.

---

## 2. Project Layout (Two-Cookiecutter Style)

```
backend/
├── backend/                  # Source root
│   ├── users/                # Pre-existing custom user app
│   ├── core/                 # Shared mixins, base classes, generics
│   ├── catalog/              # Categories + Products + ProductImages
│   ├── orders/               # Orders + OrderItems
│   ├── expenses/             # Expense tracking (online + offline)
│   ├── contrib/
│   ├── static/
│   └── templates/
├── config/
│   ├── settings/             # base.py, local.py, production.py, test.py
│   ├── api_router.py         # Mounts every app's API router under /api/
│   ├── urls.py               # Root URL conf
│   └── celery_app.py
├── compose/                  # Dockerfiles for local + production
├── requirements/             # base.txt, local.txt, production.txt
├── manage.py
└── docker-compose.local.yml
```

### App skeleton

Every app under `backend/<name>/` follows this layout:

```
backend/<name>/
├── __init__.py
├── apps.py                   # AppConfig with name = "backend.<name>"
├── models.py
├── admin.py
├── api/
│   ├── __init__.py
│   ├── serializers.py        # ModelSerializers, snake_case (DRF convention)
│   ├── views.py              # ViewSets
│   └── urls.py               # router.register(...) → exposed via api_router
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

---

## 3. URL Convention

All API routes live under `/api/`. Each app exposes its router via `config/api_router.py`:

```python
# config/api_router.py
from rest_framework.routers import DefaultRouter
from backend.users.api.views import UserViewSet
from backend.catalog.api.views import CategoryViewSet, ProductViewSet
from backend.orders.api.views import OrderViewSet
from backend.expenses.api.views import ExpenseViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("catalog/categories", CategoryViewSet, basename="category")
router.register("catalog/products",   ProductViewSet,  basename="product")
router.register("orders/orders",      OrderViewSet,    basename="order")
router.register("expenses/expenses",  ExpenseViewSet,  basename="expense")
```

So the frontend hits:

| Resource     | URL                               |
|--------------|-----------------------------------|
| Categories   | `GET /api/catalog/categories/`    |
| Products     | `GET /api/catalog/products/`      |
| Product detail | `GET /api/catalog/products/<slug>/` |
| Orders       | `GET/POST /api/orders/orders/`    |
| Expenses     | `GET/POST /api/expenses/expenses/` |
| Login        | `POST /api/login/`                |
| Register     | `POST /api/register/`             |
| Me           | `GET /api/users/me/`              |

`lookup_field = "slug"` for products and categories so URLs are human‑readable.

---

## 4. Naming Conventions

- **Apps:** singular‑plural mix is fine (`catalog`, `orders`, `expenses`). App config name is always `backend.<app>`.
- **Models:** PascalCase singular (`Product`, `Category`, `Order`, `OrderItem`, `Expense`).
- **Fields:** `snake_case` — never camelCase. `price_per_unit`, `is_active`, `compatible_with`.
- **Serializers:** `<Model>Serializer`. Use `ModelSerializer` by default.
- **ViewSets:** `<Model>ViewSet`. Inherit `viewsets.ModelViewSet` for full CRUD or compose mixins.
- **URL basenames:** singular (`category`, `product`, `order`, `expense`).

---

## 5. Permissions Pattern

| Resource | List/Retrieve | Create/Update/Delete |
|---|---|---|
| `catalog/categories` | `AllowAny` | `IsAdminUser` |
| `catalog/products`   | `AllowAny` | `IsAdminUser` |
| `orders/orders`      | Authenticated, scoped to `request.user` (or `IsAdminUser` to see all) | Authenticated for create; staff for status updates |
| `expenses/expenses`  | `IsAdminUser` only | `IsAdminUser` only |

Use a small `get_permissions()` override pattern when actions need different rules:

```python
def get_permissions(self):
    if self.action in ("list", "retrieve"):
        return [AllowAny()]
    return [IsAdminUser()]
```

---

## 6. Serializer Rules

- Always set `fields = [...]` explicitly. Never `__all__`.
- Read-only computed fields go into a `SerializerMethodField`.
- Image fields return absolute URLs by using `serializers.ImageField` and ensuring the request is in context (DRF does this automatically when called from a ViewSet).
- For nested writes (e.g. `OrderItem` inside `Order`), accept a list in `create()` and override `perform_create` on the viewset.
- Match the field names in [../frontend/src/domain/interfaces/](../frontend/src/domain/interfaces/) `*Api` interfaces — these are the contract.

---

## 7. Migrations

- Hand-write migrations only when an automated tool is unavailable. Otherwise:
  ```bash
  docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations <app>
  docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
  ```
- Initial migrations are committed. Never edit a migration after it's been applied to production.

---

## 8. Adding a New App — Recipe

1. `mkdir backend/<name>` and create `__init__.py`, `apps.py` with `name = "backend.<name>"`.
2. Add `"backend.<name>"` to `LOCAL_APPS` in `config/settings/base.py`.
3. Create `models.py`, run `makemigrations <name>`.
4. Create `api/serializers.py`, `api/views.py`, `api/urls.py` (optional).
5. Register router in `config/api_router.py`.
6. Wire admin in `admin.py`.
7. Add seed data via a management command in `backend/<name>/management/commands/seed_<name>.py` or a fixture.
8. Write the matching frontend `apiRepository`, replace mock service body, done.

---

## 9. Things NOT to Do

- ❌ Don't use `__all__` in serializers — explicit `fields`.
- ❌ Don't return camelCase from the API — that's the frontend mapper's job.
- ❌ Don't put business logic in views — push it into the model or a service helper.
- ❌ Don't bypass the `api_router` by adding ad‑hoc URL patterns.
- ❌ Don't run `python manage.py` against the local `.venv/` — it's incomplete. Always go through Docker.
- ❌ Don't commit secret values into `.env` examples; use `.env.template` only.
- ❌ Don't forget to add `MEDIA_URL` / `MEDIA_ROOT` handling when introducing image fields.
- ❌ Don't drop pre-existing user data when changing `AUTH_USER_MODEL` — it's already set to `users.User`.

---

## 10. Definition of Done

A backend change is "done" when:
1. Models defined, migrations created and committed
2. Serializer + ViewSet + URL registration in place
3. Admin registered (so the owner can manage data via /admin/)
4. Permissions enforced
5. Frontend `apiRepository` + service updated to use the real endpoint
6. `python manage.py check` passes (run via Docker)
7. The endpoint is reachable at `/api/docs/` (Swagger)
