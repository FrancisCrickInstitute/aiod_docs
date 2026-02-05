# Getting Started

## Prerequisites

If you just want to use AIoD as a computational pipeline, and do not require viewing your images and/or the results, then all you need is:

1. Nextflow ([installation instructions](https://www.nextflow.io/docs/latest/install.html))
2. Conda ([installation instructions](https://www.anaconda.com/docs/getting-started/miniconda/install))

A GPU is not required, but **highly recommended**.

## Setup

Setting up AIoD is simple, but is different for different environments. Please see the relevant section below, depending on whether you want to run AIoD on your own workstation, or want to run it on the HPC at your institution.

=== "Crick"

    You have access to AIoD via NEMO OnDemand through the "AI on Demand (AIoD)" app. Any issues, contact :material-slack:stp-seai.

    If you want to skip Napari and use the pipeline directly, see our page on [running the Nextflow pipeline directly]().

=== "Local (Laptop, workstation etc.)"

    ??? warning "Windows Users"

        To install and run Nextflow, you will need to have setup the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install).

    With the pre-requisites above, you can either [run the Nextflow pipeline directly](), or [install the Napari plugin]() and run AIoD from there!

    !!! tip

        For getting the most out of Nextflow, see our [advice on tuning Segment-Flow]() to ensure it uses your machine's resources appropriately.

=== "HPC (Non-Crick)"

    !!! warning
        
        This section is intended for members of HPC teams to ensure everything is setup correctly. Please send [this page]() to the relevant person at your institute, and that they can [contact us]() with any issues.

    In order to fully use AIoD, several things need to be in place:

    1. You'll need a virtual desktop environment to host/run Napari on HPC.
        - This is primarily to ease submitting jobs to the cluster, and secondarily to ensure that both Napari and our `ai-on-demand` plugin are correctly installed, for which we have a [conda environment YAML file](https://github.com/FrancisCrickInstitute/ai-on-demand/blob/main/ai-od.yml).
        - Per the name, we use OnDemand ([Open OnDemand](https://www.openondemand.org/)) to allow easy access to Napari, though many other approaches/solutions are available.
        - Whichever approach is used, it is important to note that our Napari plugin uses Python's subprocess module to run Nextflow at the command line, which must be in the appropriate environment in order for job submission to work correctly.
    2. An institution-specific profile for the Nextflow pipeline
        - If your HPC uses SLURM, we recommend using the existing Crick profile as a template, and [then submitting your own]() (to account for institution-specific names).
        - If your HPC uses another scheduler/setup, then you will need to [submit a new profile]() with the appropriate executor and options.
        - In the unlikely event that Nextflow does not support your executor/scheduler, then you will be restricted to running AIoD locally and thus limited in scale. In that instance, we recommend contacting the Nextflow team to request support for your executor!
    3. An internet connection (specifically, the ability to allow incoming traffic) to download any models from the model registry specified by a URL, which are then downloaded and cached. Without this, only models specified by accessible filepaths will be available.
            - If firewalls or other cybersecurity is in place that makes this a problem, then I recommend that the relevant models are downloaded by a privileged user, moved in a centrally-accessible location, and then you [add a new filepath for that model]() so that your users can see it.


## Tutorials

We have several tutorials to guide users through installation and usage of the main parts of AIoD:

### Napari Plugin Installation
<!-- <iframe width="560" height="315" src="https://www.youtube.com/embed/rIehsqqYFEM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->

### Running Models (via Napari)


### Running Models (via Nextflow only)
