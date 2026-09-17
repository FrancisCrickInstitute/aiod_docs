"""Render the AIoD model registry into the docs at build time.

`aiod_registry` is the single source of truth for which models exist, so the model
reference page and the home page card grid are both derived from the installed
package rather than maintained by hand. Adding a model family to the registry and
rebuilding is enough to make it appear in both places.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml
from aiod_registry import TASK_NAMES, load_manifests
from aiod_registry import __version__ as registry_version

log = logging.getLogger("mkdocs.plugins.aiod")

CARD_DATA = Path(__file__).parent / "docs" / "data" / "model_cards.yml"

# Where the generated reference page lands, relative to the site root. Raw HTML in
# Markdown is passed through untouched by MkDocs (unlike Markdown links, which get
# rewritten), so the card hrefs have to be written relative to the page they sit on
# — the home page, at the site root.
MODELS_PAGE = "sections/model_registry/models/"


def _manifests():
    """Every manifest, sorted by display name.

    Deliberately not `filter_access=True`: that drops any family whose locations
    are all unreachable from the machine doing the build, which for a docs build is
    every filepath-only model. The docs need to list those and say they are
    restricted, not pretend they do not exist.
    """
    return dict(sorted(load_manifests().items(), key=lambda kv: kv[1].name.lower()))


def _anchor(short_name: str) -> str:
    return f"model-{short_name}"


def _is_url(location) -> bool:
    return urlparse(str(location)).scheme in ("http", "https")


def _availability(version) -> str:
    """How obtainable a version is, aggregated over its tasks.

    A task is obtainable by anyone if at least one of its locations is a URL; if
    every location is a filepath, only people who can read that path will see it.
    """
    per_task = [
        any(_is_url(entry.location) for entry in task.locations)
        for task in version.tasks.values()
    ]
    if all(per_task):
        return "Public"
    if not any(per_task):
        return "Restricted"
    return "Mixed"


def _cell(text) -> str:
    """Make a value safe to drop into a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def _task_label(task: str) -> str:
    return TASK_NAMES.get(task, task)


def _param_default(param) -> str:
    value = param.value
    if isinstance(value, list):
        effective = (
            param.default
            if param.default is not None
            else (value[0] if value else None)
        )
        options = ", ".join(f"`{opt}`" for opt in value)
        return f"`{effective}` (of {options})"
    if value is None:
        # A null in the manifest is a real default the model acts on (usually
        # "work it out yourself"), not a missing entry, so name it rather than
        # describing it. The declared dtype says what to replace it with.
        return f"`None` ({param.dtype})" if param.dtype else "`None`"
    return f"`{value}`"


def _param_table(params) -> list[str]:
    lines = [
        "| Parameter | Argument | Default | Description |",
        "| --- | --- | --- | --- |",
    ]
    for param in params:
        lines.append(
            f"| {_cell(param.name)} "
            f"| `{_cell(param.arg_name or param.name)}` "
            f"| {_cell(_param_default(param))} "
            f"| {_cell(param.tooltip or '')} |"
        )
    return lines


def _links(metadata) -> str:
    parts = []
    if metadata.url:
        parts.append(f"[Documentation]({metadata.url})")
    if metadata.repo:
        parts.append(f"[Repository]({metadata.repo})")
    for pub in metadata.pubs or []:
        label = f"{pub.title}" + (f" ({pub.year})" if pub.year else "")
        parts.append(
            f"[{label}]({pub.doi and f'https://doi.org/{pub.doi}' or pub.url})"
        )
    return " · ".join(parts)


