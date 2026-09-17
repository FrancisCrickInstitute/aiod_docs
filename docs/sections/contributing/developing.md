# Developing AIoD

This page serves as a guide for setting up your development environment for contributing to code across the AIoD project. If you just want to add models to AIoD, see our [contributing page](./expanding.md).

It is intended for core developers and goes beyond what the majority of users need to know. We assume that _what_ you're developing has been discussed in a specific issue in the relevant repository. See our page on [raising an issue](../support/index.md#raising-an-issue) for this first step!


## Framework Repo Overview

AIoD comprises several separate interdependent codebases, which are developed in separate repositories as shown on the [home page](../../index.md#repositories).

Depending on what you are developing, you may only need to setup one or two of these repositories.

### Interdependencies

`aiod_utils` is a dependency for both `aiod_napari` and `Segment-Flow` (for the latter, via the conda environments built for the Nextflow pipeline steps).

`aiod_registry` is also a dependency for both `aiod_napari` and `Segment-Flow` (for a subset of the conda environments).

To date, AIoD packages at the same minor level (e.g. everything on `0.2.x`) are expected to work together. This may change, but each version will have the correct dependencies of the other AIoD packages as needed.


## Project Setup

### Prerequisites

- [Git](https://git-scm.com/downloads)
- [Conda](https://www.anaconda.com/docs/getting-started/miniconda/install) (strongly recommended — see warning below)
- [Nextflow](https://www.nextflow.io/docs/latest/install.html)

### Environment
!!! warning

    Due to Segment-Flow's use of conda environments for running pipeline steps, past experience has shown it exceedingly difficult to use an environment manager other than conda (such as the Python `venv` module) for this project.

Create an isolated conda environment. All AIoD packages require Python `>=3.11,<3.13`:

```bash
# Conda (recommended)
$ conda create --name c-aiod python=3.12
$ conda activate c-aiod
```

### Installation

Pick a top level directory to install the AIoD subprojects into, which can be your home or general development directory or a dedicated AIoD folder.

Which ones you need to install depend on what you are developing. The Python packages (`aiod_utils`, `aiod_napari`, and `aiod_registry`) will all follow the typical pattern:

```bash
(c-aiod) $ git clone git@github.com:FrancisCrickInstitute/aiod_utils.git
(c-aiod) $ cd aiod_utils
(c-aiod) $ uv pip install -e .
(c-aiod) $ cd ..
```

Segment-Flow needs cloning alongside the others if you want to test local pipeline changes (see [below](#segment-flow-nextflow-pipeline)):

```bash
(c-aiod) $ git clone git@github.com:FrancisCrickInstitute/Segment-Flow.git
```

If all have been cloned, your base directory structure should look like this:

```txt
.
├── aiod_napari/
├── aiod_registry/
├── aiod_utils/
└── Segment-Flow/
```

!!! tip "`uv sync` picks up your sibling clones"

    For plugin development you do not need to install `aiod_utils` and `aiod_registry` separately. `aiod_napari` declares them as editable [`uv` sources](https://docs.astral.sh/uv/concepts/projects/dependencies/) pointing at `../aiod_utils` and `../aiod_registry`, so with the layout above, running the following from the `aiod_napari` directory:

    ```bash
    (c-aiod) $ uv sync
    ```

    installs the plugin *and* both sibling packages in editable mode — changes to any of the three are picked up immediately, with no reinstall.

    This relies on the directory names matching exactly as above. To ignore your local clones and resolve the pinned released versions from PyPI instead:

    ```bash
    (c-aiod) $ uv sync --no-sources
    ```


## Testing local changes

### `Segment-Flow` (Nextflow pipeline)

By default the plugin will run the pipeline from the [published GitHub repository](https://github.com/FrancisCrickInstitute/Segment-Flow), at a revision pinned in the plugin. That pin is what ties a plugin release to a pipeline it was actually tested against; `AIOD_NXF_REV` overrides it if you need a different tag, commit, or branch.

To use your local Segment-Flow clone instead (e.g. to test local changes), set the `AIOD_NXF_REPO` environment variable to its path. This takes precedence over `AIOD_NXF_REV`, which is ignored as a checkout is already at whatever revision you have checked out!

Run the following from your base directory:

```bash
(c-aiod) $ export AIOD_NXF_REPO=$(realpath Segment-Flow)
```

!!! note "Profiles follow `AIOD_NXF_REPO`"

    The plugin normally lists the [execution profiles](./expanding.md#add-a-profile) bundled with it. When `AIOD_NXF_REPO` is set, profiles are instead read from `$AIOD_NXF_REPO/profiles`, so your local checkout also controls which profiles appear in the dropdown.

To revert to using the published pipeline, unset the variable:

```bash
(c-aiod) $ unset AIOD_NXF_REPO
```

Note that `AIOD_NXF_REPO` does not persist — it applies only to the current shell session, so the published pipeline is always used by default.

### `aiod_utils` in pipeline steps

The Nextflow pipeline steps each run in their own conda environment, defined by the YAML files in `Segment-Flow/modules/models/envs/`. These install `aiod_utils` as a pinned release from PyPI, so local edits are not automatically picked up — and neither is any fix, until a new version is released and the pins are bumped.

There is no clean automated mechanism for this. The pragmatic approach is to temporarily edit the relevant YAML file(s) to replace the pinned version with a local editable install, run the pipeline, then revert before committing:

```yaml
# Replace this:
- aiod_utils==0.2.0
# With this:
- -e /path/to/your/aiod_utils
```

!!! tip
    Nextflow hashes the YAML file contents to determine the cache directory name, so changing the YAML automatically triggers a fresh environment build — no need to manually clear the cache.

!!! warning
    Remember to revert these YAML changes before committing — they should never be merged into the repository!

#### Swapping Without a Rebuild

Editing the YAML rebuilds the whole environment, which is safe but slow if you are iterating. `Segment-Flow` also ships [`scripts/dev_swap_conda_pkg.sh`](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/master/scripts/dev_swap_conda_pkg.sh), which instead swaps a local checkout into an *existing* cached environment and guarantees it is put back:

```bash
# Find which cached envs currently have the package installed
$ ./scripts/dev_swap_conda_pkg.sh list aiod_utils

# Swap in, run, and always restore - even if the run fails or you Ctrl-C
$ ./scripts/dev_swap_conda_pkg.sh run \
    --env ~/.nextflow/aiod/conda/env-<hash> \
    --package aiod_utils \
    --local-path /path/to/your/aiod_utils \
    -- nextflow run . -profile local --img_dir /path/to/images
```

Prefer `run` over the separate `swap` and `restore` commands: it restores on every exit path, whereas with `swap` you are responsible for remembering the other half.

!!! danger "Never edit a cached environment by hand"

    Do not `pip install -e` into `~/.nextflow/aiod/conda/env-*` yourself. Those directories are named by a hash of the YAML that describes them, so a hand-edited one silently breaks that promise — every later run reusing that cache gets code the YAML does not describe, and nothing surfaces it until something inexplicable breaks much later. The script exists to make the swap and the restore a single guaranteed unit.

If you suspect an environment has already drifted — from a swap done before this script existed, or one done by hand — `audit` compares what is actually installed against what the YAML declares, and `fix-drift` repairs it:

```bash
$ ./scripts/dev_swap_conda_pkg.sh audit aiod_utils
$ ./scripts/dev_swap_conda_pkg.sh fix-drift aiod_utils --yes
```

`fix-drift` is a dry run unless you pass `--yes`. Both take a single package by design rather than sweeping every pinned dependency: packages such as `torch` are legitimately pinned differently between the `cuda` and `generic` environment variants, so a repo-wide check would be mostly noise. They are most useful for our own packages, which are pinned identically everywhere.

!!! note "Agents get this rule automatically"

    The same guidance is checked in as a skill at `.claude/skills/dev-swap-conda-pkg/`, so an agent working in `Segment-Flow` picks it up without being told.

## Pre-building Model Environments

Each model family runs in its own conda environment, which Nextflow builds on first use. That means the first person to run a given model waits for a full environment build, and a failure partway through (no network, no disk space) surfaces as a confusing mid-run error.

`Segment-Flow` can build them all up front instead:

```bash
$ ./prebuild_all.sh crick
```

The argument is the [execution profile](./expanding.md#add-a-profile), which decides both where the environments are written (`conda.cacheDir`) and whether the `cuda` or `generic` environment variants are used, so build with the same profile your users will run with. It discovers the available models the same way the pipeline does, by scanning for `run_*.py`, so a newly added model family is picked up with no change to the script.

To build just one:

```bash
$ nextflow run prebuild.nf -profile crick --model cellpose
```

!!! tip "Worth doing at deployment time"

    If you are setting AIoD up for an institution, run this once against a shared `conda.cacheDir` before anyone else uses it. Every subsequent user gets a cache hit rather than a build, which both saves the wait and removes the most common first-run failure.

## Testing

Each Python package is tested with `pytest`, run from that repository:

```bash
(c-aiod) $ pytest -v tests/
```

For `aiod_registry` this is also what validates manifests. Pydantic reports exactly which field is wrong, so run it before opening a PR rather than waiting for CI.

!!! warning "Generated files are checked, not just generated"

    `aiod_registry` commits both its default model configs and its JSON Schema. CI regenerates them on every pull request and **fails if what you committed is stale**; on merge to `main` it regenerates and commits any difference.

    So if you change a manifest's parameters or the schema itself, run the relevant command and commit the result:

    ```bash
    (c-aiod) $ aiod-gen-configs   # after changing model parameters
    (c-aiod) $ aiod-gen-schema    # after changing schema.py
    ```