# Expanding Access

As noted in our [front-end section](../front_ends/index.md), we can add any user interface to connect to AIoD and expand access. This could be anything, such as:

- A plugin in an imaging software (ImageJ, QuPath etc.)
- A web interface
- A standalone GUI

Although our Napari plugin has been expanded to include a lot of functionality, the needs of the UI are fairly lightweight:

1. The ability to send a command to a terminal (so that we can run Nextflow)
2. (Preferred) The ability to read from a Python package
    - This is so that the UI elements can be dynamically rendered from the contents of our [model registry](../concepts/index.md#model-registry)
3. (Optional) The ability to view images

Ultimately, this should be a relatively straightforward process, but cannot give any useful advice to such a wide topic. Therefore, if you have the ability to e.g. create plugins for ImageJ, we recommend that you [get in contact](../support/index.md#contact-us) for a chat and we can provide some more concrete guidance/support.