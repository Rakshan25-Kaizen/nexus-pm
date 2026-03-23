seed:
	python -m backend.memory.setup_banks
	python -m data.seed
	python -m scripts.setup_hindsight

reset-db:
	python -m alembic upgrade head

setup: reset-db seed
