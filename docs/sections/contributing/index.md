
# Contributing to AIoD


## Model Registry

### Add a New Model Family
!!! info ""

    A **model family** is a group of models that can be run in the same environment, i.e. with the same packages/libraries.

    Examples: Cellpose (v1+2+3), SAM (and all derivatives, micro-SAM, MedSAM etc.)

To add a new model family to the registry, you will need to create a new manifest file for that model. Note that the name of this model 

It is recommended to look at the [existing manifests](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/tree/main/aiod_registry/manifests) as well as our [Pydantic schema](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/schema.py) in order to understand what is required. It is quite lightweight, however, 

You will then need to add the relevant script & environment to the Nextflow pipeline (see the [section below](#add-a-new-model-family-1)).

### Add a New Model Version
!!! info ""

    A **model version** is a single model for which there is already a [model family](#add-a-new-model-family).

    Examples: [Cellpose's `cyto3`](https://cellpose.readthedocs.io/en/v3.1.1.1/models.html#cytoplasm-model-cyto3-cyto2-cyto), [SAM2's `hiera_large`](https://github.com/facebookresearch/sam2?tab=readme-ov-file#download-checkpoints)

### Add a New Task

!!! info ""

    A **task** is the objective of the model, i.e. what it is trying to do (segment). For example, the task of MitoNet is `"mito"` (for mitochondria).

If you add a model with a task that does not exist in our current list defined in the [schema](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/schema.py) (`TASK_NAME` dict), then you can [make a pull request](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/pulls) with the new key:value (short name: long name) pair alongside the new/updated model schema you are adding.

## Nextflow Pipeline

### Add an Institution Profile

### Add a New Model Family
