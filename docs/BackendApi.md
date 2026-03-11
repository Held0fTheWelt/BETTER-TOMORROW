# Backend API – Overview

The backend API is served under the prefix **`/api/v1`**. All responses are JSON. Protected endpoints expect the header **`Authorization: Bearer <JWT>`**.

---

## Overview

| Area     | Endpoints                                                                 |
|----------|---------------------------------------------------------------------------|
| **Auth** | Register, Login, Me                                                       |
| **System** | Health, Test Protected                                                   |
| **Users** | List (GET, Admin), Get (GET), Update (PUT), Delete (DELETE, Admin)       |
| **News** | List (GET), Detail (GET), Create (POST), Update (PUT), Delete, Publish, Unpublish |

---

## 1. Auth

### 1.1 Register – Create user

**`POST /api/v1/auth/register`**

Creates a new user. Email is required. After registration an email verification token is created and a verification email is sent (or only logged in dev when `MAIL_ENABLED` is off). The user can log in only after clicking the activation link.

- **Rate limit:** 10 per minute  
- **Auth:** None  

**Request body (JSON):**

| Field      | Type   | Required | Description                          |
|------------|--------|----------|--------------------------------------|
| `username` | string | yes      | Unique, 2–80 chars, `a-zA-Z0-9_-`     |
| `email`    | string | yes      | Unique, valid format                 |
| `password` | string | yes      | Min. 8 chars, upper/lowercase, digit |

**Response:**

- **201 Created:** `{ "id": <number>, "username": "<string>" }`
- **400 Bad Request:** `{ "error": "<message>" }` (e.g. invalid password, missing fields)
- **409 Conflict:** `{ "error": "Username already taken" }` or `"Email already registered"`

---

### 1.2 Login – Get JWT

**`POST /api/v1/auth/login`**

Authenticates with username and password and returns a JWT and user data. Only possible if the user's email is verified (see 0.0.7).

- **Rate limit:** 20 per minute  
- **Auth:** None  

**Request body (JSON):**

| Field      | Type   | Required | Description |
|------------|--------|----------|-------------|
| `username` | string | yes      | Username    |
| `password` | string | yes      | Password    |

**Response:**

- **200 OK:**  
  `{ "access_token": "<JWT>", "user": { "id": <number>, "username": "<string>", "role": "<string>" } }`
- **400 Bad Request:** `{ "error": "Invalid or missing JSON body" }` or `"Username and password are required"`
- **401 Unauthorized:** `{ "error": "Invalid username or password" }`
- **403 Forbidden:** `{ "error": "Email not verified." }` – email not yet confirmed

---

### 1.3 Me – Current user

**`GET /api/v1/auth/me`**

Returns the user identified by the JWT.

- **Rate limit:** 60 per minute  
- **Auth:** Bearer JWT (required)  

**Response:**

- **200 OK:** `{ "id": <number>, "username": "<string>", "role": "<string>" }`  
  Possible roles: `user`, `editor`, `admin`.
- **401 Unauthorized:** Missing or invalid token: `{ "error": "Authorization required. Missing or invalid token." }` or `"Invalid or expired token."`
- **404 Not Found:** `{ "error": "User not found" }` (token valid but user no longer in DB)

---

## 2. System

### 2.1 Health – API status

**`GET /api/v1/health`**

Simple API health check.

- **Rate limit:** 100 per minute  
- **Auth:** None  

**Response:**

- **200 OK:** `{ "status": "ok" }`

---

### 2.2 Test Protected – Protected route (example)

**`GET /api/v1/test/protected`**

Example of a protected route. Callable only with a valid JWT.

- **Rate limit:** 60 per minute  
- **Auth:** Bearer JWT (required)  

**Response:**

- **200 OK:**  
  `{ "message": "ok", "user_id": <number>, "username": "<string>" }`
- **401:** Same as Me (missing/invalid token)

---

## 3. News

