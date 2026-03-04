# Development of AIoD

This page covers the current planned roadmap of AIoD, and its general design principles. This serves to inform users of planned features, and are encouraged to like/upvote features to help us prioritise with limited resources, or even help contribute if you are willing and able!

## Vision
AIoD is a user-friendly, community-extendable platform for running (deep learning) models on any compute, enabling scientists to run the latest models on their data without friction.

## Design Principles

Below are a few general, guiding principles in the design and implementation of AIoD (with examples) to help guide current and future developers.

#### Assume More
!!! quote ""
    More models, more use cases, more data formats, more data size, more analysis, more interfaces, more users.

Models are released all the time. Data continues to grow in size and complexity. It all just keeps increasing! AIoD is built ans fundamentally modular, and automates as much as possible to expand in key directions.

Any development that is for a specific model or could limit generalisation should be avoided.

!!! example "Examples"

    === "Automatic UI Construction"

        Automatically constructing the UI in our Napari plugin for the [models](https://github.com/FrancisCrickInstitute/ai-on-demand/blob/c2cd950237b0bab0aedb4a2c75ced8eab30e3391/src/ai_on_demand/inference/model_selection.py#L386-L444) and [preprocessing functions](https://github.com/FrancisCrickInstitute/ai-on-demand/blob/c2cd950237b0bab0aedb4a2c75ced8eab30e3391/src/ai_on_demand/inference/preprocess.py#L75).

        Further details can be found in my [SwissBIAS talk](https://zenodo.org/records/17312286).

    === "Compute Infrastructure"

        Our choice of Nextflow directly allows AIoD to be ported across compute environments. Although our use of conda environments within this may be limiting, the use of containers would maximise portability across users/institutes.

#### AIoD is a Computational Platform
!!! quote ""
    AIoD is a platform to run models at scale; interactive at use but not at compute.

The separation of AIoD between any number of front-ends and the Nextflow pipeline has the benefit of separating the computation 

!!! example "Examples"

    === "Execution over SSH"

        The ability to still use the Napari plugin and [execute over SSH] is a direct benefit of our front-end/Nextflow separation. This is only possible as the heavy computation is separated from where the user interacts with the data.

#### Guardrailing
!!! quote ""
    Provide all the options a user could need while minimizing the ability to make mistakes.

AIoD is for wet-lab scientists with minimal computational experience **and** advanced ML practitioners/developers. It should provide the advanced users the ability to customize anything they would want to, while ensuring that those without the knowledge can not only ignore all that, but do not get overwhelmed with 100 knobs and dials.

!!! example "Examples"

    === "Hiding Advanced Features"

        Limiting model parameter visibility in the Napari plugin to the current model only **and** hiding it behind a box ensures a cleaner UI without an overwhelming number of options. Similarly, hiding the ability to control how Segment-Flow breaks volumes into substacks ensures sensible defaults are used, but that things can be changed as/when needed (e.g. minimizing YX boundary effects in a 2D model by reducing Z split).

    === "Model Registry Expansion"

        The microscopists, wet-lab scientists etc. are the ones with the need, and thus may either hear about models they want to use, or may even finetune models on their own data and want to share these models.

        Adding to the model registry should be as simple as possible, as reducing the barrier for this will speed up expanding the capabilities of AIoD.

        At present, this is only possible by editing a JSON file and making a PR. This already presents too large a barrier, and thus the [registry API](#model-registry-api) feature needs to address this.


## Roadmap
Below is a rough roadmap of broad features either planned or in development, with a link to the appropriate issue on GitHub if one exists.

The priority of development of this roadmap is based on (in order):

1. Demand from users at the Crick
2. External interest from the community
3. Current availability of the SEAI team


### Model Registry API
We will improve the ability to programmatically interact with the model registry, simplifying the process for adding new models. This will be needed when [finetuning](#finetuning-any-model) is implemented!


### Full OME-NGFF Integration
More data necessitates NGFFs, for performance and practicalities. Standardisation and tooling necessitates OME-NGFF.

AIoD needs to move to a OME-NGFF*-first* setup, moving away from ever loading whole images in to memory, as well as providing utilities to write labels (with appropriate metadata around model etc.) to the data from our [custom `.rle` format](https://github.com/FrancisCrickInstitute/aiod_utils/blob/main/aiod_utils/rle.py) as required.

### Finetuning *any model*
In development is another workflow in `Segment-Flow`, but providing a unified way of finetuning all models within the AIoD platform, allowing users to go beyond the provided models and finetune them to their specific data, improving performance. This is a difficult thing to generalise, but this is well underway and we will be working alongside users to make this easy-to-use, but with advanced options as needed for those that understand them.

### Wider Accessibility
Some people don't use or like Napari, but they still like to view their images so don't want to use the terminal directly. Ergo, we need more front-ends, for e.g. ImageJ, QuPath etc.

This is discussed in more detail in our [UI section](../front_ends/index.md#user-interfaces), this is is an area where we are very much open to collaborate.

### Beyond Segmentation
At present, the model registry consists only of segmentation models. There is no requirement or constraint in the design that limits AIoD to this (beyond the name of our Nextflow pipeline!).

The Nextflow pipeline runs the specified model dynamically through `run_<MODEL NAME>.py` (as well as selecting the appropriate environment). In essence, the inputs are `model checkpoint + config + data = output`, none of which is specific to segmentation (beyond the format of the output).

Expanding to classification, object detection etc. therefore only requires a new level within the registry (e.g. `model_type`), new functions to save/load the output for that model (e.g. patch-/image-level labels), and a new Nextflow process to amalgamate these outputs across many parallelized substacks. Et voila!


## Contributing

Our [contribution](../contributing/index.md) sections covers how to contribute to the various parts of AIoD.

If you wish to help contribute to anything on the [roadmap](#roadmap), then you are very welcome to either get in contact with us directly, or to engage/create an issue on the [relevant repo](../../index.md#repositories) as needed. Note that the above roadmap links to existing issues where one already exists (this may be none at the moment as our issues are internal!).
