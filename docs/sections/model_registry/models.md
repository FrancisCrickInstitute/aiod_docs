# Available Models

Everything on this page is generated from the [model registry](./index.md), so it always
reflects the models AIoD can actually run.

The three values you need to run a model — whether [directly through Nextflow](../nextflow/index.md#running-the-pipeline-directly)
or by recognising them in the [Napari plugin](../front_ends/napari_plugin/inference.md#model-selection) —
are `--model` (the [family](../concepts/index.md#model-family)), `--model_type` (the
[version](../concepts/index.md#model-version)), and `--task`.

!!! info "Can't see a model in the plugin?"

    Models marked **Restricted** below are shared by file path rather than public
    download, so they only appear for people who can read that location. See
    [Model Location](../concepts/index.md#model-location) for why, and
    [adding a new location](../contributing/expanding.md#add-a-new-model-location) for
    how to share one more widely.

## Tasks

A [task](../concepts/index.md#task) is what a model is trying to segment. Picking one
narrows the model list to those that can do it.

{{ task_table() }}

## Model Families

{{ model_reference() }}
