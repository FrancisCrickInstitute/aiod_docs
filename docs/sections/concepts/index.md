# AIoD Concepts

This page will cover a few key concepts of AIoD, illustrating it's power, as well as providing some tips to get the best out of it both for individuals, and for labs/institutes as a whole.

!!! info
    
    As a general user of AIoD, you do not need to know everything on this page. The "Key Parameter" sections highlight the important things on this page you may need to know for setting parameters.

## Segmenting at Scale
One of the key features of AIoD is the seamless ability to run models on large and/or many images, in a maximally parallel way. That is, the pipeline will try to do this as efficiently and quickly as possible with the compute available, e.g. creating many small jobs on a HPC system.

### Parallelising "substacks" to maximize GPU usage
Each image is split into "substacks", which are effectively tiles (2D) or sub-volumes (3D+) of an image. **This splitting occurs dynamically to the available resources of the system** (in conjunction with the specified inputs), to simultaneously maximize parallelisation and utilization of each individual job.

Similar to Dask's default chunk size, this splitting will create appropriately sized cubes to parallelize running the model over. The user can, however, modify this splitting through adjusting the `??` parameters.

Additionally, the **overlap** between these substacks can be controlled through ??. This can help with models that struggle to segment on image boundaries. Note that for overlapping substacks, options in how to reconcile differences are discussed in our [processing]() section.


## Model Registry

The [model registry](../model_registry/index.md) contains a lightweight schema for defining general information about the model, and defines some key things which affect not only how a user can interact with a model, but if they can see it in the first place!

AIoD as a whole is designed to be easily extended, allowing for the addition of new models with minimal effort, expanding options and capabilities for users. See our [dedicated section](../model_registry/index.md) for more details on adding models.

#### Model Location

The location of the model defined by the schema determines who can see and run it:

