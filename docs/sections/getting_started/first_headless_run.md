# Your First Segmentation (Command Line)

This tutorial runs AIoD entirely from the terminal (no Napari/GUI). It is the counterpart to [Your First Segmentation (Napari)](./first_segmentation.md) for those who want to use `Segment-Flow` directly.

Use it when you are happy with a model's performance and want to segment a lot of data, when you are working over SSH on a machine with no display, or when you want the run to be a command you can script, schedule, and put in a paper.

**You will:**

1. Install Nextflow and Conda
2. Pick a model, version, and task
3. Describe your images in a small CSV file
4. Run the pipeline and find your masks
5. Tune the model, then re-run without redoing the work

**You need:**

- Your own images (any format AIoD can read, such as TIFF, OME-TIFF, CZI, ND2 or Zarr)
- Some familiarity with the terminal: running commands, moving between folders, and editing text files. If that's new to you, [Your First Segmentation (Napari)](./first_segmentation.md) is a gentler place to start.
- About 20 minutes (the first run takes longer while it builds the model's environment)
- A GPU helps but is not required

!!! tip "In a hurry?"

    If you are comfortable at a terminal, this is the whole tutorial:

    1. Install [Nextflow](https://www.nextflow.io/docs/latest/install.html) and [Conda](https://www.anaconda.com/docs/getting-started/miniconda/install)
    2. Create a file `imgs.csv` with one row per image:
       ```csv
       img_path,num_slices,height,width,channels,dtype
       /data/img1.tif,1,120,120,1,uint8
       ```
    3. Pick a `--model`/`--model_type`/`--task` from the [model reference](../model_registry/models.md) (e.g. `--model cellpose --model_type cyto3 --task cyto`)
    4. Run `Segment-Flow`:
       ```bash
       nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
         --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto
       ```
    5. Extract results from the cache: `~/.nextflow/aiod/aiod_cache/cellpose/cyto3_masks/` (or change `<model>/<model_type>_masks/` as needed)

## 1. Set up

!!! warning "Windows Users"

    Nextflow does not run on Windows directly. Install the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) and do everything below inside WSL.

### 1.1 Nextflow and Conda

These two tools are all the pipeline needs. Nextflow runs the pipeline, and Conda builds an isolated environment for each model. Install [Nextflow](https://www.nextflow.io/docs/latest/install.html) and [Conda](https://www.anaconda.com/docs/getting-started/miniconda/install) by following their own instructions. You never install the models themselves; AIoD will handle that for you.

**Check it worked:** run `nextflow -version` and then `conda --version`. Each should print a version number.
{: .check }

??? tip "Deploying this for other people?"

    The first time each model runs, Conda has to build its environment, which can take a while. If you are setting AIoD up for a group, build them all in advance into a shared cache. See [pre-building model environments](../contributing/developing.md#pre-building-model-environments).

### 1.2 AIoD's Python helpers (recommended)

The pipeline itself doesn't need Python, but a few steps below use two of our Python packages to list models, write your image CSV, create a config file, and read results back. We recommend installing them, as they save a lot of typing. WHowever, where a step uses them, it also says how to manage without so this is optional.

Install them into a fresh environment (we use [`uv`](https://docs.astral.sh/uv/getting-started/installation/), but any environment manager works):

```bash
uv venv aiod-env
source aiod-env/bin/activate
uv pip install aiod-registry aiod-utils
```

### 1.3 A folder to work in

Make a folder for this tutorial (e.g. `mkdir aiod-tutorial && cd aiod-tutorial`) and run everything from there. The commands below refer to `imgs.csv`, `my_config.yml` and `params.yml` by relative path, and [`-resume`](#7-re-run-without-redoing-the-work) only works when you launch from the same directory each time (without more specific configuration explained [here](../nextflow/index.md#running-the-pipeline-directly)).

## 2. Choose a model, version, and task

Three values select the unique model:

| Flag | What it is |
|---|---|
| `--model` | the [model family](../concepts/index.md#model-family), e.g. `cellpose` |
| `--model_type` | the [version](../concepts/index.md#model-version) within it, e.g. `cyto3` |
| `--task` | what it segments, e.g. `cyto` |

Every valid combination is listed on the [model reference](../model_registry/models.md) page. For `--model_type`, use the version's short name (e.g. `mitonet_v1`), not its display name (`MitoNet v1`).

??? tip "Listing them from the terminal"

    With the helpers from [step 1.2](#12-aiods-python-helpers-recommended) installed and `aiod-env` activated, this prints every valid combination, one per line, ready to paste into a command:

    ```bash
    python -c "
    from aiod_registry import load_manifests
    for name, manifest in load_manifests().items():
        for version in manifest.versions.values():
            for task in version.tasks:
                print(f'--model {name} --model_type {version.slug} --task {task}')
    "
    ```

**Check it worked:** you have three values that appear together on the model reference (or on one line of the listing above).
{: .check }

## 3. Describe your images

The pipeline doesn't scan a folder for images. Instead, you give it a CSV file listing each image and its dimensions. Image metadata is often missing or wrong, and the pipeline needs the true (intended) shape of each image before it can split it into pieces, so the CSV is treated as the source of truth.

Save it as `imgs.csv` in your working folder. It has six columns:

```csv
img_path,num_slices,height,width,channels,dtype
/data/img1.tif,1,120,120,1,uint8
/data/img2.tif,40,2048,2048,2,uint16
```

- `img_path`: the full path to the image, as seen by the machine that will run the pipeline
- `num_slices`: Z, or `1` for a 2D image
- `height`, `width`: Y and X
- `channels`: C, or `1`
- `dtype`: optional; the pipeline reads it from the image if you leave it out

Column *order* does not matter, only the names.

!!! warning "Paths are on the machine that runs the pipeline"

    If you run the pipeline over SSH or on a cluster, `img_path` must point to where the data lives on *that* machine, not on your laptop. For most HPC setups this is already the case, but check it if you are working from a mounted drive.

There are two ways to produce this CSV. For a handful of images, writing it yourself is quickest.

=== "Write it yourself"

    Type it in carefully, or copy one you (or the Napari plugin) wrote before and edit the paths. The plugin writes one to `~/.nextflow/aiod/aiod_cache/all_img_paths.csv`. Starting from a file that already works is the safest option.

=== "Generate it"

    For a directory too large to type out, `aiod_utils` can write it for you. Save the following as `make_csv.py` in your working folder, change `/data/my_images` to your image folder (and `*.tif` to your file extension):

    ```python title="make_csv.py"
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

    Then, with `aiod-env` activated, run:

    ```bash
    python make_csv.py
    ```

    Keep `index=False`: without it, the CSV gets an extra unnamed column of row numbers, which the pipeline rejects.

    The script reads the dimensions from each image's metadata, which can be wrong. Treat the result as a first draft and check it.

!!! warning "Check the numbers before you run"

    A wrong `channels` or `num_slices` is not caught when the run starts. It only shows up later, during segmentation, after the environment has been built and the model downloaded, as an error like:

    ```text
    Image shape {'C': 1, 'Z': 1, 'Y': 512, 'X': 512} does not match expected channels and slices (3, 40).
    ```

    So it is worth checking the CSV before you start.

??? tip "No images to hand?"

    Any public image will do to try the mechanics. The volume our Napari tutorial uses is [`em_20nm_z_40_145.tif`](https://zenodo.org/records/7936982/files/em_20nm_z_40_145.tif) (clicking this link will start a direct download of the 263 MB file), a 3D FIB-SEM stack whose CSV row is `<path>,106,1750,1484,1,uint8`, segmentable with `--model empanada --model_type mitonet_mini_v1 --task mito`.

**Check it worked:** your CSV has a header row and one row per image, and the dimensions match what you know about your data.
{: .check }

## 4. Run it

From your working folder, run:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 \
  -profile local \
  --img_dir imgs.csv \
  --model cellpose \
  --model_type cyto3 \
  --task cyto
```

- **`-r 0.2.1`** pins the pipeline to a specific (0.2.1) release. Without it, the latest code is used, which can change between runs (the pipeline will warn you when you do this). Always pin a version so your runs are reproducible.
- **`-profile local`** tells the pipeline what kind of machine it is running on, so it uses that machine's resources sensibly. `local` is for a laptop or workstation; clusters have their own profile (see [step 9](#9-running-it-on-hpc)).

!!! tip "Want TIFFs for Fiji or QuPath?"

    Add `--output_format tiff` to the command. Otherwise, masks are saved in AIoD's compact `.rle` format, which you read back with Python ([step 5](#5-grab-your-results)).

!!! warning "The first run is slow, and that is normal"

    Before segmenting anything, AIoD builds a Conda environment for the model and downloads its weights. That can take several minutes. Every later run with that model skips both.

**Check it worked:** the run opens with a header describing what it is about to do. Confirm the model, variant and task are what you meant, and that `Revision` shows the tag you pinned:
{: .check }

```text
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

`Config Hash` identifies this exact combination of parameters, and appears in your output filenames. Note it down if you plan to run several variations so you can match outputs to settings (all configs are also stored in the AIoD cache).

Because you passed no model config, the run uses the model's default parameters from the registry and says so:

```text
Written metadata for 'cyto3_cyto' -> model_chkpt_meta.json
Generated default config from registry params -> .../cyto3_cyto_config.yml
```

and it finishes with:

```text
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

```text
<image_id>[_<prep_hash>]_masks_<config_hash>_all.<ext>
```

- `image_id` is your filename with the extension folded in, so `img1.tif` becomes `img1_tif`
- `prep_hash` only appears if you used preprocessing ([step 8](#8-run-several-preprocessing-recipes-at-once))
- `config_hash` is the `Config Hash` from the run header
- `_all` marks the final mask, after the pieces the image was split into have been combined
- `ext` is `.tiff` if you used `--output_format tiff`, otherwise `.rle`

TIFFs open directly in Fiji, QuPath and most other image software. `.rle` is our [compact run-length encoded format](../utilities/index.md#customised-run-length-encoding-format), which you read back with the helpers from [step 1.2](#12-aiods-python-helpers-recommended):

```python
import aiod_utils.rle as rle

encoded = rle.load_encoding("img1_tif_masks_4e2ebc27_all.rle")
mask, metadata = rle.decode(encoded)

print(mask.shape, mask.dtype)   # (120, 120) uint16
print(metadata)                 # {'metadata': {'mask_type': 'instance'}}
```

The array's dtype depends on what the model produced: `uint16` for an instance segmentation, where each object has its own ID, or `bool` for a semantic one. Singleton dimensions are dropped, so a single-slice image comes back 2D rather than as a stack of one.

??? tip "Already ran it, but want TIFFs as well?"

    Run the same command again with `--output_format tiff -resume` added. The output format is not part of the `Config Hash`, so nothing is segmented again: only the final combining step re-runs, and it writes a `.tiff` next to each existing `.rle`, with the same name. See [step 7](#7-re-run-without-redoing-the-work) for how `-resume` works.

**Check it worked:** there is one `_all` file per input image, and opening it (or decoding the `.rle`) gives an array the same height and width as your input.
{: .check }

## 6. Tune the model

Every model has parameters, and for some models, performance depends heavily on getting these right. We did not pass any in step 4, so the pipeline used the defaults that come with the model registry.

Those defaults make a good starting point for your own config file. With `aiod-env` activated, run this from your working folder to write them to `my_config.yml`:

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

Without the helpers, download the model family's default config from the registry's [`default_configs`](https://github.com/FrancisCrickInstitute/aiod_registry/tree/main/aiod_registry/default_configs) folder instead:

```bash
curl -o my_config.yml https://raw.githubusercontent.com/FrancisCrickInstitute/aiod_registry/main/aiod_registry/default_configs/cellpose.yaml
```

The downloaded file starts with a "do not edit manually" comment. That applies to the copy in the registry, not yours, so edit your copy freely.

This is a YAML file: one `name: value` per line. Change the values you care about, and leave the names (and any indentation) as they are. Then pass it to the pipeline:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
  --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto \
  --model_config my_config.yml
```

!!! tip "What do the parameters mean?"

    The [model reference](../model_registry/models.md) describes every parameter for every model, and links to that model's own documentation. Change one thing at a time, so you can tell which change made the difference.

**Check it worked:** the run header now shows your file on the `Model config` line instead of `null`, and `Config Hash` has changed, so the new results sit alongside the old ones rather than overwriting them.
{: .check }

## 7. Re-run without redoing the work

Add `-resume` to any run and Nextflow reuses the results of every step whose inputs have not changed:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
  --img_dir imgs.csv --model cellpose --model_type cyto3 --task cyto \
  --model_config my_config.yml \
  -resume
```

For example, if you change a value in `my_config.yml` and re-run with `-resume`, only the model and the final combining step run again. The environment, model download and image splitting are reused from last time.

**Check it worked:** run the command above a second time without changing anything. Every step reports `cached`, and the run finishes in seconds rather than minutes:
{: .check }

```text
[f1/a6177b] setupModel           | 1 of 1, cached: 1 ✔
[skipped  ] downloadArtifact (2) | 2 of 2, stored: 2 ✔
[de/cd31d6] computeImageIds      | 1 of 1, cached: 1 ✔
[a8/03e7ad] splitStacks          | 1 of 1, cached: 1 ✔
[a1/f8cb8c] runModel (1)         | 1 of 1, cached: 1 ✔
[9f/0e18c5] combineStacks (1)    | 1 of 1, cached: 1 ✔

AIoD finished SUCCESSFULLY at 2026-09-16 11:52:10 after 1.5s
```

!!! note "This is not the same as the plugin's reload"

    The Napari plugin hashes your inputs and reloads previous results automatically. Here you get [Nextflow's `-resume`](https://www.nextflow.io/docs/latest/cache-and-resume.html) instead, which needs two things: the `work` directory intact, and the run launched from the same folder as before. Nextflow keeps its record of previous runs in a `.nextflow` folder next to where you ran it, so the same command run from elsewhere starts afresh.

    Keep both while you are iterating, and see [clearing the cache](../concepts/index.md#clearing-the-cache) when you are done.

Once a command has more than a few flags, it is easier to keep them in a parameters file. Save this as `params.yml` in your working folder:

```yaml title="params.yml"
img_dir: imgs.csv
model: cellpose
model_type: cyto3
task: cyto
model_config: my_config.yml
output_format: tiff
```

and pass it with `-params-file`:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 -profile local \
  -params-file params.yml -resume
```

You can still add parameters on the command line alongside `-params-file`. If the same parameter appears in both, the command line wins.

A parameters file is also a record of exactly how a run was configured, and it is the only way to add preprocessing, covered in the [next step](#8-run-several-preprocessing-recipes-at-once).

### Naming your runs

By default, the `Config Hash` is computed for you. It avoids clashes, but it is hard to read: `img1_tif_masks_4e2ebc27_all.rle` tells you nothing six months later if you have lost track of what `4e2ebc27` means. Set `param_hash` in your parameters file and it is used in place of the computed hash:

```yaml title="params.yml"
img_dir: imgs.csv
model: cellpose
model_type: cyto3
task: cyto
model_config: my_config.yml
param_hash: cyto3-baseline-2026-09
```

which gives `img1_tif_masks_cyto3-baseline-2026-09_all.rle`. The parameters file then records both the settings and the output name, so you can always tell which settings produced a result. You could name the parameters file to match (e.g. `cyto3-baseline-2026-09.yml`).

!!! warning "You take responsibility for uniqueness"

    The computed hash guarantees that two different sets of parameters cannot write to the same filename. When you name runs yourself, that is up to you: reusing a name with different parameters overwrites the earlier results.

    Keep the value filesystem-safe, as it becomes part of a filename. Changing `param_hash` on a run you have already done changes the output filename, so the model and combining steps run again (the model download and image splitting are still reused).

## 8. Run several preprocessing recipes at once

Preprocessing can matter as much as the choice of model, so it is worth trying a few options and comparing them. The pipeline runs the model over *each* set of preprocessing steps you give it, in one run:

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

The indentation here matters, so copy the example and change the values rather than retyping it. The empty set `- []` means "also run on the untouched data", which lets you compare the results with and without preprocessing.

Each set gets a short hash which appears in its output filenames, and the run logs a legend mapping them at the start:

```text
Preprocessing hash legend for this run:
[e0337ccb] CLAHE-tileGridSize=[12, 12]-clipLimit=3.0
[4dbb4ea2] CLAHE-tileGridSize=[12, 12]-clipLimit=8.0
```

The [available steps and their parameters](../utilities/index.md#preprocessing) are documented with the utilities, and there are [more examples](../nextflow/index.md#preprocessing-examples) on the pipeline reference.

!!! note "Parameters file only"

    `preprocess` is a nested structure, so it cannot be passed on the command line. It has to come from a `-params-file`.

**Check it worked:** you have one `_all` mask per image *per preprocessing set*, each carrying a different `prep_hash` in its filename.
{: .check }

## 9. Running it on HPC

To run on a cluster, you run the same command *on the cluster* (e.g. after logging in over SSH), with that cluster's profile in place of `local`. At the Crick, that profile is `crick`:

```bash
nextflow run FrancisCrickInstitute/Segment-Flow -r 0.2.1 \
  -profile crick \
  -params-file params.yml
```

The profile tells Nextflow how to submit jobs on that cluster: which scheduler it uses, which queues to use, and what resources to request. It does not send work to a cluster from elsewhere; choosing `crick` on your laptop will not run anything on NEMO. If your cluster does not have a profile yet, see [adding a profile](../contributing/expanding.md#add-a-profile).

On a cluster, the `nextflow run` command itself becomes the *head job*: a small process that submits each piece of work to the scheduler as a separate job, waits for them, and collects the results. It has to keep running for the whole run. Before you start:

- **The paths in your CSV must be the cluster's paths.** If you are working from a mounted drive, use the path on the cluster, not the mounted one.
- **Run the head job somewhere it will not be killed.** Most clusters stop long-running processes on login nodes, so run it in an interactive session, inside `tmux` or `screen`, or as a batch job of its own.
- **Put the cache somewhere with space.** `--root_dir` defaults to your home directory, which is usually the smallest volume you have. See [choosing a cache location](../front_ends/napari_plugin/inference.md#basecache-directory).

??? tip "Tuning how the work is split"

    Two parameters control how your images are divided into parallel jobs: `memory_per_job` in the profile (how much a single job can hold) and `substack_scale` (scales substacks up or down for stronger or weaker hardware). The [tuning section](../nextflow/index.md#tuning-the-pipeline) covers both, and running locally you may want to raise `memory_per_job` from its conservative default to match your actual RAM.

## Something went wrong?

??? failure "`Missing required parameter: --img_dir`"

    `--img_dir` is the only parameter with no default, so this is the one you can forget. `img_dir does not exist: <path>` means the path is wrong, or you are not running from your working folder.

??? failure "`Model <x> not yet implemented!`"

    The name you passed to `--model` has no script in the pipeline. The message lists every model that does. Note this is the *family* name (`empanada`), not the version (`mitonet_v1`).

??? failure "`Version '<x>' not found in manifest`"

    `--model_type` does not match that family. The error lists the valid versions with their short names, which is what you need to give.

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
