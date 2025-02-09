default:
    just test


test: sync-env
   uv run pytest tests/


run path: sync-env
    uv run mechabellum-replay-parser "{{path}}"


build: clean sync-env
    uv build
    for file in dist/*.whl; do cp "$file" dist/dist.whl; break; done

clean:
    rm -rf dist


sync-env:
    uv sync

