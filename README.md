# AIoD Documentation

[![Build](https://github.com/FrancisCrickInstitute/aiod_docs/actions/workflows/ci.yml/badge.svg)](https://github.com/FrancisCrickInstitute/aiod_docs/actions/workflows/ci.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-live%20site-1f6feb.svg)](https://franciscrickinstitute.github.io/aiod_docs/)

Source for the [AI OnDemand (AIoD)](https://franciscrickinstitute.github.io/aiod_docs/) umbrella docs for the whole framework.

> **📖 Read the docs at [franciscrickinstitute.github.io/aiod_docs](https://franciscrickinstitute.github.io/aiod_docs/)**

This repo builds the site with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Requirements

We require Python (for `aiod-registry`) to generate the model reference and [uv](https://docs.astral.sh/uv/).

## Building locally

```bash
uv sync --group docs
uv run mkdocs serve   # live-reloading preview on http://127.0.0.1:8000
uv run mkdocs build   # one-off build into site/
```

## Repository layout

| Path | What it is |
| --- | --- |
| `mkdocs.yml` | Site config: nav, theme, plugins, `site_url` |
| `docs/` | All page content; the nav in `mkdocs.yml` is the source of truth for ordering |
| `docs/data/model_cards.yml` | Logos and grouping for the home page model cards |
| `docs/assets/` | Images, GIFs and video clips |
| `main.py` | mkdocs-macros hooks that generate the model reference (see below) |

## Generated content

The **Available Models** reference and the home page model cards are automatically generated. [`main.py`](main.py) defines three [mkdocs-macros](https://mkdocs-macros-plugin.readthedocs.io/) (`model_grid()`, `task_table()`, and `model_reference()`) which import the installed [`aiod_registry`](https://github.com/FrancisCrickInstitute/aiod_registry) at build time and render every family, version, task and parameter from its manifests.

- To update the model list, change the manifest in `aiod_registry` and release it...do not touch the markdown here! The site only picks up new or changed models when the pinned `aiod-registry` in `uv.lock` moves, which [`registry-bump.yml`](.github/workflows/registry-bump.yml) does via a `repository_dispatch` from that repo's release (or `workflow_dispatch`, until `aiod_docs` is added to its `notify-downstream` matrix).
- The macros plugin runs with `on_undefined: strict`, so a manifest the generator can't handle fails the build. This is why PRs run `mkdocs build` in CI.

## Deployment

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) builds the site on every pull request, and runs `mkdocs gh-deploy --force` on every push to `main`, publishing to GitHub Pages.

## Contributing

Corrections and additions are very welcome (please open a PR). Pages are plain markdown under `docs/`; if you add one, add it to the `nav` in `mkdocs.yml` too. For contributing to AIoD more broadly, see the [Developer Guide](https://franciscrickinstitute.github.io/aiod_docs/sections/contributing/developing/).

## Support

Please [open an issue](https://github.com/FrancisCrickInstitute/aiod_docs/issues) for anything unclear, missing or wrong in the docs. Issues with AIoD itself are best raised on the [relevant repository](https://franciscrickinstitute.github.io/aiod_docs/#repositories).

## License

[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](LICENSE)

This repository is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse and adapt it freely, with credit. The other AIoD repositories are MIT; documentation is prose rather than software, so it carries a licence built for that.

The Crick trademarks and the third-party model logos under `docs/assets/` are **excluded** — see [NOTICE.md](NOTICE.md).
