# AIoD Napari Plugin ([`aiod_napari`](https://pypi.org/project/aiod-napari/))

To easily visualise your data, and select the different models, parameters, and other options within AIoD, we have developed a [Napari plugin](https://github.com/FrancisCrickInstitute/aiod_napari).

## Installation

=== "Local"

    1. Create a virtual environment. We recommend [`uv`](https://docs.astral.sh/uv/getting-started/installation/), though `venv`, `conda`, or `pixi` all work:

        ```bash
        uv venv aiod-env # (1)!
        source aiod-env/bin/activate # (2)!
        ```

        1.  Creates an isolated Python environment in a new `aiod-env` folder inside whatever directory your terminal is currently in.
        2.  *Activates* the environment, so that everything you install next goes into this environment. You need to do this again in every new terminal. On Windows (PowerShell) use `aiod-env\Scripts\activate` instead.

    2. Install Napari: [Official guide](https://napari.org/stable/tutorials/fundamentals/installation.html)
    3. In your environment, install our plugin.

    For the latest published version:

    ```bash
    uv pip install aiod_napari
    ```

    or [you can install through the Napari interface directly](https://napari.org/dev/plugins/start_using_plugins/finding_and_installing_plugins.html).


=== "Crick HPC (NEMO)"

    An AIoD app is already available on OnDemand for you to use.

    If you would like to create your own environment so that you can install other plugins, please create a "NEMO Desktop" session, and follow the [local install instructions](#local).

=== "Non-Crick HPC"

    To use the Napari plugin, you must be able to run Napari on your institute's HPC, through something like [Open OnDemand](https://www.openondemand.org/) or some other service that provides a visual server/interface.

    If this is not possible, you can skip the GUI entirely. [Your First Segmentation (Command Line)](../../getting_started/first_headless_run.md) walks through running the pipeline from the terminal. Otherwise, contact your HPC about setting this up!

    If this is possible, then the [local installation instructions](#local) should work for you. If not, contact your HPC team or see our [contact page](../../support/index.md#contact-us) where we may be able to help.


## Tutorial
For a step-by-step walkthrough that takes you from nothing installed to a set of masks, see [Your First Segmentation (Napari)](../../getting_started/first_segmentation.md).

## Using the Plugin

The plugin itself is structured into several main widgets that you'll see in the dropdown:

- [`Evaluation`](./evaluation.md): Simple options for calculating different metrics (in isolation, or when comparing different annotation sets)
- [**`Inference`**](./inference.md): Primary interface for running the models on data!
- [`Postprocess`](./postprocess.md): Useful functions for filtering, merging, and morphing masks

For a detailed guide on using each plugin, please click the relevant widget above.

