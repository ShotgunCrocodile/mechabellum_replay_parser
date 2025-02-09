default:
    just test


test: sync-env
   uv run pytest tests/


run path: sync-env
    uv run mechabellum-replay-parser "{{path}}"


build: clean sync-env
    uv build
    for file in dist/*.tar.gz; do cp "$file" dist/dist.tar.gz; break; done

clean:
    rm -rf dist


sync-env:
    uv sync

