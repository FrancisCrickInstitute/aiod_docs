# Troubleshooting

Common problems and what they usually mean. If none of these fit, please
[get in touch or raise an issue](./index.md#raising-an-issue), including what you selected and the full error message.

## Installation and startup

??? failure "The plugin isn't in Napari's Plugins menu"

    Napari is almost definitely running in a different environment from the one you installed the plugin into. Activate the environment and launch Napari from that same terminal:

    ```bash
    source aiod-env/bin/activate # (1)!
    napari # (2)!
    ```

    1.  Replace `aiod-env` with whatever you named your environment. On Windows
        (PowerShell) the equivalent is `aiod-env\Scripts\activate`.
    2.  Your terminal prompt should now show the environment name in brackets. Launching
        Napari in this environment is what guarantees it sees the plugin.

    Installing Napari system-wide and the plugin into a virtual environment (or vice versa) is the usual cause.

??? failure "The run fails immediately, mentioning `nextflow`"

    The plugin runs `nextflow` as a command, so it has to be on your `PATH` *in the
    environment Napari was started from*, not just installed somewhere on the
    machine. Check with:

    ```bash
    nextflow -version
    ```

    in the terminal you launched Napari from. If that fails, revisit the
    [prerequisites](../getting_started/index.md#prerequisites).

    On HPC this often means a module has to be loaded before Napari starts, rather than afterwards.

## Before the run starts

??? failure "The run is rejected because two images share a filename"

    Images are identified by filename *and* extension, so two files sharing both collide even when they are in different directories. `sample1.tiff` in two folders is a conflict; `sample1.tiff` and `sample1.czi` are not.

    Rename or move one of them, or run them separately (though this may override results from the first run). The error names every conflicting set, so it should be clear what needs renaming!

??? failure "The run is rejected because a file's extension isn't recognised"

    Unique file identity is derived from the filename and file extension, so an extension that cannot be read cannot be processed. The error lists the extensions that *are* accepted.

    For a format that should be supported but isn't, you may need the optional Bio-Formats reader, or to convert the data up front. See [unsupported formats](../utilities/index.md#consistent-reader-selection).

??? failure "A model I expected isn't in the list"

    Two likely reasons:

    1. **The task filter.** The model list is narrowed by the selected task, so checkthe task matches what that model does. The [model reference](../model_registry/models.md) lists every model against its tasks.
    2. **It's shared by file path, not public download.** Models marked [**Restricted**](../model_registry/models.md) are only visible to people who can read the location they live at (see [Model Location](../concepts/index.md#model-location)). If you should have access, check you can read that path; if you want it shared more widely, [add another location](../contributing/expanding.md#add-a-new-model-location).

## During the run

??? failure "It fails while setting up the environment for the model"

    This is `conda` building the model's environment, which needs both network access and disk space. Check you have several GB free wherever your cache directory points, and that you can reach the internet, then run it again.

    If it fails the same way twice, conda may have left a partial environment behind. Delete the offending environment under `conda/` in your [cache directory](../concepts/index.md#structure) (e.g. `~/.nextflow/aiod/conda/env-<HASH>`) and retry.

    Deploying for a whole institution? Building every environment once, up front in central location that all users have access to, and the [execution profile](../contributing/expanding.md#add-a-profile) points to. See [pre-building environments](../contributing/developing.md#pre-building-model-environments).

??? failure "You run out of disk space partway through"

    The [`work` directory](../concepts/index.md#work) is almost always the culprit: it holds Nextflow's intermediate outputs *and* a preprocessed OME-Zarr copy of your data per set of preprocessing parameters. It is the largest thing the pipeline produces.

    Clear it with [`nextflow clean`](../concepts/index.md#clearing-the-cache), which leaves your results alone. If you hit this repeatedly, your [cache directory](../front_ends/napari_plugin/inference.md#basecache-directory) is probably on a small home-directory quota and should be moved somewhere with more space.

## After the run

??? failure "The channel/Z dropdowns are wrong, or the image is split along the wrong axis"

    The axis order is read from file metadata, which can be missing, wrong, or read incorrectly. Set it yourself with the [axes override](../front_ends/napari_plugin/inference.md#advanced-options) under Data Selection's Advanced Options, then run again.

    Worth checking *before* a long run, since it determines how the data is split.

??? failure "The masks are one blob instead of separate objects"

    That is a *semantic* rather than *instance* segmentation, which is the default.
    Either set the output type before running (**Run Pipeline :material-arrow-right:
    Advanced Options :material-arrow-right: Output mask type** to `instance`), or apply
    [Label masks](../front_ends/napari_plugin/postprocess.md#label-masks) from the
    Postprocess widget afterwards.

??? failure "The results just aren't very good"

    Not everything is a bug, no model is right everywhere! In rough order of effort:
    adjust the model's [parameters](../front_ends/napari_plugin/inference.md#model-selection)
    (every one has a tooltip, and the model's own documentation is linked from the
    :octicons-question-16: button), try
    [preprocessing](../front_ends/napari_plugin/inference.md#preprocessing) such as
    CLAHE, or try a different model on the same task from the
    [model reference](../model_registry/models.md).

    Running several preprocessing sets in one go and
    [comparing the outputs visually](../front_ends/napari_plugin/postprocess.md#visualize-overlaps)
    is usually the quickest way to see what is actually helping.

    Otherwise, if no model in AIoD, with any preprocessing or parameter tuning can give a good result, we encourage you to identify a model in literature that could work, and then you can [ask us to add that model to AIoD](./index.md#contact-us).