Public read endpoints (list, detail) require no auth. Write and status changes (Create, Update, Delete, Publish, Unpublish) require JWT and role **editor** or **admin**; otherwise 401 (no token) or 403 (Forbidden).

---

### 3.1 News List – List published articles

**`GET /api/v1/news`**

Returns a paginated list of **published** articles only. Unpublished or scheduled articles are not included.

- **Rate limit:** 60 per minute  
- **Auth:** None  

**Query parameters:**

| Parameter  | Type   | Default        | Description                                      |
|------------|--------|----------------|--------------------------------------------------|
| `q`        | string | –              | Search term (searches title/content)            |
| `sort`     | string | `published_at` | Sort: `published_at`, `created_at`, `updated_at`, `title` |
| `direction`| string | `desc`         | `asc` or `desc`                                 |
| `page`     | int    | 1              | Page number (≥ 1)                                |
| `limit`    | int    | 20             | Items per page (1–100)                           |
| `category` | string | –              | Filter by category                               |

**Response:**

- **200 OK:**  
  `{ "items": [ <news object>, ... ], "total": <number>, "page": <number>, "per_page": <number> }`

**News object (excerpt):**  
`id`, `title`, `slug`, `summary`, `content`, `author_id`, `author_name`, `is_published`, `published_at` (ISO-8601), `created_at`, `updated_at`, `cover_image`, `category`

---

### 3.2 News Detail – Get single article

**`GET /api/v1/news/<id>`**

Returns a published article by numeric ID. Unpublished or scheduled articles return 404.

- **Rate limit:** 60 per minute  
- **Auth:** None  

**Response:**

- **200 OK:** A single news object (same fields as in list).
- **404 Not Found:** `{ "error": "Not found" }`

---

### 3.3 News Create – Create article

**`POST /api/v1/news`**

Creates a new news article. Author is taken from the JWT identity.

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT, role **editor** or **admin**  

**Request body (JSON):**

| Field          | Type   | Required | Description           |
|----------------|--------|----------|-----------------------|
| `title`        | string | yes      | Title                 |
| `slug`         | string | yes      | Unique URL slug       |
| `content`      | string | yes      | Content (text)        |
| `summary`      | string | no       | Short summary         |
| `is_published` | bool   | no       | Default: false        |
| `cover_image`  | string | no       | URL or path           |
| `category`     | string | no       | Category              |

**Response:**

- **201 Created:** The created news object.
- **400 Bad Request:** `{ "error": "title, slug, and content are required" }` or other validation errors.
- **401/403:** No token or role not editor/admin.
- **409 Conflict:** `{ "error": "Slug already in use" }`

---

### 3.4 News Update – Edit article

**`PUT /api/v1/news/<id>`**

Updates an existing article. Only provided fields are changed.

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT, role **editor** or **admin**  

**Request body (JSON):** All fields optional: `title`, `slug`, `summary`, `content`, `cover_image`, `category`.

**Response:**

- **200 OK:** The updated news object.
- **400/401/403:** Same as Create.
- **404 Not Found:** `{ "error": "News not found" }`
- **409 Conflict:** `{ "error": "Slug already in use" }`

---

### 3.5 News Delete – Delete article

**`DELETE /api/v1/news/<id>`**

Deletes an article.

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT, role **editor** or **admin**  

**Response:**

- **200 OK:** `{ "message": "Deleted" }`
- **404 Not Found:** `{ "error": "<message>" }`
- **401/403:** Same as above.

---

### 3.6 News Publish – Publish article

**`POST /api/v1/news/<id>/publish`**

Sets the article to "published" (and `published_at` to now).

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT, role **editor** or **admin**  

**Response:**

- **200 OK:** The updated news object (with `is_published: true`, `published_at` set).
- **404:** Article not found.
- **401/403:** Same as above.

---

### 3.7 News Unpublish – Unpublish article

**`POST /api/v1/news/<id>/unpublish`**

