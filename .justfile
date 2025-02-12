default:
    just test


test: sync-env
   uv run pytest tests/


run +args: sync-env
    uv run mechabellum-replay-parser {{args}}


build: clean sync-env
    uv build
    for file in dist/*.tar.gz; do cp "$file" dist/dist.tar.gz; break; done

clean:
    rm -rf dist


sync-env:
    uv sync


bump-version type:
    uv run bumpver update {{type}}
    uv sync
    git add uv.lock pyproject.toml
    git commit -m "Bump version to `uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version`"