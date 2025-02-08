default:
    just test


test: sync-env
   uv run pytest tests/


run path: sync-env
    uv run mechabellum-replay-parser "{{path}}"


sync-env:
    uv sync

