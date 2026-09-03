# Centralised Utilities ([`aiod_utils`](https://pypi.org/project/aiod-utils/))

Almost every part of AIoD needs to do the same handful of low-level things: open an image, split it up, encode the resulting masks, and preprocess the data on the way in. To ensure everything behaves the same no matter where it happens (i.e. the [Napari plugin](../front_ends/napari_plugin/index.md) or the [Nextflow pipeline](../nextflow/index.md)), we have a centralised utilities package [`aiod_utils`](https://github.com/FrancisCrickInstitute/aiod_utils).

It is a small, dependency-light package that holds this shared behaviour in one place, and it is installed by the front-ends *and* by [every model environment](../contributing/expanding.md#conda-environment) in [`Segment-Flow`](../nextflow/index.md).

It can also be used standalone, if any of the features are useful in other projects. This page will outline the main capabilities of `aiod_utils` so you can decide if it's useful to you!

!!! info "Four Modules"

    - [**`aiod_utils.io`**](#universal-inputoutput) — loading images, and agreeing on what "the data" is
    - [**`aiod_utils.stacks`**](#dynamic-stacks) — deciding how to split an image for parallelisation
    - [**`aiod_utils.rle`**](#customised-run-length-encoding-format) — compactly storing the resulting masks
    - [**`aiod_utils.preprocess`**](#preprocessing) — modular, serialisable preprocessing steps

!!! note "Do I need to know this?"

    As a general user, no...this all happens under the hood. This page is useful if you are [adding to or developing AIoD](../contributing/index.md), or find you want to use one of its capabilities in your own project!


## "Universal" Input/Output

Bioimaging has an unfortunate number of file formats, and users should not have to care which one their data happens to be in. `aiod_utils.io` wraps [BioIO](https://github.com/bioio-devs/bioio) to provide a single entry point for loading images.

This ensures that images load consistently in both the the [Napari plugin](../front_ends/napari_plugin/index.md) and the [Nextflow pipeline](../nextflow/index.md).

### Consistent Reader Selection

BioIO can often read a given file with more than one plugin, and its default ordering does not always pick the one we want (a plain `.tiff` being handled by the OME-TIFF reader, for example, or Bio-Formats gobbling up formats a dedicated reader handles better). We apply our own opinions on top, e.g. ensuring that a `.tiff` file is read by [`bioio-tifffile`](https://github.com/bioio-devs/bioio-tifffile) not [`bioio-ome-tiff`](https://github.com/bioio-devs/bioio-ome-tiff).

!!! note "Unsupported Formats"

    While `bioformats` covers many file formats, it is a much heavier dependency, and so is an optional install:
    
    ```
    pip install aiod_utils[bioformats]
    ```

    For deployed AIoD solutions, this may not within your control. In that case, we recommend converting your data up front with e.g. [`bioformats2raw`](https://github.com/glencoesoftware/bioformats2raw).


### Describing Input Data

Metadata is frequently missing, wrong, or interpreted differently by different readers, and `Segment-Flow` needs to know image shapes *before* it starts splitting anything. `aiod_utils.io.image_paths_to_csv` writes out a simple CSV of paths and dimensions to act as the definitive source of truth for a pipeline run. See [creating the input CSV](../nextflow/index.md#creating-the-input-csv) for how this is used in practice.


## Dynamic Stacks

As covered in our [concepts page](../concepts/index.md#parallelising-substacks-to-maximize-gpu-usage), AIoD parallelises by splitting each image into **substacks** — tiles (2D) or sub-volumes (3D). `aiod_utils.stacks` defines how this is done, providing that functionality to other pipelines/projects, as well as enabling a front-end can show you what *would* happen before you run anything (i.e. displaying how many parallel jobs would be submitted).

!!! info "Why 'substack'?"

    "Tile", "patch", "chunk", and "block" all already mean something specific in adjacent tools, and a "substack" is expected to be a larger sub-unit of the original volume than those.


### Sizing to the Hardware

Given a memory budget (from the [Nextflow profile](../contributing/expanding.md#add-a-profile)), the data type, and the image shape, we calculate the largest substack that will fit (with some headroom, as the peak memory of a model is rather more than the size of its input).

Crucially, the dimensions are scaled *proportionally* rather than to a cube. Scaling each dimension by the same factor keeps the substack shaped like the image, which uses the memory budget far better for the anisotropic data that is common in volume EM, where a naive cube would waste most of the budget on a dimension that is already small.

!!! under-construction "Automatic Splitting"

    Deriving the budget automatically from the resources actually available is still in development. Until then, splitting uses sensible defaults which you can [override directly](../nextflow/index.md#individual-level).


### Requested vs. Sensible

The [`num_substacks` parameter](../nextflow/index.md#parameters-explained) lets you request a specific number of splits per dimension, or `auto` (recommended). Requests are treated as a strong preference rather than an instruction: if the resulting substacks would be absurdly small or large enough to not fit on a GPU, we fall back to the automatic calculation.


### Substack Overlap

Overlap is specified as a *fraction* per dimension rather than an absolute number of pixels. Note that the number of substacks is guaranteed, but the exact overlap may be adjusted slightly, as the two cannot always be satisfied simultaneously.


### Tracking Where Substacks Came From

Substack indices are encoded into the output filenames (`..._x0-512_y0-512_z0-32`), which is what allows the pipeline's parallel jobs to remain independent and still be [stitched back together](../nextflow/index.md#postprocessing) at the end.

Note that `aiod_utils` also handles this when downsampling, so the indices are converted with rounding that guarantees regions never overlap incorrectly.


## Customised Run Length Encoding Format

Run length encoding (RLE) is a method to losslessly compress information that is naturally suited to segmentation masks.

Our implementation has a couple of advantages over a default RLE implementation:

1. Encoding of both binary and instance masks
2. Metadata travels with the encoding, so a mask file is self-describing (it records its own type, and can carry run information)
3. Instance masks are encoded within their own bounding box, rather than against the full image, improving compression and encode/decode time

The last point is what makes this usable at scale. Models like [Segment Anything](https://github.com/facebookresearch/segment-anything) can produce hundreds of instances per slice, most of which occupy a tiny fraction of the frame; encoding each one against the whole frame means the cost grows with the *image* size rather than the *object* size. Storing an offset and a local encoding instead makes encoding dense results dramatically cheaper!

!!! info "Why not just save a TIFF?"

    A run length encoded mask is far smaller (typically ~100x-2000x) than the image it came from, which matters when results are being written by many parallel jobs, moved around a [shared cache](../concepts/index.md#caching), and reloaded into a viewer.


### Binary and Instance Masks

The two mask types are handled by the same interface, and are freely convertible in both directions:

- **Binary** — each element is a slice of a foreground/background mask, and is the natural output of semantic segmentation
- **Instance** — each element is a labelled object, allowing instances to *overlap*, which is necessary for models like SAM where the same pixel can legitimately belong to more than one mask

The mask type is inferred if not given, but we recommend being explicit!


## Preprocessing

Preprocessing lives here rather than in the pipeline for the same reason as everything else on this page: the Napari plugin needs to *offer* the options, the pipeline needs to *run* them, and a saved config needs to mean the same thing to both.

Each step is a subclass of a common `Preprocess` class that declares its own name, parameters (with defaults, human-readable labels, and tooltips), and whether it changes the image shape. Everything else follows from that:

- The [Napari plugin builds its widgets automatically](../development/index.md#automatic-ui-construction) from the declared parameters, so a new step needs no UI code
- Steps serialise to and from the `preprocess` block of a [Nextflow params file](../nextflow/index.md#preprocessing-examples), and are validated before a run starts rather than failing inside a job
- Steps that change the image shape can report their *output* shape without running, which is what lets substack sizes and job counts be calculated up front
- Parameters are rendered into a canonical string, used in filenames and hashes so that differently-preprocessed versions of the same data never collide in the [AIoD cache](../concepts/index.md#caching)

Currently available steps are downsampling (with a choice of aggregation), [CLAHE](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization#Contrast_Limited_AHE), and rank filtering (mean/median over a configurable neighbourhood).


### Preprocessing Sets

Preprocessing is specified as one *or more* sets of steps, with the pipeline running over each set in turn. This is useful for e.g. applying different CLAHE parameters to get better performance in different regions of an image, then combining the results.

Each set is ran through `Segment-Flow` separately, allowing for one set of input parameters to run a model other multiple, differently-preprocessed versions of the data. 


### Extending Preprocessing Functionality

Adding a new step is intentionally low-effort, it just needs a new sub-class. See [expanding preprocessing](../contributing/expanding.md#preprocessing-function) for details.