Sets the article to "not published" (`is_published: false`, `published_at` optionally cleared).

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT, role **editor** or **admin**  

**Response:**

- **200 OK:** The updated news object.
- **404/401/403:** Same as Publish.

---

## 4. Users (CRUD)

All user endpoints require **Bearer JWT**. **List** and **Delete** are for **admin** role only; **Get** and **Update** for Admin (any user) or for the current user (Self).

### 4.1 Users List – List users (Admin)

**`GET /api/v1/users`**

Paginated list of all users. **Admin** only.

- **Rate limit:** 60 per minute  
- **Auth:** Bearer JWT, role **admin**  

**Query parameters:**

| Parameter | Type   | Default | Description                |
|-----------|--------|---------|----------------------------|
| `page`    | int    | 1       | Page number (≥ 1)          |
| `limit`   | int    | 20      | Items per page (1–100)     |
| `q`       | string | –       | Search in username/email   |

**Response:**

- **200 OK:** `{ "items": [ { "id", "username", "role", "email" }, ... ], "total", "page", "per_page" }`
- **403:** Not admin

---

### 4.2 Users Get – Get one user

**`GET /api/v1/users/<id>`**

Single user: **Admin** may fetch any user; otherwise only the **current** user's profile (`id` = JWT user). For self and for admin, the response includes `email`.

- **Rate limit:** 60 per minute  
- **Auth:** Bearer JWT (Admin or Self)  

**Response:**

- **200 OK:** `{ "id", "username", "role" }` or including `"email"` (see above)
- **403:** Other user, not admin
- **404:** User not found

---

### 4.3 Users Update – Edit user

**`PUT /api/v1/users/<id>`**

Update user: **Admin** may update any user and may set `role`; otherwise only **own** profile (no `role`). Body: all fields optional.

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT (Admin or Self)  

**Request body (JSON):**

| Field               | Type   | Description                                              |
|---------------------|--------|----------------------------------------------------------|
| `username`          | string | New username (unique, 2–80 chars, `a-zA-Z0-9_-`)         |
| `email`             | string | New email (unique, valid format)                         |
| `password`          | string | New password (same rules as registration)                |
| `current_password`  | string | Required when changing **own** password                  |
| `role`              | string | **Admin** only: `user`, `editor`, `admin`                |

**Response:**

- **200 OK:** Updated user object (same as Get, including `email` when Admin/Self)
- **400:** Validation error, e.g. "Current password is incorrect"
- **403:** No permission for this user
- **404:** User not found
- **409:** "Username already taken" or "Email already registered"

---

### 4.4 Users Delete – Delete user (Admin)

**`DELETE /api/v1/users/<id>`**

Permanently delete a user. **Admin** only. The user's news entries are kept; `author_id` is set to `null`.

- **Rate limit:** 30 per minute  
- **Auth:** Bearer JWT, role **admin**  

**Response:**

- **200 OK:** `{ "message": "Deleted" }`
- **403:** Not admin
- **404:** User not found

---

## 5. General

### 5.1 Authentication

- Protected endpoints expect the header: **`Authorization: Bearer <access_token>`**  
  The token is obtained from **`POST /api/v1/auth/login`**.
- Invalid or expired token: **401** with JSON `error`.
- Valid token but insufficient rights (e.g. role `user` for news write): **403 Forbidden**.

### 5.2 Error responses

- API errors are JSON: `{ "error": "<message>" }`.
- Missing or invalid JSON body: **400** with corresponding `error` message.

### 5.3 CORS

- When frontend and backend use different origins, **CORS_ORIGINS** must be set in the backend (e.g. `http://localhost:5001,http://127.0.0.1:5001`) so the browser allows API requests.

### 5.4 Rate limits

- Per-endpoint limits are as stated above (e.g. 10/min Register, 20/min Login, 60/min Health/News List). Exceeding them typically returns **429 Too Many Requests** (depending on config).