- **URL:** All users can see and run the model ([Cellpose example](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/manifests/cellpose.json#L71))
- **Filepath:** Only users that have (read-)access to the filepath will see the model in the Napari plugin and be able to run it in the Segment-Flow pipeline ([internal U-Net example](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/manifests/seai_unet.json#L25))

The schema allows for multiple locations to be defined, allowing for custom, cross-institute usage for models that cannot yet be fully public. This is also useful in the case where an institute has decentralised workstations.

!!! note "Open-Source Models"

    In general, we believe in making models publicly available for use by all, so we expect this feature is most useful for developmental/unpublished work, or when models are finetuned on proprietary/not-yet-public data.

#### Model Versions/Variants & Tasks
Each [model manifest](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/tree/main/aiod_registry/manifests) represents a "top-level" model family, something like [Cellpose](https://github.com/MouseLand/cellpose), [StarDist](https://github.com/stardist/stardist), [Segment Anything](https://github.com/facebookresearch/segment-anything), [Empanada](https://empanada.readthedocs.io/en/latest/index.html) etc. Each of these models may consist of , but the key is that they can be run within a [single environment](#conda-environments) and [Python script](ADDINGMODEL).

##### Task
What the model is used for, e.g. segmenting mitochondria.

TODO: ADD MODEL FAMILY STUFF

##### Model Version
The specific model. For example, `cyto3` is a specific version of the Cellpose model family.

## Caching

AIoD takes advantage of shared directories to cache (store) models, results, and environments to:

- Maximize reproducibility
- Minimize unnecessary computation
- Flexibly share models, meaning that models can only be run by select users (useful for work in preparation for publication, or finetuned models on private data etc.)

??? note "AIoD caches are semi-temporary"

    Although we use the word "*cache*" here, the AIoD cache is not expected to be as temporary as e.g. scratch memory. As discussed on this page, the cache has huge uses in making AIoD an effective framework, so it is recommended to have the cache in a persistent location. The Napari plugin has some simple options for inspecting and clearing the cache if users want to.

### Structure

The cache has a general structure, a schematic of which is shown below to help navigate (should you want to!):

```
$HOME/.nextflow/aiod
├── aiod_cache
│   ├── cellpose
│   │   ├── checkpoints
│   │   ├── cyto2_masks
│   │   └── cyto3_masks
│   ├── empanada
│   ├── sam2
│   ├── stardist
│   └── etc.
├── conda // On a local machine
│   ├── env-<HASH1>
│   ├── env-<HASH2>
│   └── ...
├── configs
├── project_configs
├── work // Nextflow outputs folder
└── README.md
```

By default, the cache is in the `.nextflow` folder in your home directory (`~`/`$HOME`). You can change this in the [Napari plugin](), or by using the [`??` parameter in Segment-Flow]().

!!! warning "Key Parameter"
    
    For some HPC setups (including the Crick), your default home directory will have very little space. For non-local usage, we recommend changing this parameter. Guidance on choosing where can be found [here](../front_ends/napari_plugin.md).


<!-- TODO: ADD NOTE ON CACHE CLEANING THROUGH NEXTFLOW CLEAN -->

#### Directory Explanation
##### `aiod_cache`
This folder contains the checkpoints (i.e. actual model files) and outputs for each model, organised first under each major model name (Cellpose, SAM2 etc.), then under each specific model version. There is also a `checkpoints` folder that stores the actual model 

##### `configs`
This folder contains configuration files for the model parameters. These can be [generated by the Napari plugin](#napari-plugin), or directly by users.

##### `project_configs`
This folder contains project files that can be loaded to autofill the Napari plugin interface. This simplifies switching between different projects and avoids having to make a few or many different clicks!

##### `work`
Nextflow's `work` directory is where outputs from each step of a Nextflow pipeline are stored. At the end of our pipeline, we move the final results to the relevant folder in the [`aiod_cache`](#aiod_cache) directory, so the contents of this folder can be periodically deleted (see more information on the [resume functionality](#direct-segment-flow-usage)). Further guidance on this directory can also be found in the [nf-core documentation](https://nf-co.re/docs/tutorials/storage_utilization/managing_work_directory_growth).


### Reproducibility (Hashing)
#### Napari Plugin
When using the Napari plugin (which creates all the input parameters for you), a unique hash (series of numbers & letters) is created as an identifier for your input data, options, and parameters. If the cache contains previous results with the same hash, then those results are loaded and no further computation is done.

#### Direct Segment-Flow Usage
If you are using the [Segment-Flow pipeline directly](DIRECT), then the input parameter files are yours to name and manage. You will, however, still benefit from the cache as the [Nextflow `work` directory](#work) will use Nextflow's resume capability to load previous results (for the same input).

For more information, see the [Nextflow documentation on `-resume`](https://www.nextflow.io/docs/latest/cache-and-resume.html).

### Reloading Results
The hash above is used to identify whether the cache contains any existing results, and if so will reload the results into the Napari viewer (or immediately complete for the Segment-Flow pipeline).

Therefore, **we recommend that the cache is located as centrally as possible** so that the largest number of users can reload results from previous users. This is likely to be at the group-/lab-level.

### Sharing Models
As discussed in the [model registry](#model-location) section, models can be defined by a URL or filepath.

Models defined by a URL will be downloaded into the cache under the relevant [model folder](#aiod_cache), or if by defined by a location the model will be copied into the cache.


### Conda Environments
In the Nextflow pipeline, each model is encapsulated in it's own environment. Through the [Nextflow profile](), we can set a central location for the conda environments to be created, allowing them to be shared across all users, decreasing storage usage and removing creation time.

!!! note "Why Conda?"

    Conda is the simplest option available within Nextflow for defining the environment-per-model that we need. Although containers are more reproducible, we have found that this can be more constraining when trying to generalize across institutes. We will switch to `pixi` once Nextflow fully supports this, however.


## Multiple Front-Ends
As depicted in ??, the actual computation of AIoD happens in our Nextflow pipeline. As a result, we can connect any front-end to facilitate easier access and usage of AIoD.

Please see [UI](../front_ends/index.md) section for a list of currently available front-ends, and some guidance on what's needed for any new ones.