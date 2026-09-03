# Model Registry ([`aiod_registry`](https://pypi.org/project/aiod-registry/))

The model registry of AIoD contains information *about* the models, enabling us to pull and use this information across the [front-ends](../front_ends/index.md) and [Nextflow pipeline](../nextflow/index.md). Through this, we can allow for anyone to add models to the registry and propagate these changes through the framework with minimal user/developer effort.

Each *manifest* in the registry defines a [**model family**](../concepts/index.md#model-family) (a group of models that can be run in the same environment, e.g. Cellpose 1/2/3) that is comprised of an arbitrary number of [**model versions**](../concepts/index.md#model-version) (a specific model within a family, e.g. `cyto3`).


## Schema
The [schema](https://github.com/FrancisCrickInstitute/aiod_registry/blob/main/aiod_registry/schema.py) for model manifests in AIoD is intended to be lightweight, as similar efforts in the past have created too much of a burden on users and thus inhibited adoption. Our schema is defined by a [Pydantic model](https://docs.pydantic.dev/latest/), allowing us to not only validate manifests, but to ensure that when read into Python all inputs are of the appropriate type (this is useful for [automatic ingest](#automatic-ingest)). Validation is strict — a field name that is not in the schema is an error rather than being silently ignored.

As mentioned, each manifest itself represents a [**model family**](../concepts/index.md#model-family). In short, the schema defines:

- Meta information about the model (associated websites, publications, authors, repositories etc.)
- Information about each model version:
    - It's task (what it is doing, e.g. segmenting mitochondria)
    - It's parameters (and what they're for)
    - It's [locations](../concepts/index.md#model-location) (where to find the model — one or more, see below)

Note that the parameters, metadata etc. can be written at the top level and apply to all models in a model family, but each version can override this as needed for specific differences.

These nest as a family, containing versions, containing tasks, each of which has one or more locations:

```
manifest          name, short_name, metadata, params, config, usage_guide
└── versions      axes, slug, metadata
    └── tasks     params, metadata
        └── locations   location, config_path
```

A few fields are easy to overlook:

- [**`short_name`**](https://github.com/FrancisCrickInstitute/aiod_registry/blob/eb0871750c129fa18c080bff014da97d0bc50655/aiod_registry/schema.py#L268) — auto-derived from `name` if omitted (lowercased, spaces to underscores). It also names the [Python script and conda environment](../contributing/expanding.md#add-a-new-model-family_1) in the pipeline, so it is usually worth setting explicitly.
- [**`slug`**](https://github.com/FrancisCrickInstitute/aiod_registry/blob/eb0871750c129fa18c080bff014da97d0bc50655/aiod_registry/schema.py#L260-L263) — a filesystem-safe identifier for a version, auto-derived from the version name the same way. Set it explicitly where the model's own identifiers are case-sensitive (as PanSeg's are), since auto-derivation lowercases.
- [**`axes`**](https://github.com/FrancisCrickInstitute/aiod_registry/blob/eb0871750c129fa18c080bff014da97d0bc50655/aiod_registry/schema.py#L66-L75) — the dimension order a version expects, e.g. `YX` for 2D or `ZYX` for 3D. Must include both `Y` and `X`.
- [**`param_type`**](https://github.com/FrancisCrickInstitute/aiod_registry/blob/eb0871750c129fa18c080bff014da97d0bc50655/aiod_registry/schema.py#L108-L176) — a channel-selection parameter is declared with `param_type: channel`, with `channel_start` setting whether the first option is `-1` (use the image as-is) or `0` (the first channel). A list-valued parameter can also carry a `default` naming which option is preselected.


## Automatic Ingest
As it would be a monumental pain to e.g. add elements to the Napari plugin dropdowns every time we added a new model family/version, the registry contains simple functionality to allow easy ingestion of all manifests. This can then be used to [automatically construct the UI at runtime](../development/index.md#automatic-ui-construction), allowing for the interface to always reflect all possible options within the registry.

The same information is used to generate a default config file per model from its declared parameters, which the [Nextflow pipeline](../nextflow/index.md) falls back to when a user supplies none. These are committed to the registry and regenerated with the `aiod-gen-configs` command.


## Expanding the Registry
To add new models to the registry, see our [model contribution section](../contributing/expanding.md#model-registry). Using Pydantic, validation will be confirmed via `pytest` upon a pull request.