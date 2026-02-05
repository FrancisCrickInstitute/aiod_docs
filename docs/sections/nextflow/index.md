# Nextflow Pipeline (`Segment-Flow`)

Our [Nextflow pipeline](https://github.com/FrancisCrickInstitute/Segment-Flow) is where the actual code and processes for running models, and orchestrating the parallelization happens.

## Running the Pipeline Directly
The Nextflow pipeline can be run directly, allowing headless use and avoiding Napari or any other front-end. Although more work is required in specifying the input parameters, 


An example run script may look like:

```
??
```

Where the `??` params file looks like:

```yaml
??
```

### Creating the Input CSV
The input CSV file provides a definitive source of truth for the dimensions of the input data, which can be useful in the cases of missing, incorrect or misunderstood metadata.

You can use `aiod_utils.??` to more easily create this CSV, though it requires providing a `dict` specifying the size of each dimension. Missing dimensions will be guessed, so it is important to review the generated CSV afterwards.

The CSV should look like:
```csv
img_path,num_slices,height,width,channels
<path>,5,1000,1000,3
...
```

!!! warning "Filepaths"

    The filepaths in this CSV are the paths for wherever the computation is actually taking place, so the paths need to make sense for the remote destination rather than where you may be currently working. So when working locally and sending the command to the HPC, the filepath(s) must be those on the HPC itself, not e.g. the mounted path. For more information, see our section on [executing over SSH](../front_ends/napari_plugin.md#execution-over-ssh).


## Tuning the Pipeline

### Pipeline-/Institutional-Level
The [dynamic resource requests functionality of Nextflow](https://www.nextflow.io/docs/latest/process.html#dynamic-task-resources) allows us to be efficient in our requests on HPC, such that we are not requesting far more memory than is needed. This works well for memory requests, but requesting the required time is often very dependent on the hardware itself, and can be hard to estimate ahead of time.

The [current "crick" Nextflow profile](https://github.com/FrancisCrickInstitute/Segment-Flow/blob/master/profiles/crick.conf) is a good starting point, but when making your own [institutional profile](CONTRIB)

### Individual-Level
Beyond tuning the processes, a user has a certain level of control over how to run the pipeline through how the [substacks](../concepts/index.md#parallelising-substacks) are created (their size and number).

