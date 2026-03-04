# AIoD Napari Plugin

To easily visualise your data, and select the different models, parameters, and other options within AIoD, we have developed a [Napari plugin](https://github.com/FrancisCrickInstitute/ai-on-demand).

## Installation

=== "Local"

    1. Create a virtual environment using your favourite tool (`venv`, `uv`, `conda`, `pixi` etc.)
    2. Install Napari: [Official guide](https://napari.org/stable/tutorials/fundamentals/installation.html)
    3. In your environment, install our plugin via `pip`:

    For the latest published version:

    ```
    pip install aiod_napari
    ```

    or [install through Napari directly](https://napari.org/dev/plugins/start_using_plugins/finding_and_installing_plugins.html).
    
    For the most recent version:
    ```
    pip install git+https://github.com/FrancisCrickInstitute/ai-on-demand.git
    ```

=== "Crick HPC (NEMO)"

    An AIoD app is already available on OnDemand for you to use.

    If you would like to create your own environment so that you can install other plugins, please create a "NEMO Desktop" session, and following the [local install instructions](#local).

=== "Non-Crick HPC"

    To use the Napari plugin, you must be able to run Napari on your institute's HPC, through something like [Open OnDemand](https://www.openondemand.org/) or some other service that provides a visual server/interface.

    If this is not possible, either see our section on [running the Nextflow pipeline directly](../../nextflow/index.md#running-the-pipeline-directly) or contact your HPC about setting this up.

    If this is possible, then the [local installation instructions](#local) should work for you. If not, contact your HPC team or see our [contact page](../../support/index.md#contact-us) where we may be able to help.


## Tutorials
If you prefer video tutorials over the written content of this page, see the videos below:

!!! under-construction "Under Construction!"

    Video tutorials coming soon!

## Using the Plugin

The plugin itself is structured into several main widgets that you'll see in the dropdown:

- [`Evaluation`](./evaluation.md): Simple options for calculating different metrics (in isolation, or when compare different annotation sets)
- [**`Inference`**](./inference.md): Primary interface for running the models on data!
- [`Postprocess`](./postprocess.md): Useful functions for filtering, merging, and morphing masks

For a detailed guide on using each plugin, please click the relevant widget above.

