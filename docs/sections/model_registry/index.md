# Model Registry

The model registry of AIoD contains information *about* the models, enabling us to pull and use this information across the [front-ends](../front_ends/index.md) and [Nextflow pipeline](../nextflow/index.md). Through this, we can allow for anyone to add models to the registry and propagate these changes through the framework with minimal user/developer effort.

Each *manifest* in the registry defines a [**model family**](../concepts/index.md#model-family) (a group of models that can be run in the same environment, e.g. Cellpose 1/2/3) that is comprised of an arbitrary number of [**model versions**](../concepts/index.md#model-version) (a specific model within a family, e.g. `cyto3`).


## Schema
The [schema](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry/blob/main/aiod_registry/schema.py) for model manifests in AIoD is intended to be lightweight, as similar efforts in the past have created too much of a burden on users and thus inhibited adoption. Our schema is defined by a [Pydantic model](https://docs.pydantic.dev/latest/), allowing us to not only validate manifests, but to ensure that when read into Python all inputs are of the appropriate type (this is useful for [automatic ingest](#automatic-ingest)).

As mentioned, each manifest itself represents a [**model family**](../concepts/index.md#model-family). In short, the schema defines:

- Meta information about the model (associated websites, publications, authors, repositories etc.)
- Information about each model version:
    - It's task (what it is doing, e.g. segmenting mitochondria)
    - It's parameters (and what they're for)
    - It's [location](../concepts/index.md#model-location) (where to find the model)

Note that the parameters, metadata etc. can be written at the top level and apply to all models in a model family, but each version can override this as needed for specific differences.


## Automatic Ingest
As it would be a monumental pain to e.g. add elements to the Napari plugin dropdowns every time we added a new model family/version, the registry contains simple functionality to allow easy ingestion of all manifests. This can then be used to [automatically construct the UI at runtime](../development/index.md#automatic-ui-construction), allowing for the interface to always reflect all possible options within the registry.


## Expanding the Registry
To add new models to the registry, see our [model contribution section](../contributing/expanding.md#model-registry). Using Pydantic, validation will be confirmed via `pytest` upon a pull request.