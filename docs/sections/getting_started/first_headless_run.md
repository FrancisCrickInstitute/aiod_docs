# Your First Headless Run

This tutorial runs AIoD entirely from the terminal (no Napari/GUI). It is the counterpart to [Your First Segmentation](./first_segmentation.md) for those who want to use `Segment-Flow` directly.

That is the right choice when you are happy with a model's performance and just want to segment a lot of data, when you are working over SSH on a machine with no display, or when you want the run to be a command you can script, schedule, and put in a paper.

**You will:**

1. Install Nextflow and Conda
2. Pick a model, version, and task
3. Describe your images in a small CSV file
4. Run the pipeline and find your masks
5. Tune the model, then re-run without redoing the work

**You need:**

- Your own images (any format AIoD can read — TIFF, OME-TIFF, CZI, ND2, Zarr etc.)
- A terminal, and about 20 minutes (the first run is longer to build the environments)
- A GPU helps but is not required

!!! tip "In a hurry?"

    If you are comfortable at a terminal, this is the whole tutorial:

    1. Install [Nextflow](https://www.nextflow.io/docs/latest/install.html) and [Conda](https://www.anaconda.com/docs/getting-started/miniconda/install)
    2. Write `imgs.csv` with one row per image:
       ```csv
       img_path,num_slices,height,width,channels,dtype
       /data/img1.tif,1,120,120,1,uint8
       ```
    3. Pick a `--model`/`--model_type`/`--task` from the [model reference](../model_registry/models.md) (e.g. `--model cellpose --model_type cyto3 --task cyto`)
    4. Run Segment-Flow:
       ```bash
       nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
         --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto
       ```
    5. Extract results from the cache: `~/.nextflow/aiod/aiod_cache/cellpose/cyto3_masks/` (or change `<model>/<model_type>_masks/` as needed)

## 1. Install what runs the models
!!! warning "Windows Users"

    Nextflow does not run on Windows directly. Before you start, install the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) and do everything below inside WSL.

You need two things, and neither of them is a segmentation model:

- [Conda](https://www.anaconda.com/docs/getting-started/miniconda/install) to build an isolated environment per model
- [Nextflow](https://www.nextflow.io/docs/latest/install.html) to run the pipeline

A few steps below use small Python helpers to inspect the registry and read results back. They are optional (the pipeline never needs them) but if you want them to ease setup:

```bash
pip install aiod-registry aiod-utils
```

**Check it worked:** `nextflow -version` prints a version banner, and `conda --version`
prints a version number.

??? tip "Deploying this for other people?"

    The first run of each model pays for a full Conda environment build. If you are setting AIoD up for a group, build them all up front into a shared cache. See [pre-building model environments](../contributing/developing.md#pre-building-model-environments).

## 2. Choose a model, version, and task

Three values decide what runs:

| Flag | What it is |
|---|---|
| `--model` | the [model family](../concepts/index.md#model-family), e.g. `cellpose` |
| `--model_type` | the [version](../concepts/index.md#model-version) within it, e.g. `cyto3` |
| `--task` | what it segments, e.g. `cyto` |

Every valid combination is listed on the [model reference](../model_registry/models.md) page. You can use `aiod-registry` to query this in the terminal (if you installed `aiod_registry` into an activated environment):

```bash
python -c "
from aiod_registry import load_manifests
for name, manifest in load_manifests().items():
    for version in manifest.versions.values():
        for task in version.tasks:
            print(f'--model {name} --model_type {version.slug} --task {task}')
"
```

!!! tip "Use the slug, not the display name"

    Pass `--model_type` the `slug` (`mitonet_v1`), not the display name (`MitoNet v1`).
    The value is used verbatim as a directory name for your results, so a name with
    spaces in it gives you a directory with spaces in it.

**Check it worked:** you have three values, and they appear together on one line of that
output.

## 3. Describe your images

The pipeline does not discover your images by scanning a folder. You give it a CSV, one row per image, stating each image's dimensions. Image metadata is frequently missing, wrong, or interpreted differently by different readers, and the pipeline has to know the true shape of your data *before* it can split it up. The CSV ensures any mismatches are corrected automatically in the pipeline, and is considered to be the source of truth.

While this part is easier when automated by `aiod_napari`, we provide a helper function in `aiod_utils` and it is easily automatable.

The CSV has six columns:

```csv
img_path,num_slices,height,width,channels,dtype
/data/img1.tif,1,120,120,1,uint8
/data/img2.tif,40,2048,2048,2,uint16
```

- `img_path`: the path as seen by the machine that will run the pipeline
- `num_slices`: Z, or `1` for a 2D image
- `height`, `width`: Y and X
- `channels`: C, or `1`
- `dtype`: optional; the pipeline reads it from the image if you leave it out

Column *order* does not matter, only the names.

!!! warning "Locality of `img_path`"

    Note that above it says "the path as seen by the machine that will run the pipeline". If you are running the pipeline over SSH, the data must be on the remote machine, not local.

    For most HPC setups this is inherently true, but it's important to ensure paths are on the filesystem where computation happens.

There are three ways to produce this CSV, and for a handful of images the first is the fastest.

=== "Write it yourself"

    *Carefully* type it in, or modify a previous one that you've written/was generated.

    If you have used the Napari plugin, this will be at `~/.nextflow/aiod/aiod_cache/all_img_paths.csv`. Any previous headless run left whatever you wrote last time. Copying a known-good file and editing the paths is the lowest-risk route!

=== "Generate it"

    For a directory too large to type out, `aiod_utils` will write it for you. It needs
    the dimensions of each image handed to it, so read them first:

    ```python
    from pathlib import Path
    from aiod_utils.io import load_image, image_paths_to_csv

    paths = sorted(Path("/data/my_images").glob("*.tif"))

    dims, dtypes = [], []
    for p in paths:
        img = load_image(p)
        dims.append({"Z": img.dims.Z, "Y": img.dims.Y, "X": img.dims.X, "C": img.dims.C})
        dtypes.append(img.dtype)

    image_paths_to_csv(
        paths, "imgs.csv", dimensions=dims, dtypes=dtypes,
        overwrite=True, index=False,
    )
    ```

    `Y` and `X` are required in each dict; `Z` and `C` default to `1` if you leave them
    out. **Without `index=False`, you get an unnamed leading column of row
    numbers, which is not a valid input.**

    Note: this code snippet automatically extracts dimensions from the image metadata, which can sometimes be incorrectly encoded. The CSV file must contain the correct dimension information, so treat the result as a first draft and check it!

!!! warning "Check the numbers before you run"

    A wrong `channels` or `num_slices` is not caught when the run starts. It surfaces later inside the segmentation step, after the environment has been built and the model downloaded, as:

    ```
    Image shape {'C': 1, 'Z': 1, 'Y': 120, 'X': 120} does not match expected channels and slices (3, 40).
    ```

    A quick check of the CSV saves you finding out the slow way!

??? tip "No images to hand?"

    Any public image will do to try the mechanics. The volume our Napari tutorial uses is
    [`em_20nm_z_40_145.tif`](https://zenodo.org/records/7936982/files/em_20nm_z_40_145.tif) (clicking this link will start a direct download of the 263 MB file), a 3D FIB-SEM stack whose CSV row is
    `<path>,106,1750,1484,1,uint8`, segmentable with `--model empanada --model_type
    mitonet_mini_v1 --task mito`.

**Check it worked:** your CSV has a header row and one row per image, and the dimensions
match what you know about your data.

## 4. Run it

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 \
  -profile local \
  --img_dir imgs.csv \
  --model cellpose \
  --model_type cyto3 \
  --task cyto
```

- **`-r 0.2.1`** pins the pipeline to a specific (0.2.1) release. Without it the latest code version is used, which can change between runs (the pipeline will warn you when you do this). It is strongly recommended to always specify a pinned version to maintain reproducibility.
- **`-profile local`** runs on your current machine. On a cluster you would use a different one — see [step 9](#9-running-it-on-hpc).
- **No `--model_config`.** The model runs on its registry defaults. Later in [step 6](#6-tune-the-model) we will cover changing them.

!!! warning "The first run is slow, and that is normal"

    Before segmenting anything, AIoD builds a Conda environment for the model and
    downloads its weights. That can take several minutes. Every later run with that model
    skips both.

**Check it worked:** the run opens with a header describing exactly what it is about to
do. Confirm the model, variant and task are what you meant, and that `Revision` shows the
tag you pinned:

```
════════════════════════════════════════════════════
              █████╗ ██╗        ██████╗
             ██╔══██╗██║        ██╔══██╗
             ███████║██║ █████╗ ██║  ██║
             ██╔══██║██║██╔══██╗██║  ██║
             ██║  ██║██║╚█████╔╝██████╔╝
             ╚═╝  ╚═╝╚═╝ ╚════╝ ╚═════╝

               S E G M E N T - F L O W
════════════════════════════════════════════════════
Started         : 2026-09-16 11:44:08
Model name      : cellpose
Model variant   : cyto3
Task            : cyto
Model config    : null
Config Hash     : 4e2ebc27
Image filepaths : imgs.csv
---
Cache directory : /Users/you/.nextflow/aiod/aiod_cache/cellpose
Work directory  : /path/to/work
Profile         : local
Revision        : 0.2.1 (35a522a)
---
Full Command    : nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto
════════════════════════════════════════════════════
```

`Config Hash` identifies this exact combination of parameters, and appears in your output filenames. Note it down if you plan to run several variations so you can link outputs to input (though all configs are stored in the AIoD cache).

Because you passed no config, the run also reports that it fell back to the registry:

```
Written metadata for 'cyto3_cyto' -> model_chkpt_meta.json
Generated default config from registry params -> .../cyto3_cyto_config.yml
```

and it finishes with:

```
======================================================================
AIoD finished SUCCESSFULLY at 2026-09-16 11:49:27 after 5m 20s
======================================================================
```

## 5. Grab your results

Masks are written into the AIoD cache, organised by model and version:

```bash
ls ~/.nextflow/aiod/aiod_cache/cellpose/cyto3_masks/
```

Filenames follow a fixed pattern:

```
<image_id>[_<prep_hash>]_masks_<config_hash>_all.<ext>
```

- `image_id` is your filename with the extension folded in, so `img1.tif` becomes `img1_tif`
- `prep_hash` only appears if you used preprocessing ([step 8](#8-run-several-preprocessing-recipes-at-once))
- `config_hash` is the `Config Hash` from the run header
- `_all` refers to the final mask after the substack results have been combined.
- `ext` is the file extension. By default masks are written as `.rle`, our [compact run-length encoded format](../utilities/index.md#customised-run-length-encoding-format). To read one back:

```python
import aiod_utils.rle as rle

encoded = rle.load_encoding("img1_tif_masks_4e2ebc27_all.rle")
mask, metadata = rle.decode(encoded)

print(mask.shape, mask.dtype)   # (120, 120) uint16
print(metadata)                 # {'metadata': {'mask_type': 'instance'}}
```

Two things to expect from that array. Its dtype depends on what the model produced — `uint16` for an instance segmentation where each object has its own ID, `bool` for a semantic one. Singleton dimensions are dropped, so a single-slice image comes back 2D rather than as a stack of one.

If you would rather open the results in Fiji, QuPath or anything else, add `--output_format tiff` to the run and skip the decoding entirely. The output format is *not* part of the `Config Hash`, so re-running with `--output_format tiff` writes a `.tiff` alongside the existing `.rle` under the same name rather than being treated as a different experiment.

Combined with [`-resume`](#7-re-run-without-redoing-the-work), that makes getting a second format cheap: only the combining step re-runs, so you get the other file in seconds without segmenting anything again.

**Check it worked:** there is one `_all` file per input image, and decoding it (or opening the TIFF) gives an array the same height and width as your input.

## 6. Tune the model

Every model exposes parameters, and for some of them performance depends heavily on getting these right. You did not pass any in step 4, so the pipeline used the defaults that ship with the model registry.

Those defaults are also your template. You can easily create a copy:

```bash
python -c "
from aiod_registry import load_manifests
from aiod_registry.utils import generate_default_config, resolve_version
m = load_manifests()['cellpose']
print(generate_default_config(m, resolve_version(m, 'cyto3'), 'cyto'), end='')
" > my_config.yml
```

which gives you every parameter with its default value:

```yaml title="my_config.yml"
diameter: 0
segment_channel: 0
nucleus_channel: 0
do_3D: false
stitch_threshold: 0.0
cellprob_threshold: 0.0
flow_threshold: 0.4
niter: 0
anisotropy: null
channel_axis: null
z_axis: null
batch_size: 64
min_size: 15
```

Edit the values you care about, leave the rest, and pass it back:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
  --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto \
  --model_config my_config.yml
```

!!! tip "What do the parameters mean?"

    The [model reference](../model_registry/models.md) lists every parameter for every
    model with its description, and links to that model's own documentation. If unsure, change one
    thing at a time. With a baseline result already in hand, that is the only way to
    tell what helped!

**Check it worked:** the run header now shows your file on the `Model config` line instead of `null`, and `Config Hash` has changed, so the new results sit alongside the old ones rather than overwriting them.

## 7. Re-run without redoing the work

Add `-resume` to any run and Nextflow reuses the results of every step whose inputs have not changed:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
  --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto \
  --model_config my_config.yml \
  -resume
```

Change one parameter and only the affected steps re-run (running the model and combining the outputs).

!!! note "This is not the same as the plugin's reload"

    The Napari plugin hashes your inputs and reloads previous results automatically. Here
    you get [Nextflow's `-resume`](https://www.nextflow.io/docs/latest/cache-and-resume.html)
    instead, which needs two things: the `work` directory intact, and the run launched
    from the same directory as before — Nextflow keeps its cache in a `.nextflow`
    folder next to where you ran it, so the same command from elsewhere starts afresh.

    Keep both while you are iterating, and see [clearing the cache](../concepts/index.md#clearing-the-cache) when you are done.

Once a command has more than a few flags, move it into a parameters file:

```yaml title="params.yml"
img_dir: imgs.csv
model: cellpose
model_type: cyto3
task: cyto
model_config: my_config.yml
output_format: tiff
```

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
  -params-file params.yml -resume
```

Parameter files serve as a record of the specific configuration of each run. They are also necessary for adding preproccessing to the pipeline, which is explained in the next step.

### Naming your runs

By default the `Config Hash` is computed for you, which is safe but opaque, `..._masks_4e2ebc27_all.rle` tells you nothing six months later if you haven't kept the config for what `4e2ebc27` means. Set `param_hash` yourself and it is used verbatim instead:

```yaml title="params.yml"
img_dir: imgs.csv
model: cellpose
model_type: cyto3
task: cyto
model_config: my_config.yml
param_hash: clahe-baseline-2026-09
```

giving `example_fluo_jpg_masks_clahe-baseline-2026-09_all.rle`. Keeping it in the parameters file means one file both describes the run and names its outputs, so a result on disk can always be traced back to what produced it. You may also want to embed that into the `params-file` filename itself too!

!!! warning "You take responsibility for uniqueness"

    The computed hash guarantees that two different sets of parameters cannot write to the same filename. Naming the runs yourself menas you need to ensure that, as reusing a name with different parameters will overwrite the old ones.

    Keep the value filesystem-safe (it becomes part of a filename), and choose it *before* the run you care about: changing it alters the mask filename, which re-runs the model and the combining step, though the model download and image splitting stay cached.

**Check it worked:** every step reports `cached`, and the run finishes in seconds rather than minutes:

```
[f1/a6177b] setupModel           | 1 of 1, cached: 1 ✔
[skipped  ] downloadArtifact (2) | 2 of 2, stored: 2 ✔
[de/cd31d6] computeImageIds      | 1 of 1, cached: 1 ✔
[a8/03e7ad] splitStacks          | 1 of 1, cached: 1 ✔
[a1/f8cb8c] runModel (1)         | 1 of 1, cached: 1 ✔
[9f/0e18c5] combineStacks (1)    | 1 of 1, cached: 1 ✔

AIoD finished SUCCESSFULLY at 2026-09-16 11:52:10 after 1.5s
```

Change a parameter and the steps it affects lose their `cached` marker while the rest keep theirs.

## 8. Run several preprocessing recipes at once

Preprocessing can be as important as the choice of model, and you'll need to try several and compare. The pipeline will run the model over *each* set of preprocessing steps you give it, in one invocation:

```yaml title="params.yml"
img_dir: imgs.csv
model: cellpose
model_type: cyto3
task: cyto
preprocess:
- []
- - name: CLAHE
    params:
      clipLimit: 3.0
      tileGridSize: [12, 12]
- - name: CLAHE
    params:
      clipLimit: 8.0
      tileGridSize: [12, 12]
```

The empty set `- []` means "also run on the untouched data", which is useful for comparing the results with and without preprocessing.

Each set gets a short hash which appears in its output filenames, and the run logs a legend mapping them at the start:

```
Preprocessing hash legend for this run:
[e0337ccb] CLAHE-tileGridSize=[12, 12]-clipLimit=3.0
[4dbb4ea2] CLAHE-tileGridSize=[12, 12]-clipLimit=8.0
```

The [available steps and their parameters](../utilities/index.md#preprocessing) are documented with the utilities, and there are [more examples](../nextflow/index.md#preprocessing-examples) on the pipeline reference.

!!! note "Parameters file only"

    `preprocess` is a nested structure, so it cannot be passed on the command line — it
    has to come from a `-params-file`.

**Check it worked:** you have one `_all` mask per image *per preprocessing set*, each
carrying a different `prep_hash` in its filename.

## 9. Running it on HPC

Everything so far runs on one machine. The reason to use Nextflow at all is that moving to
a cluster is a change of one flag:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 \
  -profile crick \
  -params-file params.yml
```

The profile carries the executor, queues, and resource requests for that site. If yours does not have one yet, see [adding a profile](../contributing/expanding.md#add-a-profile).

Three things to watch out for:

- **The paths in your CSV must resolve on the machine that runs the pipeline**, not on your laptop. If you are working from a mounted drive, the CSV needs the cluster's paths (not the mounted ones!).
- **The head job has to live somewhere it will not be killed.** It runs for the duration, submitting and collecting jobs, so run it in an interactive session, a `tmux`/`screen` session, or as a batch job of its own, not on a login node!
- **Put the cache somewhere with space.** `--root_dir` defaults to your home directory, which is usually the smallest volume you have. See [choosing a cache location](../front_ends/napari_plugin/inference.md#basecache-directory).

??? tip "Tuning how the work is split"

    Two parameters control how your images are divided into parallel jobs: `memory_per_job` in the profile (how much a single job can hold) and `substack_scale` (a blanket multiplier for weaker or stronger hardware). The [tuning section](../nextflow/index.md#tuning-the-pipeline) covers both, and running locally you may want to raise `memory_per_job` from its conservative default to match your actual RAM.

## Something went wrong?

??? failure "`Missing required parameter: --img_dir`"

    `--img_dir` is the only parameter with no default, so this is the one you can forget. `img_dir does not exist: <path>` means the path is wrong!

??? failure "`Model <x> not yet implemented!`"

    The name you passed to `--model` has no script in the pipeline. The message lists every model that does. Note this is the *family* name (`empanada`), not the version (`mitonet_v1`).

??? failure "`Version '<x>' not found in manifest`"

    `--model_type` does not match that family. The error lists the valid versions with their slugs, which is what you need to give.

??? failure "None of its locations are accessible on this machine"

    The model exists in the registry, but is shared by file path rather than public download, and you cannot read that path. See [Model Location](../concepts/index.md#model-location); models marked **Restricted** on the [model reference](../model_registry/models.md) are the ones this applies to.

??? failure "`Cannot derive unique image_id`"

    Two of your images share both a filename and an extension, even if they are in different directories. The message lists every conflicting set. Rename one, or run them separately.

??? failure "`Column '<col>' not found in input image path csv file`"

    Your CSV is missing a required column. Check for a typo, and for a stray leading column if you generated it without `index=False`.

??? failure "It fails while building the model's environment"

    Conda needs network access and disk space, and a large environment can take a while (the pipeline allows an hour before giving up). Check you have several GB free where your cache lives, then run again with `-resume`; it picks up where it stopped.

    If it fails the same way twice, delete the partial environment under `~/.nextflow/aiod/conda/` and retry.

If none of these fit, [get in touch or raise an issue](../support/index.md). Please include your command, your CSV, and the error.

## Where next

<div class="grid cards" markdown>

- :material-tune: **Every parameter explained**: the [pipeline reference](../nextflow/index.md#parameters-explained) documents every input the pipeline accepts, including the ones this tutorial did not use.
- :material-image-multiple: **All the models**: the [model reference](../model_registry/models.md) lists every family, version and task, with their parameters.
- :material-scale-balance: **See what changed**: compare two results visually, or measure agreement between them, with the [Napari plugin's postprocessing tools](../front_ends/napari_plugin/postprocess.md).
- :material-server: **Scale it up**: [tuning the pipeline](../nextflow/index.md#tuning-the-pipeline) covers getting the most out of a cluster.
- :material-cog: **Add your own model**: if the model you want is missing, [adding it](../contributing/expanding.md) is a manifest entry and a script.

</div>
