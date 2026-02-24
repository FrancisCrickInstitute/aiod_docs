
# Developer setup guide

This page serves as a guide for setting up your development environment for contributing to code across the AIoD project.
It is intended for core developers and goes beyond what the majority of users need to know.

## Codebase overview

### Subprojects

AI on Demand comprises several separate interdependent codebases, which are developed in separate repositories.

1. [ai-on-demand](https://github.com/FrancisCrickInstitute/ai-on-demand), the Napari plugin and main user interface
2. [Segment-Flow](https://github.com/FrancisCrickInstitute/Segment-Flow), the Nextflow pipeline
3. [aiod_utils](https://github.com/FrancisCrickInstitute/aiod_utils), which contains shared utility code
4. [aiod_registry](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry), the [model registry](../model_registry/index.md).
5. [aiod_docs](https://github.com/FrancisCrickInstitute/aiod_docs), which contains the documentation (this site!)

Depending on your level of involvement, you may only need to setup one or two of these repositories.

### Interdependencies

`aiod_utils` is a dependency for both `ai-on-demand` and `Segment-Flow` (for the latter, via the conda environments built for the Nextflow pipeline steps).

## Project set up

### Prerequisites

- [Git](https://git-scm.com/downloads)
- [Conda](https://www.anaconda.com/docs/getting-started/miniconda/install) (strongly recommended — see warning below)
- [Nextflow](https://www.nextflow.io/docs/latest/install.html)
- SSH access to the [FrancisCrickInstitute](https://github.com/FrancisCrickInstitute) GitHub organisation with SSO enabled — contact a maintainer to be added if needed

### Environment

Create an isolated Python environment using an environment manager of your choice

!!! warning
    Due to Segment-Flow's use of conda environments for running pipeline steps, past experience has shown it exceedingly difficult to use an environment manager other than conda (such as the Python `venv` module) for this project.

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

Next install `ai-on-demand` in editable mode.
The `--recurse-submodules` flag is required to also clone Segment-Flow, which is included as a git submodule:

```bash
(c-aiod) $ git clone --recurse-submodules git@github.com:FrancisCrickInstitute/ai-on-demand.git
(c-aiod) $ cd ai-on-demand
(c-aiod) $ pip install -e .
```

Note that `pip install -e .` will not reinstall `aiod_utils` since it is already installed, regardless of the git URL specified in `pyproject.toml`.

By default the plugin will run the pipeline from the [published GitHub repository](https://github.com/FrancisCrickInstitute/Segment-Flow). 
To use your local Segment-Flow submodule instead (e.g. to test local changes), set the `AIOD_NXF_REPO` environment variable to its path.
Run the following from the `ai-on-demand` directory:

```bash
(c-aiod) $ export AIOD_NXF_REPO=$(realpath src/ai_on_demand/Segment-Flow)
```

To revert to using the published pipeline, unset the variable:

```bash
(c-aiod) $ unset AIOD_NXF_REPO
```

From your base directory, the project structure should look like this:

```txt
.
├── ai-on-demand/
│   └── src/ai_on_demand/Segment-Flow/  ← submodule
└── aiod_utils/
```

Install other AIoD project components as required in the same manner.
