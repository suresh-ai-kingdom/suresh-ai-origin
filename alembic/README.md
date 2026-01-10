This Alembic environment is configured to use `models.Base.metadata` for autogeneration.

To stamp/create initial migration locally:

- pip install alembic
- alembic revision --autogenerate -m "initial"
- alembic upgrade head

For CI, prefer running `alembic upgrade head` before starting the app if migrations are used in production.