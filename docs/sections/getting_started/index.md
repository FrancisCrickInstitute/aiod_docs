# Getting Started

## Prerequisites

If you just want to use AIoD as a computational pipeline, and do not require viewing your images and/or the results, then all you need is:

1. Nextflow ([installation instructions](https://www.nextflow.io/docs/latest/install.html))
2. Conda ([installation instructions](https://www.anaconda.com/docs/getting-started/miniconda/install))

A GPU is not required, but **highly recommended**.

## Setup

Setting up AIoD is simple, but the steps are different for different environments. Please see the relevant section below, depending on whether you want to run AIoD on your own workstation, or want to run it on the HPC at your institution.

=== "Crick"

    You have access to AIoD via Napari through the "AI on Demand (AIoD)" app on NEMO OnDemand. Any issues, contact :material-slack:stp-seai or post on :material-slack:help-aiod.

    If you want to skip Napari and use the pipeline directly, see our page on [running the Nextflow pipeline directly](../nextflow/index.md#running-the-pipeline-directly).

=== "Local (Laptop, workstation etc.)"

    !!! warning "Windows Users"

        To install and run Nextflow, you will need to have setup the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). Then you can install the [prerequisites](#prerequisites).

    With the prerequisites above, you can either run the Nextflow pipeline directly ([walkthrough](./first_headless_run.md), [reference](../nextflow/index.md#running-the-pipeline-directly)), or [install the Napari plugin](../front_ends/napari_plugin/index.md#installation) and run AIoD from there!

    !!! tip

        For getting the most out of Nextflow, see our [advice on tuning Segment-Flow](../nextflow/index.md#tuning-the-pipeline) to ensure it uses your machine's resources appropriately.

=== "HPC (Non-Crick)"

    !!! warning
        
        This section is intended for members of HPC teams to ensure everything is setup correctly. Please send this page to the relevant person at your institute, and note that they can [contact us](../support/index.md#contact-us) with any issues.

    In order to fully use AIoD, several things need to be in place:

    1. You'll need a virtual desktop environment to host/run Napari on HPC (or, for users happy at the command line, no Napari at all — see [running the pipeline directly](../nextflow/index.md#running-the-pipeline-directly))
        - This is primarily to ease submitting jobs to the cluster, and secondarily to ensure that both Napari and our `aiod-napari` plugin are correctly installed, for which we have a [conda environment YAML file](https://github.com/FrancisCrickInstitute/aiod_napari/blob/main/ai-od.yml) or a [uv lockfile](https://github.com/FrancisCrickInstitute/aiod_napari/blob/main/uv.lock).
        - Per the name, we use OnDemand ([Open OnDemand](https://www.openondemand.org/)) to allow easy access to Napari, though many other approaches/solutions are available.
        - Whichever approach is used, it is important to note that our Napari plugin uses Python's subprocess module to run Nextflow at the command line, which must be in the appropriate environment in order for job submission to work correctly.
    2. An institution-specific profile for the Nextflow pipeline
        - If your HPC uses SLURM, we recommend using the [existing Crick profile](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/master/profiles/crick.conf) as a template, and [then submitting your own](../contributing/expanding.md#add-a-profile) (to account for institution-specific names).
        - If your HPC uses another scheduler/setup, then you will need to [submit a new profile](../contributing/expanding.md#hpc) with the appropriate executor and options.
        - In the very unlikely event that Nextflow does not support your executor/scheduler, then you will be restricted to running AIoD locally and thus limited in scale. In that instance, we recommend contacting the Nextflow team to request support for your executor!
    3. An internet connection (specifically, the ability to allow downloading from a URL) to download any models from the model registry specified by a URL, which are then downloaded and cached. Without this, only models specified by local, accessible filepaths will be available.
        - If firewalls or other cybersecurity is in place that makes this a problem, then we recommend that the relevant models are downloaded by a privileged user, moved to a centrally-accessible location, and then you [add a new filepath for that model](../contributing/expanding.md#add-a-new-model-location) so that your users can see it.

    Once the profile is in place, we strongly recommend [pre-building the model environments](../contributing/developing.md#pre-building-model-environments) into your shared conda cache. Otherwise the first user to try each model waits for a full environment build, and any failure during it shows up as a confusing error partway through the run.


## Tutorials

We have several tutorials to guide users through installation and usage of the main parts of AIoD:

!!! under-construction "Under Construction!"

    Short video walkthroughs of each workflow are coming soon! Until then, the talk below covers AIoD as a whole, and the written tutorials cover the main entrypoints (Napari & Nextflow) step-by-step.

### Introductory Talk

A recorded talk introducing AIoD for a general audience. It's an hour in total, so if you are here to get something running quickly, start with the written tutorials below instead!

<iframe class="docs-embed"
  src="https://www.youtube-nocookie.com/embed/2yWhYc0Ibhw"
  title="AI OnDemand: An extendable, user-friendly framework for segmenting images at scale"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  referrerpolicy="strict-origin-when-cross-origin"
  allowfullscreen></iframe>

### Running Models (via Napari)
For a step-by-step written walkthrough of a first run, see [Your First Segmentation (Napari)](./first_segmentation.md).


### Running Models (via Nextflow only)
To run the pipeline straight from the terminal (with no Napari at all), see [Your First Segmentation (Command Line)](./first_headless_run.md).
