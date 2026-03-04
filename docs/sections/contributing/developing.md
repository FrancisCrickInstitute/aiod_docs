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

Create an isolated conda environment:

```bash
# Conda (recommended)
$ conda create --name c-aiod python=3.12
$ conda activate c-aiod
```

### Installation

Pick a top level directory to install the AIoD subprojects into, which can be your home or general development directory or a dedicated AIoD folder.

Install `aiod_utils` first, as it is a dependency for the other components.

```bash
(c-aiod) $ git clone git@github.com:FrancisCrickInstitute/aiod_utils.git
(c-aiod) $ cd aiod_utils
(c-aiod) $ pip install -e .
(c-aiod) $ cd ..
```

Next install `aiod_napari` in editable mode.
The `--recurse-submodules` flag is required to also clone Segment-Flow, which is included as a git submodule:

```bash
(c-aiod) $ git clone --recurse-submodules git@github.com:FrancisCrickInstitute/ai-on-demand.git
(c-aiod) $ cd ai-on-demand
(c-aiod) $ pip install -e .
```

Note that `pip install -e .` will not reinstall `aiod_utils` since it is already installed, regardless of the git URL specified in `pyproject.toml`.

From your base directory, the project structure should look like this:

```txt
.
├── ai-on-demand/
│   └── src/ai_on_demand/Segment-Flow/  ← submodule
└── aiod_utils/
```

Install other AIoD project components as required in the same manner.


## Testing local changes

### `Segment-Flow` (Nextflow pipeline)

By default the plugin will run the pipeline from the [published GitHub repository](https://github.com/FrancisCrickInstitute/Segment-Flow).

To use your local Segment-Flow submodule instead (e.g. to test local changes), set the `AIOD_NXF_REPO` environment variable to its path.

Run the following from the `aiod_napari` directory:

```bash
(c-aiod) $ export AIOD_NXF_REPO=$(realpath src/ai_on_demand/Segment-Flow)
```

To revert to using the published pipeline, unset the variable:

```bash
(c-aiod) $ unset AIOD_NXF_REPO
```

Note that `AIOD_NXF_REPO` does not persist — it applies only to the current shell session, so the published pipeline is always used by default.

### `aiod_utils` in pipeline steps

The Nextflow pipeline steps each run in their own conda environment, defined by the YAML files in `Segment-Flow/modules/models/envs/`. These install `aiod_utils` directly from GitHub, so local edits to `aiod_utils` are not automatically picked up.

There is no clean automated mechanism for this. The pragmatic approach is to temporarily edit the relevant YAML file(s) to replace the git URL with a local editable install, run the pipeline, then revert before committing:

```yaml
# Replace this:
- git+https://github.com/FrancisCrickInstitute/aiod_utils.git
# With this:
- -e /path/to/your/aiod_utils
```

!!! tip
    Nextflow hashes the YAML file contents to determine the cache directory name, so changing the YAML automatically triggers a fresh environment build — no need to manually clear the cache.

!!! warning
    Remember to revert these YAML changes before committing — they should never be merged into the repository!