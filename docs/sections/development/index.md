# Development of AIoD

This page covers the current planned roadmap of AIoD, and its general design principles. This serves to inform users of planned features, and are encouraged to like/upvote features to help us prioritise with limited resources, or even help contribute if you are willing and able!

## Vision
AIoD is a user-friendly, community-extendable platform for running (deep learning) models on any compute, enabling scientists to run the latest models on their data without friction.

## Design Principles

Below are a few general, guiding principles in the design and implementation of AIoD (with examples) to help guide current and future developers.

#### Assume More
!!! quote ""
    More models, more use cases, more data formats, more data size, more analysis, more interfaces, more users.

Models are released all the time. Data continues to grow in size and complexity. More . AIoD needs to .


!!! example "Examples"

    === "Automatic UI Construction"

        Automatically constructing the UI in our Napari plugin for the [models](https://github.com/FrancisCrickInstitute/ai-on-demand/blob/c2cd950237b0bab0aedb4a2c75ced8eab30e3391/src/ai_on_demand/inference/model_selection.py#L386-L444) and [preprocessing functions](https://github.com/FrancisCrickInstitute/ai-on-demand/blob/c2cd950237b0bab0aedb4a2c75ced8eab30e3391/src/ai_on_demand/inference/preprocess.py#L75).

    === "??"

        ??

#### AIoD is a Computational Platform
!!! quote ""
    AIoD is a paltform to run models at scale; interative at use but not at compute.


!!! example "Examples"

    === "Execution over SSH"

        ??

    === "Finetuning"

        ??

#### Guardrailing
!!! quote ""
    Provide all the options a user could need while minimizing the ability to make mistakes.

AIoD is for wet-lab scientists with minimal computational experience **and** advanced ML practitioners/developers. It should provide the advanced users the ability to customize anything they would want to, while ensuring that those without the knowledge can not only ignore all that, but do not get overwhelmed with 100 knobs and dials.

!!! example "Examples"

    === "Hiding Advanced Features"

        Limiting model parameter visibility in the Napari plugin to the current model only **and** hiding it behind a box ensures a cleaner UI without an overwhelming number of options. Similarly, hiding the ability to control how Segment-Flow breaks volumes into substacks ensures sensible defaults are used, but that things can be changed as/when needed (e.g. minizing YX boundary effects in a 2D model by reducing Z split).

    === "Project Config Files"

        ??

    === "Model Registry Expansion"

        The microscopists, wet-lab scientists etc. are the ones with the need, and thus may either hear about models they want to use, or may even finetune models on their own data and want to share these models.

        Adding to the model registry should be as simple as possible, as reducing the barrier for this will speed up expanding the capabilities of AIoD.

        At present, this is only possible by editing a JSON file and making a PR. This already presents too large a barrier, and thus the [registry API](#model-registry-api) feature needs to address this.

## Roadmap
Below is a rough roadmap of broad features either planned or in development, with a link to the appropriate issue on GitHub if one exists.

The priority of development of this roadmap is based on (in order):

1. Demand from users at the Crick
2. External interest from the community
3. Current resource availability of the SEAI team


### Model Registry API


### Full OME-NGFF Integration
More data necessitates NGFFs, for performance and practicalities. Standardisation and tooling necessitates OME-NGFF.

AIoD needs to move to a OME-NGFF*-first* setup, moving away from ever loading whole images in to memory, as well as providing utilities to write labels (with appropriate metadata around model etc.) to the data from our [custom `.rle` format](RLEFORMAT) as required.

### Finetuning *any model*


### Wider Accessibility
Some people don't use or like Napari, but they still like to view their images so don't want to use the terminal directly. Ergo, we need more front-ends, for e.g. ImageJ, QuPath etc.

This is discussed in more detail in our [UI section](../front_ends/index.md#user-interfaces), this is is an area where we are very much open to collaborate.

### Beyond Segmentation
At present, the model registry consists only of segmentation models. There is no requirement or constraint in the design that limits AIoD to this (beyond the name of our Nextflow pipeline!).

The Nextflow pipeline runs the specified model dynamically through `run_<MODEL NAME>.py` (as well as selecting the appropriate environment). In essence, the inputs are `model checkpoint + config + data = output`, none of which is specific to segmentation (beyond the format of the output).

Expanding to classification, object detection etc. therefore only requires a new level within the registry (e.g. `model_type`), new functions to save/load the output for that model (e.g. patch-/image-level labels), and a new Nextflow process to amalgamate these outputs across many parallelized substacks. Et voila!


## Contributing

Our [contribution](../contributing/index.md) sections covers how to contribute to the various parts of AIoD, but these are generally smaller components that feed in to the capabilities of AIoD, but are not *new fearures* per se.

If you wish to help contribute to anything on the [roadmap](#roadmap), then you are very welcome to either get in contact with us directly, or to engage/create an issue on the [relevant repo](REPOLINKS) as needed. Note that the above roadmap links to existing issues where one already exists.
