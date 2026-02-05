# AIoD Napari Plugin

To easily visualise your data, and select the different models, parmaters, and other options within AIoD, we have developed a [Napari plugin](https://github.com/FrancisCrickInstitute/ai-on-demand).

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

    To use the Napari plugin, you must be able to run Napari on your institute's HPC, through something like Open OnDemand or some other service that provides a visual server/interface.

    If this is not possible, either see our section on [running the Nextflow pipeline directly](../nextflow/index.md#running-the-pipeline-directly) or contact your HPC about setting this up.

    If this is possible, then the [local installation instructions](#local) should work for you. If not, contact your HPC team or see our [contact page](??) where we may be able to help.


## Tutorial

If you prefer, please find our video tutorial on setting up and using the plugin:

TODO: VIDEO LINK

## Configuration
The Napari plugin has a few key variables that you need to be aware of. The rest of the UI should be self-explanatory, but please see the [video tutorial]() above for a fuller usage guide if you prefer.

### Cache Directory

As discussed in our [AIoD Concepts](../concepts/index.md#caching) section, the cache is where models, config files, and all outputs (i.e. segmentation mask files) exist.

Where you select to place this cache has a few considerations, namely:
- If you have any space limits (common with home directories on HPC systems), select a directory you have access to with more space
- If you want to have a cache at a lab or institute level, select a central location where everyone has write access. This allows for more [reloading previous results](../concepts/index.md#reloading-results), and reduces the collective storage footprint of downloaded models (at the potential cost of privacy — see note below)

The path/directory you select will be remembered in future sessions.

!!! note

    As discussed in our [development roadmap](../development/index.md), future extension to a finetuning pipeline will therefore provide the ability to generate finetuned models, which will be stored in this cache. Therefore, if you are concerned about privacy for proprietary data or unpublished work, ensure that the cache location is somewhere local to your lab (or other group granularity) as needed.


### Execution Profile

This is the execution profile that will be used by our [Nextflow pipeline](../nextflow/index.md), and it governs how and (effectively) where the pipeline is run. It is important that you select the right profile depending on where you want to run the pipeline.

=== "Local"

    You can run the pipeline locally (i.e. on your laptop/workstation) using the `local` profile.

    Note that this is not recommended when working with larger data, unless you are using a workstation with appropriate resources (i.e. a GPU, and enough RAM for the data you are using).

=== "Crick HPC (NEMO)"

    Please select the `crick` profile. Note that this is true whether you are running it via the AIoD OnDemand app, or to NEMO [over SSH](#execution-over-ssh).

=== "Non-Crick HPC"

    You will need to setup a profile that works for your given HPC, so long as it is one of [Nextflow's executors](https://www.nextflow.io/docs/latest/executor.html). I recommend using the [`crick` profile]() as a template, and adapt it to your needs. Further guidance can be found [here]().

    See the [contributing a profile]() section for guidance on how to make this accessible to other users at your institution.

=== "Cloud"

    You will need to setup a profile that works for your given cloud platform, so long as it is one of [Nextflow's executors](https://www.nextflow.io/docs/latest/executor.html).

    See the [contributing a profile]() section for guidance on how to make this accessible to other users, if you want.


### Model Selection
Models are only shown that are both relevant to the selected task, and you have access to them. Accessible models are those in our registry defined by a URL, or by a filepath that you have access to (further details [here](../concepts/index.md#model-location)).

<!-- 2 FIGURES FOR 2 DIFFERENT TASKS -->

Once a model has been selected, if you want to modify any parameters you can change any of the defaults in the parameters section:

<!-- FIGURE OF MODEL PARAMETERS -->

For some models, the performance is highly-dependent on correct settings of these parameters. Each parameter has a tooltip that explains what it is, but it is recommended checking the official documentation of that model for further guidance. To view all parameters and tooltips, as well as any links to that model's documentation, click the :octicons-question-16: (model info) icon.

## Project Configuration
To better facilitate working across different projects, or to generally speed up working with the plugin, you can save and load "project config" files. These files capture *every single element of the plugin*, so that all options, parameters, data etc. currently selected can be recreated from this file.

Note that, as discussed [here](../concepts/index.md#project_configs), these files are stored in the central cache by default.

!!! tip

    Saving and loading config files will not only help with reproducibility and sharing AIoD usage across teams, but will greatly speed up testing different models and working on different projects with different analysis needs.

## Execution over SSH

!!! warning

    This is a more advanced feature that requires you to have SSH keys setup with access to your HPC (or to wherever the computation is taking place, e.g. a workstation).

It is possible with our Napari plugin to remotely execute the Nextflow pipeline, allowing you to e.g. run Napari locally, while running the segmentation distributed on your HPC, and receiving the results locally to view. (Doing this directly with Nextflow is simpler, and discussed [here](DIRECTLY)).

To do this, you will need:

1. SSH keys setup for your given remote computation (workstation, HPC etc.) — note that you need to know *which* key can access that compute as you will need to select it for use
2. Your remote data mounted/accessible by your local computer
3. ??

To enable this feature, you will need to enter the required information in the SSH options box:

<!-- FIGURE OF SSH OPTIONS -->

The parameters are as follows:

- _"Hostname"_: Name of where you are SSH'ing into (i.e. `ssh username@<HOSTNAME>`)
- _"Target node"_: For HPC systems where there is a login node before any compute nodes, enter the name of the actual target compute node here
- _"Username"_: The username you use to SSH (i.e. `ssh <USERNAME>@hostname`)
- _"Passphrase"_: Any passphrase associated with your SSH key
- _"Remote path prefix"_: The prefix of the path on the remote machine to the directory you have mounted (e.g. `/hpc/lab/my_lab/my_big_data`)
- _"Mounted path prefix"_: The prefix of the path on your local machine to the remote mounted directory (e.g. `/Volumes/my_big_data`)
- _"Command prepend"_: Any commands that need to be executed before the `nextflow run ...` command. This is useful for any module loading, or any other setup required

!!! example "Example with Explanation"

    If you were to mount the data on your HPC institution on a Mac, the mounted drive would be under `/Volumes/`. Let's say, `/Volumes/my_big_data`. This is your _"Mounted path prefix"_. On the HPC itself, the actual path to that folder is then your _"Remote path prefix"_, e.g. `/hpc/lab/my_lab/my_big_data`.

    If you would normally SSH to your HPC via `ssh myname@hpc.institute.org`, simply specify `hpc` as the _"Hostname"_.

    If you proxy jump to a compute node, e.g. `ssh -J myname@hpc.institute.org myname@TARGET.institute.org`, then additionally add the `TARGET` to _"Target node"_.