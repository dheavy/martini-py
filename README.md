# MARTINI 🍸

Backend engine to build Large Language Model (LLM)-based applications, providing frontend clients with API endpoints for "chat with your PDF" functionality (and more to come).

**Martini is the companion backend for frontend developers creating LLM-based apps**.

Built in Python, bundled with the necessary DevOps apparatus to run on-premise or in the cloud, it goes beyond simple Notebooks prototypes. The current version offers endpoints to create a "chat with PDF" app, namely:

1. create a collection of documents;
2. upload a PDF document to a collection;
3. monitor document processing after upload;
4. use an LLM to query documents from this collection (e.g. ChatGPT meets your PDFs).

In the near future, expect it to work with spreadsheets, images, Word documents, etc... More functionalities to come (see **Roadmap** section of this README).

The API is built with [Django](https://www.djangoproject.com/) and [DRF](https://www.django-rest-framework.org/) on top of a [Postgres](https://www.postgresql.org/) database, and a [Qdrant](https://qdrant.tech/) database for [vector embeddings](https://cloud.google.com/blog/topics/developers-practitioners/meet-ais-multitool-vector-embeddings) storage and retrieval. For LLM operations, it uses [LangChain](https://python.langchain.com/docs/get_started/introduction.html) and [OpenAI's API](https://openai.com/blog/openai-api) (for now, but it is being built towards LLM agnosticism).

In "production" mode (when run fully from [Docker Compose](https://docs.docker.com/compose/) stack), the app is served through an [Nginx reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/), and leverages a task management pipeline built with [Celery](https://docs.celeryq.dev/en/stable/) and [Redis](https://redis.io/) to offload document processing.

## Getting Started

### Prerequisites

#### Minimal

[Docker](https://docs.docker.com/engine/install/) is the minimal technical requirement to run Martini.

Because the current version (v0.1) runs on OpenAI's API only, you must to [register an OpenAI account](https://platform.openai.com/signup?launch) if you do not have one already, and [create an API key](https://platform.openai.com/account/api-keys) for use in Martini. More information can be found on [OpenAI's Help](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key).

**Once you have an OpenAI API key:**

1. **Create a copy of the `.env.example` file** at the root of the project, and name it `.env`:

```bash
# From the project's root folder
cp .env.example .env
```

2. **Paste the API key as value of the `OPENAI_API_KEY`** environment variable in you `.env` file.

3. Change the values for `APP_SUPERUSER_NAME`, `APP_SUPERUSER_PWD` and `APP_SUPERUSER_EMAIL` with a user name, a password and the user's email to be used for authentication in the [Django Admin Site](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/) of the stack.

#### Advanced

If you wish to benefit from all helper scripts, or edit/develop the application, you'll need **Python** and **Poetry**.

1. Fulfill the **Minimal** prerequisites listed above.
2. [Install Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer).
3. From the project's directory, generate a virtual environment with `poetry shell`.
4. Then install the dependencies with `poetry install`.

### Start Martini

Use Docker run the backend instance with minimal hurdle.

> Before you move on, please make sure you have completed the requirements in **Prerequisites > Minimal**.

Start Docker and run the following CLI command from the project's directory.

```bash
# Build images, create containers and run as daemon.
docker compose -f ./docker-compose.prod.yml up --build -d
```

#### Access the API

You can then access the API locally on <http://localhost:8080/>.

To make full usage of it, please refer to the **API Document** section below.


#### Use the monitoring tools

When your stack is running, you can use the built-in [Qdrant Web UI](https://github.com/qdrant/qdrant-web-ui) and [Flower](https://flower.readthedocs.io/en/latest/) tools to monitor the **Qdrant database** and **Celery task manager** respectively:

- Qdrant UI is available on <http://localhost:6333/>
- Flower is available on <http://localhost:5557/>

You can also use the built-in [Django Admin Site](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/), available at <http://localhost:8080/admin>.

The credentials to the Admin Site are the one in your `.env` file, you should have edited before building the Compose stack.

> If you are not familiar with Django, the **Admin Site** is a built-in administrative tool allowing you to create, edit, update and delete models and their relationships from a web UI. It automatically adapts to new models created in code. More information in Django's documentation: <https://docs.djangoproject.com/en/4.2/ref/contrib/admin/>

### API documentation

Once the server is running, an online documentation for the API can be accessed through:

- Swagger: <http://localhost:8080/swagger/>
- Redoc: <http://localhost:8080/redoc/>

If you are running the Development setup described in the next section, update the ports accordingly to use the Django development server (<http://localhost:8000> instead of <http://localhost:8080>).

A third, browsable documentation generated by DRF exists, but we advise not to rely on it as we may remove its access in the near future.

> The documentation is automatically generated, sourcing information from [functions docstrings](https://peps.python.org/pep-0257/) throughout the code.

## Development

### Key concepts

Before working with (or on) Martini, you should know the key concepts it relies on.

Martini uses LLMs to query (or "chat" with) an `UnstructedDocument`, or a `DocumentCollection` of `UnstructedDocuments`.

- An `UnstructedDocument` is any document, structured (e.g. JSON, CSV) or unstructured (e.g. PDF, image...) that Martini can process and work on (in the current version, PDF only).

- A `DocumentCollection` is a list of `UnstructedDocuments` that you choose to group together, creating a common library of knowledge the LLM can pull answers from.

- Each `UnstructedDocument` belongs to a single `DocumentCollection`.

- Martini creates a default `DocumentCollection` on startup. If you do not specify a `DocumentCollection` when creating a new `UnstructedDocument`, it will end up there.

### Work with Martini (frontend development)

After you have started an instance of Martini using Docker, you can use the API to leverage its functionality.

> Make sure you follow the requirements from the **Prerequisites > Minimal** section at the beginning of this README before moving on.

The typical process you will want achieve with your app will be as follows. We encourage you do a first rundown using a frontend client like cURL or Insomania (which is way easier to upload files).

1. **Run the containerized stack** from the root of the project's directory

```bash
docker compose -f ./docker-compose.prod.yml up --build -d
```

2. **Upload a file**: `POST /api/documents/`

```bash
curl --request POST \
  --url http://127.0.0.1:8000/api/documents/ \
  --header 'Content-Type: multipart/form-data' \
  --form 'name=my document name' \
  --form 'description=my optional description' \ # optional
  --form collection=1 \                          # optional: will fallback to default collection (id=1) if omitted
  --form 'file=@/path/to/my/file.pdf'
```

You will receive a response similar to:

```bash
{
  "id": 2,
  "name": "my document",
  "description": "my optional description",
  "file": "http://127.0.0.1:8000/static/uploads/1689099297_25989dd1-6895-4593-81cc-b05f6771f31a.pdf",
  "task_id": "dc7d299d-6834-43eb-bf43-4e6b2f0fba02",
  "collection": 1
}
```

The file is uploaded, but the processing will run asynchronously. You will need the `id` value from the response above to poll the processing status.

3. Query file processing status: `GET /api/documents/{id}/status`

```bash
curl --request GET \
  --url http://127.0.0.1:8000/api/documents/{id}/status  # replace with id
```

You will receive a response similar to the one below.

```bash
{
  "status": "PENDING", # PENDING if waiting to start, then STARTED, SUCCESS when finished, RETRY if retrying after a failure, FAILURE if failed after max retries
  "detail": "..."  # if any
}
```

You should _poll_, or request regularly, until the `status` field is `SUCCESS` or `FAILURE`.

4. Ask questions: `POST /api/messages`

You can now ask question regarding the `UnstructedDocument` (or all `UnstructedDocuments`, if you have uploaded several) in your `DocumentCollection`.

```bash
curl --request POST \
  --url http://127.0.0.1:8000/api/messages/ \
  --header 'Content-Type: application/json' \
  --data '{ "query": "When and where was Django developed?", "collection_id": 1 }'
  # you can also pass a `collection_name` instead of `collection_id`
```

The response will look like this:

```bash
{
  "query": "When and where was Django developed?",
  "answer": "Django was not mentioned in the context provided, so I don't know when and where it was developed."
}  # GPT will ONLY provide answers based on what's in the DocumentCollection!
```

### Work on Martini (backend development)

Whether you wish to contribute to the development of Martini, run a local instance of the app with the abiity to change backend stuff on-the-go with hot-reloading, or benefit from several helper scripts to improve DX, here's how you can leverage the Development setup.

> Before you move on, make sure you have followed all requirements from the **Prerequisites > Advanced** section, at the beginning of this README.

#### Development mode

In development mode, you are running a subset of the composer stack (Postgres and Qdrant) with the Django app development server. This allows you to work on the Django app with hot-reloading.

Note that in development, the Celery suite of tools for task management is disabled. Tasks (file processing) are run synchronously.

> This is mostly because of a _segfault_ bug on M1 machines when run Celery workers are run locally.
> Please see <https://github.com/celery/celery/issues/7007> and <https://github.com/celery/celery/issues/5867#issuecomment-564581217>

#### Get started with development

From the project's root directory, activate a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) and install dependencies using the following commands:

```bash
poetry shell
poetry install
```

Run the following to start the stack in development mode:

```bash
poetry run docker-up
```

It will also tail the logs from the stack. You can exit the logs using `Ctrl+D`.

Next, change into the **martini** directory, and run the following commands from another console:

```bash
# Change into the `martini` directory
cd martini

# Run these three commands
poetry run manage collectstatic
poetry run manage migrate
poetry run manage runserver
```

The first one will generate the static files used in Django's installed apps (in Django's Admin Site and the DRF Browsable API, notably).

The next will run database migrations, and the final one will start the development server.

> If you have used Django before, you will recognize calls to `collectstatic`, `migrate` and `runserver`, normally invoked from the `manage.py` file. The `poetry run manage` script is a proxy to Django's `manage.py`. To learn more, see [Django's documentation on `django-admin` and `manage.py`](https://docs.djangoproject.com/en/4.2/ref/django-admin/).

#### Helper scripts

Special **Poetry** script can help speed up your workflow.

The following must be run from the project's root directory. They are shortcuts for Docker-related commands.

```bash
# Stop, then turn off and removes all Docker containers, images and volumes for the application.
# Then rebuild and re-run the application.
poetry run docker-reset

# Shutdown containers.
poetry run docker-down

# Build and start containers in development mode.
poetry run docker-up

# Stop, then turn off and remove all Docker containers, images and volumes for the application.
poetry run docker-clean

# Builds and runs the application in production mode.
poetry run docker-prod

# Tail log from all containers.
poetry run docker-logs

# Tail logs from the Postgres container.
poetry run docker-postgres

# Tail logs from the Qdrant container
poetry run docker-qdrant

# Tail logs from the Django container (production mode only).
poetry run docker-web

# Tail logs from the Nginx container (production mode only).
poetry run docker-web-nginx

# Tail logs from the Celery worker container (production mode only).
poetry run docker-celery-worker

# Tail logs from the Flower container (production mode only).
poetry run docker-celery-flower

# Tail logs from the Celery scheduler container (production mode only).
poetry run docker-celery-beat

# Tail logs from the Redis container (production mode only).
poetry run docker-redis
```

The next scripts are to be run in the **martini** folder. They are related to the Django application itself.

```bash
# A proxy for manage.py. You can pass as arguments anything you would pass to django-admin / manage.py.
poetry run manage <arg>

# A wrapper around "django-admin startapp".
# @see https://docs.djangoproject.com/en/4.2/intro/tutorial01/#:~:text=%24%20python%20manage.py%20startapp%20polls
# What it does is ensure the new app is created within the "apps" folder for tidyness.
poetry run startapp
```

> By default, new apps in Django are created in their own folder within the project directory, which gets messy when you have several apps. The approach here is to create apps within a dedicated **apps** folder.
> Once an app is created this way, you must edit the app config in two places (**apps.py** in your app folder, and `INSTALLED_APPS` in the project settings). The `poetry run startapp` script will remind you of it after you create an app.

## Deployment

TBD

## Roadmap

Here is a list of features to be added. It is non-exhaustive and currently unordered.

- **Replace LangChain with lighweight library, or custom code implementing most functions and [ReAct flow](https://arxiv.org/abs/2210.03629)** (LangChain ultimately gets in the way with too much bloat and abstraction with little production value 🙁)
- More processable document types.
- More LLMs.
- Finer control and/or removal of monitoring tools (Qdrant UI, Celery Flower...) in production.
- Thorough functional testing: find exceptions and edge cases, handle them properly.
- Connectors: enable uploading or connecting to documents from various sources (Google Drive, Slack...).
- Deployment apparatus for VPCs (AWS, GCP, Azure, DigitalOcean, Linode...).
- Unit and integration tests.

## Alternative Projects

Martini is a barebone, "simple" project. Interesting open-source alternative exist, covering or overlapping similar functionalities and needs. Here's a non-exhaustive list:

- [Danwser](https://docs.danswer.dev/): Open-source Entreprise Q-A

## Contributing

Contributions are welcome. They should focus on the **Roadmap** and follow the branching and commit naming convention described hereafter.

### Branch naming convention

A git branch should start with a **category**, followed by an optional **reference** and a "kebab-cased" **description**

**Categories** are:

- `feat` when adding, refactoring or removing a feature, including tests
- `fix` when fixing a bug
- `chore` is everything else (documentation, formatting, remove useless code...)

**References** are either the name of a topic (e.g. feature branch) or a issue name, ticket number...

**Description** should be short, and like the branch name itself, kebab-cased (lower case, dash-separated words).

#### Examples

```bash
git branch feat/add-tabular-data-processing
git branch feat/new-llms/add-cohere-ai-llm
git branch fix/celery-worker-local
git branch chore/update-readme
```

### Commit naming convention

A commit message should start with a **category**, an optional **scope** between parens, followed by a colon, and a **statement**.

The **scope** is the area of the app ("`tasks`"), or even what specific components ("`unstructured-documents`") impacted by the change. You can omit it if it's redundant with your **statement**.

The **statement** should be short and contextualize the change.

#### Examples

```bash
git commit -m "feat: add new model"
git commit -m "fix(tasks): celery workers segfault on M1 MacBookPro"
git commit -m "chore(readme): update branch naming convention"
```

## Versioning

[SemVer](https://semver.org/) is used for versioning, using [git tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging).

## License

Distributed under MIT license.
