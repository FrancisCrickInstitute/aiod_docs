# Expanding AIoD

This page covers how to add models to AIoD. If you want to contribute to the codebase, then see our [developer guide](./developing.md) for advice!

## Model Registry
The model registry contains the [manifests/schemas](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/tree/main/aiod_registry/manifests) that provide the basic information about a model, and is the starting point when adding new models to AIoD.

The process of adding a model depends whether it represents a new model family, or new version to an existing model, as the following sections will explain.

### Add a New Model Family

!!! warning "Experience Needed!"

    Adding a new model family requires familiarity with how best to run the model being added, and some Python familiarity to ensure it is integrated into the framework properly.

    The information here should be all you need to add the model, however!

To add a new [model family](../concepts/index.md#model-family) to the registry, you will need to create a new manifest file for that model. Note that the name of this model should reflect the group of models, and should therefore refer to the library/framework accordingly.

It is recommended to look at the [existing manifests](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/tree/main/aiod_registry/manifests) and our [Pydantic schema](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/schema.py) in order to understand what is required. It is quite lightweight, however, and should be a quick, simple process. If you encounter any issues, see our [contact us](../support/index.md#contact-us) section.

Each new schema needs:

- A model name (the `short_name` is used as the name for the Python script and conda environments in the Nextflow pipeline — details [below](#add-a-new-model-family_1))
- At least one model version — details [below](#add-a-new-model-version)
- Relevant metadata (as much information as possible to provide background information and external links to help further guidance users on model usage and for references to include in publications)

**You will then need to add the relevant script & environment to the Nextflow pipeline (see the [section below](#add-a-new-model-family-1)).**

### Add a New Model Version
To add a new [model version](../concepts/index.md#model-version), you simply need to add a new entry within the existing manifest. Looking at a simple case like the [`empanada` model versions](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/a1f49db85674b6e5405f1d29145c71dc1f0adbd3/aiod_registry/manifests/empanada.json#L23) should help indicate how to do it!

A model version must contain:

- A name
- A task the model is used for
- A location (filepath or URL — see [here](../concepts/index.md#model-location) for the implications of each)
- (Optional) a filepath/URL to a config file, which depending on how the model is interacted with might be necessary ([example](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/a1f49db85674b6e5405f1d29145c71dc1f0adbd3/aiod_registry/manifests/seai_unet.json#L42))

If this model version represents a new task that does not exist, see the [add a new task](#add-a-new-task) section below.

If the model has different parameter inputs or additional metadata beyond the global, model family-level settings, these can be added for specific versions as indicated in the [Pydantic schema](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/a1f49db85674b6e5405f1d29145c71dc1f0adbd3/aiod_registry/schema.py#L165-L173).

#### Add a New Model Location
As discussed in our [Concepts section](../concepts/index.md#model-location) you may wish to keep a model private prior to publication, but have it used by multiple individuals in different locations. In this case, simply append a new file location to the schema ([example](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/a1f49db85674b6e5405f1d29145c71dc1f0adbd3/aiod_registry/manifests/seai_unet.json#L41)), and then the model will be available to users that have read-access to that location.

### Add a New Task
If you add a model with a task that does not exist in our current list defined in the [schema](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/schema.py) (`TASK_NAME` dict), then you can [make a pull request](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/pulls) with the new key:value (short name: long name) pair alongside the new/updated model schema you are adding.


## Nextflow Pipeline
Our [Nextflow `Segment-Flow` pipeline](../nextflow/index.md) is where the actual main computation happens, and determines how each model is run. When adding a new model family to AIoD or setting up AIoD for a new institution, you will need to add specific files as explained below.

### Add a Profile
For new institutions/compute environments, configuring the [profile](https://www.nextflow.io/docs/latest/config.html#config-profiles) is needed to ensure things are set up properly!

=== "HPC"

    For a new institution running AIoD, you will need to add an execution profile to the [`Segment-Flow` repo profiles folder](https://github.com/FrancisCrickInstitute/Segment-Flow/tree/master/profiles). By doing so, it will both be available to all when running the pipeline directly, and automatically populate as an option in the Napari plugin.

    We recommend using the current [Crick profile](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/master/profiles/crick.conf) as a starting point, modifying a few parameters most likely to differ for your institute:

    - The `executor` (i.e. we use `'slurm'`) — full list of options [here](https://www.nextflow.io/docs/latest/executor.html)
    - The `queue` names for the relevant GPU/CPU partitions
    - A central location for the conda envs (`conda.cacheDir`)

=== "Local"

    If you are running AIoD locally (i.e. on a workstation), then just edit the existing `local.conf` profile as you do no need others to see these changes. We recommend you look at the [Crick profile](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/master/profiles/crick.conf) for some guidance on settings for using a GPU.

Once done, see our section on [tuning the pipeline](../nextflow/index.md#tuning-the-pipeline) for some starting guidance on how to get the most out of AIoD!


### Add a New Model Family

!!! warning "Experience Needed!"

    Adding a new model family requires familiarity with how best to run the model being added, and some Python familiarity to ensure it is integrated into the framework properly.

    The information here should be all you need to add the model, however!

You will need to add 2 things to the pipeline:

1. A `run_<MODEL NAME>.py` script (where `<MODEL NAME>` matches the [`short_name`](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/a1f49db85674b6e5405f1d29145c71dc1f0adbd3/aiod_registry/schema.py#L217) of the new schema)
2. A `conda_<MODEL NAME>.yml` environment file to run the model

#### Python Script
The existing scripts can be found here, and simply handle how that specific model is run. it is therefore completely model-specific, with the exception of a couple of things that it should have:

1. An entrypoint that loads our [argparser](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/5b5e1625ae1a293501438e8d711f27770542ff83/modules/models/resources/usr/bin/utils.py#L43-L66) to take inputs from the pipeline.
2. Saves the output masks with [our function](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/5b5e1625ae1a293501438e8d711f27770542ff83/modules/models/resources/usr/bin/utils.py#L13-L34).

Look at any of the existing scripts for guidance if you are unsure (e.g. [Cellpose](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/master/modules/models/resources/usr/bin/run_cellpose.py)), or [get in contact](../support/index.md#contact-us).

#### Conda Environment

!!! note "Why Conda?"

    Conda is the simplest option available within Nextflow for defining the environment-per-model that we need. We will eventually move everything to containers for better reproducibility and portability!

Each model family needs it's own conda environment which Nextflow will create and use for running that model. You can see the current environments [here](https://github.com/FrancisCrickInstitute/Segment-Flow/tree/master/modules/models/envs). Note that there is a "generic" and "cuda" folder to allow for variation if anything additional is needed to support GPUs (though in some cases this is not needed!).

**The only requirement for each environment is that it installs our [`aiod_utils`](https://github.com/FrancisCrickInstitute/aiod_utils) package!**


## AIoD Utilities

### Preprocessing Function
Adding a new subclass to our [`Preprocess` class](https://github.com/FrancisCrickInstitute/aiod_utils/blob/main/aiod_utils/preprocess.py) will allow this function to be used to preprocess images in `Segment-Flow`. It will also automatically create the widgets for this function in the [Napari plugin](../front_ends/napari_plugin/index.md).

The documentation and existing classes in this script should be sufficient for adding new functions!