def define_env(env):
    @env.macro
    def model_grid() -> str:
        """The home page card grid, one card per entry in model_cards.yml."""
        manifests = _manifests()
        cards = yaml.safe_load(CARD_DATA.read_text(encoding="utf-8"))["cards"]

        covered = {fam for card in cards for fam in card["families"]}
        for short_name in manifests:
            if short_name not in covered:
                log.warning(
                    "Model family '%s' has no entry in docs/data/model_cards.yml — "
                    "it will show as a card without a logo. Add one to control its "
                    "grouping and image.",
                    short_name,
                )
                cards.append(
                    {"title": manifests[short_name].name, "families": [short_name]}
                )

        html = ['<div class="model-grid">']
        for card in cards:
            families = [f for f in card["families"] if f in manifests]
            if not families:
                log.warning(
                    "Card '%s' lists no families present in the registry — skipping.",
                    card.get("title"),
                )
                continue
            href = card.get("href") or f"{MODELS_PAGE}#{_anchor(families[0])}"
            html.append(f'  <a href="{href}" class="model-card">')
            if card.get("logo"):
                # Card titles may carry markup (a <br> to balance a long name); the
                # alt text must not.
                alt = re.sub(r"<[^>]+>", " ", card["title"])
                alt = " ".join(alt.split())
                html.append(f'    <img src="assets/{card["logo"]}" alt="{alt} logo">')
            html.append(f"    <span>{card['title']}</span>")
            html.append("  </a>")
        html.append("</div>")
        return "\n".join(html)

    @env.macro
    def task_table() -> str:
        """Every task the registry defines, and which families can perform it."""
        manifests = _manifests()
        families_by_task: dict[str, list[str]] = {task: [] for task in TASK_NAMES}
        for manifest in manifests.values():
            for version in manifest.versions.values():
                for task in version.tasks:
                    entry = f"[{manifest.name}](#{_anchor(manifest.short_name)})"
                    if entry not in families_by_task.setdefault(task, []):
                        families_by_task[task].append(entry)

        lines = [
            "| Task | `--task` | Models |",
            "| --- | --- | --- |",
        ]
        for task, label in TASK_NAMES.items():
            models = ", ".join(families_by_task.get(task, [])) or "_none yet_"
            lines.append(f"| {label} | `{task}` | {models} |")
        return "\n".join(lines)

    @env.macro
    def model_reference() -> str:
        """One section per model family: versions, tasks, availability, parameters."""
        out: list[str] = []
        for manifest in _manifests().values():
            out.append(f"### {manifest.name} {{ #{_anchor(manifest.short_name)} }}")
            out.append("")
            out.append(f"Run with `--model {manifest.short_name}`.")
            out.append("")
            if manifest.metadata.description:
                out.append(manifest.metadata.description)
                out.append("")
            links = _links(manifest.metadata)
            if links:
                out.append(links)
                out.append("")

            out.append("| Version | `--model_type` | Tasks | Axes | Availability |")
            out.append("| --- | --- | --- | --- | --- |")
            for name, version in manifest.versions.items():
                tasks = ", ".join(_task_label(t) for t in version.tasks)
                axes = f"`{version.axes}`" if version.axes else "—"
                out.append(
                    f"| {_cell(name)} | `{_cell(version.slug)}` | {_cell(tasks)} "
                    f"| {axes} | {_availability(version)} |"
                )
            out.append("")

            if any(_availability(v) != "Public" for v in manifest.versions.values()):
                out.append(
                    '!!! note "Restricted versions"\n\n'
                    "    Some versions above are shared by file path rather than public "
                    "download, so they are only visible to people who can read that "
                    "location — see [Model Location](../concepts/index.md#model-location)."
                )
                out.append("")

            if manifest.usage_guide:
                out.append(f'!!! tip "Usage guidance"\n\n    {manifest.usage_guide}')
                out.append("")

            if manifest.params:
                out.append('??? note "Parameters"')
                out.append("")
                for line in _param_table(manifest.params):
                    out.append(f"    {line}")
                out.append("")

            # Only surface per-task parameters where they genuinely differ; most
            # tasks inherit the family-level set verbatim.
            for version_name, version in manifest.versions.items():
                for task_name, task in version.tasks.items():
                    if task._params_inherited or not task.params:
                        continue
                    out.append(
                        f'??? note "Parameters — {version_name} / {_task_label(task_name)}"'
                    )
                    out.append("")
                    for line in _param_table(task.params):
                        out.append(f"    {line}")
                    out.append("")

        out.append("")
        out.append(f"*Generated from `aiod_registry` {registry_version}.*")
        return "\n".join(out)
