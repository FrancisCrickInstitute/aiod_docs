# Developing AIoD

This page serves as a guide for setting up your development environment for contributing to code across the AIoD project. If you just want to add models to AIoD, see our [contributing page](./expanding.md).

It is intended for core developers and goes beyond what the majority of users need to know. We assume that _what_ you're developing has been discussed in a specific issue in the relevant repository. See our page on [raising an issue](../support/index.md#raising-an-issue) for this first step!


## Framework Repo Overview

AIoD comprises several separate interdependent codebases, which are developed in separate repositories as shown on the [home page](../../index.md#repositories).

Depending on what you are developing, you may only need to setup one or two of these repositories.

### Interdependencies

`aiod_utils` is a dependency for both `aiod_napari` and `Segment-Flow` (for the latter, via the conda environments built for the Nextflow pipeline steps).

`aiod_registry` is also a dependency for both `aiod_napari` and `Segment-Flow` (for a subset of the conda environments).


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

By default the plugin will run the pipeline from the [published GitHub repository](https://github.com/FrancisCrickInstitute/Segment-Flow).

To use your local Segment-Flow clone instead (e.g. to test local changes), set the `AIOD_NXF_REPO` environment variable to its path.

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
- aiod_utils==0.1
# With this:
- -e /path/to/your/aiod_utils
```

!!! tip
    Nextflow hashes the YAML file contents to determine the cache directory name, so changing the YAML automatically triggers a fresh environment build — no need to manually clear the cache.

!!! warning
    Remember to revert these YAML changes before committing — they should never be merged into the repository!

!!! under-construction
    We have a Bash script + skill that allows agents to robustly swap published and development versions of packages into the Nextflow envs, avoiding needed to rebuild. We will publish this soon! 