# Solution

A todo app: React (hooks) → Django REST API → MongoDB, all running in Docker. The original task description is preserved [below](#adbrew-test).

## Run it

```bash
cp .env.example .env        # then set ADBREW_CODEBASE_PATH to the absolute path of ./src
docker-compose build
docker-compose up -d
```

- App: http://localhost:3000 (the first start runs `yarn install` and takes a few minutes; `docker logs -f app` shows progress)
- API: http://localhost:8000/todos/

## What it does

- The list is loaded from MongoDB (`GET /todos/`).
- Submitting the form creates a todo (`POST /todos/`) and then re-fetches the list from MongoDB.
- Beyond the brief: mark a todo done (`PATCH /todos/<id>/`) and delete it (`DELETE /todos/<id>/`).
- Validation on both sides, loading and empty states, per-row pending state, a retry banner when the API is unreachable, and accessible labels and alerts.

## API

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/todos/` | | `200` list, newest first | `503` |
| POST | `/todos/` | `{"description": "..."}` | `201` created todo | `400`, `503` |
| PATCH | `/todos/<id>/` | `{"completed": true}` and/or `{"description": "..."}` | `200` updated todo | `400`, `404`, `503` |
| DELETE | `/todos/<id>/` | | `204` | `404`, `503` |

A todo is `{"id", "description", "completed", "created_at"}`. Every error has the same shape:

```json
{"error": {"code": "validation_error", "message": "'description' must not be empty.", "details": {"field": "description"}}}
```

Descriptions are trimmed and must be 1 to 200 characters. Note the trailing slash: `/todos` without it redirects (301).

## Architecture

### Backend: `src/rest/todos/`

```
request → views.py → services.py → repository.py → MongoDB
          (HTTP)     (rules)        (storage)
```

| File | Responsibility |
|---|---|
| `views.py` | Converts HTTP to service calls and back. No business logic, no database access. |
| `services.py` | Use cases: validate, persist, raise `TodoNotFoundError`. Depends on the repository *interface*. |
| `repository.py` | `TodoRepository` (abstract contract) and `MongoTodoRepository` (the only code that imports pymongo). Maps `ObjectId` to string and driver errors to `StorageError`. |
| `validators.py` | Pure input validation. |
| `domain.py` | The `Todo` dataclass, independent of HTTP and storage. |
| `exceptions.py` / `exception_handler.py` | Domain errors, mapped to HTTP status codes and a consistent JSON shape in one place. |
| `dependencies.py` | Composition root: builds one `MongoClient` (thread-safe and pooled) and wires the service once per process. |

Design patterns and principles:

- **Repository pattern.** Storage sits behind an interface. Tests swap in `InMemoryTodoRepository`, and changing the database touches only one class.
- **Service layer.** Business rules live in one place, separate from HTTP.
- **Dependency injection.** The service receives its repository, and views receive the service (`as_view(service_factory=...)`), so each layer can be tested in isolation.
- **SOLID.** Single responsibility per module. Dependency inversion, because the service depends on the abstract `TodoRepository`. Open/closed, because a new storage backend means a new class, not edits.
- **Centralized error handling.** A custom DRF `EXCEPTION_HANDLER` gives every error the same response shape, and unexpected errors are logged but never leaked to the client.

As required, there are no Django models, serializers or SQLite: all data is stored in MongoDB through the existing `MONGO_HOST`/`MONGO_PORT` configuration.

### Frontend: `src/app/src/`

| File | Responsibility |
|---|---|
| `api/httpClient.js` | `fetch` wrapper. Sends and parses JSON, and turns network failures and API errors into a single `ApiError`. |
| `api/todoApi.js` | Every todo endpoint in one module. |
| `hooks/useTodos.js` | A custom hook holding the todo state and actions. It re-fetches after every change, so the UI always matches MongoDB. It aborts the first load on unmount. |
| `components/` | Presentational components (`TodoForm`, `TodoList`, `TodoItem`, `ErrorBanner`) that receive data and callbacks through props. |
| `validation.js`, `config.js` | Client-side validation (the backend still validates everything) and configuration. |

Function components and hooks only (`useState`, `useEffect`, `useCallback`, `useRef`), with no class components or lifecycle methods. Logic lives in a **custom hook**, the UI in **presentational components**, and HTTP in an **API module**.

## Tests

```bash
docker exec api bash -c "cd /src/rest && python manage.py test todos"                 # 24 tests
docker exec app bash -c "cd /src/app && CI=true yarn test --watchAll=false"           # 6 tests
```

- Backend: validators, service (with the in-memory repository), views (status codes and error shapes, including 503 and 500), and integration tests against the real Mongo container in a throwaway database. These are skipped if Mongo is down.
- Frontend: the user flows (load, create then refresh, validation, server errors, retry, toggle and delete) with the API module mocked.

## Changes to the Docker setup

The original image no longer builds, because the base image and package mirrors have moved on since the test was written. The fixes are minimal and commented in the `Dockerfile`:

1. **`FROM python:3.8` → `python:3.8-bullseye`.** The unpinned tag now resolves to Debian 12, which lacks `libssl1.1`, a dependency of MongoDB 4.4.
2. **Removed the `bullseye-security` apt source.** Debian is retiring it, so its packages return 404.
3. **Removed `easy_install pip`.** `easy_install` no longer exists. The bundled pip 23 is kept deliberately, because pip 24.1 and later rejects `celery==5.0.5`'s malformed metadata.
4. **`CHOKIDAR_USEPOLLING=true` on the `app` service** (`docker-compose.yml`). File-change events don't cross Docker Desktop's Windows/macOS bind mounts, so without it React never hot-reloads.

Also added: `.gitignore` (Mongo data in `src/db`, `.env`, caches) and `.env.example`.

## With more time

- Pagination for `GET /todos/` and an index on `created_at`.
- Upgrade the stack (supported Python, MongoDB and Debian) instead of pinning end-of-life versions.
- Restrict CORS to known origins and move `SECRET_KEY`/`DEBUG` to environment variables for production.
- Optimistic UI updates with rollback, for snappier toggles.

---

# NOTE: DO NOT FORK THIS REPOSITORY. CLONE AND SETUP A STANDALONE REPOSITORY.

# Adbrew Test!

Hello! This test is designed to specifically test your Python, React and web development skills. The task is unconventional and has a slightly contrived setup on purpose and requires you to learn basic concepts of Docker on the fly. 


# Structure

This repository includes code for a Docker setup with 3 containers:
* App: This is the React dev server and runs on http://localhost:3000. The code for this resides in src/app directory.
* API: This is the backend container that run a Django instance on http://localhost:8000. 
* Mongo: This is a DB instance running on port 27017. Django views already have code written to connect to this instance of Mongo.

We highly recommend you go through the setup in `Dockerfile` and `docker-compose.yml`. If you are able to understand and explain the setup, that will be a huge differentiator.

# Setup
1. Clone this repository (DO NOT FORK)
```
git clone https://github.com/adbrew/test.git
```
2. Change into the cloned directory and set the environment variable for the code path. Replace `path_to_repository` appropriately.
```
export ADBREW_CODEBASE_PATH="{path_to_repository}/test/src"
```
3. Build container (you only need to build containers for the first time or if you change image definition, i.e., `Dockerfile`). This step will take a good amount of time.
```
docker-compose build
```
4. Once the build is completed, start the containers:
```
docker-compose up -d
```
5. Once complete, `docker ps` should output something like this:
```
CONTAINER ID   IMAGE               COMMAND                  CREATED         STATUS         PORTS                      NAMES
e445be7efa61   adbrew_test_api     "bash -c 'cd /src/re…"   3 minutes ago   Up 2 seconds   0.0.0.0:8000->8000/tcp     api
0fd203f12d8a   adbrew_test_app     "bash -c 'cd /src/ap…"   4 minutes ago   Up 3 minutes   0.0.0.0:3000->3000/tcp     app
884cb9296791   adbrew_test_mongo   "/usr/bin/mongod --b…"   4 minutes ago   Up 3 minutes   0.0.0.0:27017->27017/tcp   mongo
```
6. Check that you are able to access http://localhost:3000 and http://localhost:8000/todos
7. If the containers in #5 or #6 are not up, we would like you to use your debugging skills to figure out the issue. Only reach out to us if you've exhausted all possible options. The `app` container may take a good amount of time to start since it will download all package dependencies.

# Tips
1. Once containers are up and running, you can view container logs by executing `docker logs -f --tail=100 {container_name}` Replace `container_name` with `app` or `api`(output of `docker ps`)
2. You can enter the container and inspect it by executing `docker exec -it {container_name} bash` Replace `{container_name}` with `app` or `api` (output of `docker ps`)
3. Shut all containers using `docker-compose down`
4. Restart a container using `docker restart {container_name}`


# Task

When you run `localhost:3000`, you would see 2 things:
1. A form with a TODO description textbox and a submit button. On this form submission, the app should interact with the Django backend (`POST http://localhost:8000/todos`) and create a TODO in MongoDB.
2. A list with hardcoded TODOs. This should be changed to reflect TODOs in the backend (`GET http://localhost:8000/todos`). 
3. When the form is submitted, the TODO list should refresh again and fetch latest list of TODOs from MongoDB.

# Instructions [IMPORTANT] 
1. All React code should be implemented using [React hooks](https://reactjs.org/docs/hooks-intro.html) and should not use traditional stateful React components and component lifecycle method.
2. Do not use Django's model, serializers or SQLite DB. Persist and retrieve all data from the mongo instance. A `db` instance is already present in `views.py`.
3. Do not bypass the Docker setup. Submissions that do not have proper docker setup will be rejected.
4. We are looking for developers who have strong fundamentals and can ramp up fast. We expect you to learn and grasp basic React Hooks/Mongo/Docker concepts on the fly.
5. Do not fork this repository or submit your solution as a PR since this is a public repo and there are other candidates taking the same test. Send us a link to your repo privately.
6. If you are able to complete the test, we will have a live walkthrough of your code and ask questions to check your understanding.
7. The code for the actual solution is pretty easy. The code quality in your solution should be production-ready - error handling, abstractions, well-maintainable and modular code. If you're not aware, we recommend reading a bit about software design principles and applying them (both JS and Python). Here are some reading resources to get you started:
   * https://kinsta.com/blog/python-object-oriented-programming/
   * https://realpython.com/solid-principles-python/
   * https://www.toptal.com/python/python-design-patterns
