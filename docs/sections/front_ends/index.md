# User Interfaces

As the computation of AIoD happens within the Nextflow pipeline, we can create any user interface (UI) as a front-end for users.

This could be anything, such as:

- A plugin in an imaging software (Napari, ImageJ, QuPath etc.)
- A web interface
- A standalone GUI

At present, we only have a Napari plugin implemented. If you would like to create a plugin/UI, then please see our [Contributing](../contributing/index.md) section.

Although our Napari plugin has been expanded ot include a lot of functionality, the needs of the UI are fairly lightweight:

1. The ability to send a command to a terminal (so that we can run Nextflow)
2. (Preferred) The ability to read from a Python package
    - This is so that the UI elements can be dynamically rendered from the contents of our [model registry](../concepts/index.md#model-registry)
3. (Optional) The ability to view images
