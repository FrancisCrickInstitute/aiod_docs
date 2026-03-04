# AI OnDemand (AIoD)

## Overview
AI OnDemand (AIoD) is a framework developed by the [Software Engineering & AI STP](https://www.crick.ac.uk/research/platforms-and-facilities/software-engineering-and-artificial-intelligence) at the [Francis Crick Institute](https://www.crick.ac.uk/) that enables running any model on any compute environment without requiring user knowledge on how to install and run these models, let alone run them at scale on HPC/cloud compute (via [Nextflow](https://www.nextflow.io/docs/latest/index.html))!

It is designed to allow the use of arbitrary user interfaces (currently with a fully-fledged [Napari plugin](./sections/front_ends/napari_plugin/index.md)) to simplify usage and immediately visualise results while separating compute from visualisation.


Here's a simplified GIF outlining AIoD:

![AIoD Overview](./assets/aiod_overview_animated.gif)


This documentation covers how to setup and use the framework, providing information for different user groups of AIoD:

- Wet lab scientists
- ML practitioners/experts
- HPC facility staff
- Future contributors!


!!! note "Cricksters"

    **Users within the Francis Crick Institute have automatic access to AIoD with no setup required.**
    
    If users outside of the Crick want to use AIoD on their HPC and are not HPC admins/specialists, please forward [this page](./sections/getting_started/index.md) to your HPC admins. Alternatively, see our [AIoD-Napari over SSH](./sections/front_ends/napari_plugin/inference.md#execution-over-ssh) or [Nextflow directly](./sections/nextflow/index.md#running-the-pipeline-directly) sections to use AIoD on your HPC without the need for OnDemand/virtual desktop. 

## Available Models
Although AIoD is a portable, efficient, expandable framework to run any model, for users the practical functionality is determined by which models are available! 

Currently, the following models are integrated: 

<div class="model-grid">
  <a href="https://github.com/MouseLand/cellpose" class="model-card">
    <img src="assets/cellpose_logo.png" alt="Cellpose logo">
    <span>Cellpose</span>
  </a>
  <a href="https://github.com/stardist/stardist" class="model-card">
    <img src="assets/stardist_logo.jpg" alt="Stardist logo">
    <span>StarDist</span>
  </a>
  <a href="https://github.com/facebookresearch/sam2" class="model-card">
    <span>Segment Anything (1+2)</span>
  </a>
  <a href="https://github.com/stardist/stardist" class="model-card">
    <img src="assets/empanada_logo_icon.png" alt="Empanada logo">
    <span>Empanada</span>
  </a>
  <a href="https://github.com/stardist/stardist" class="model-card">
    <img src="assets/plantseg_logo.png" alt="PlantSeg logo">
    <span>PlantSeg</span>
  </a>
  <a href="https://github.com/FrancisCrickInstitute/em-segment-pytorch/" class="model-card">
    <img src="assets/etchacell_logo.jpeg" alt="Etch-a-cell logo">
    <span>Etch-a-Cell Models</span>
  </a>
</div>

...with more on the way!

## Contribution

AIoD is developed as an extendable platform, allowing users to easily add new models, preprocessing functions etc., that can become available to all or restricted users as desired. This simplifies and unifies running models on local, high-performance, or cloud compute!

If you want to use a model that is not currently available, see [how to add a model](./sections/contributing/expanding.md) or get in [contact with us](./sections/support/index.md#contact-us). 

## Repositories

<div class="grid cards" markdown>

- [:simple-github: __Segment-Flow__](https://github.com/FrancisCrickInstitute/Segment-Flow) — Nextflow pipeline that scalably, reproducibly distributes data over models
- [:simple-github: __Model Registry__](https://github.com/FrancisCrickInstitute/AIoD-Model-Registry) — Pydantic schema and model manifests for each model in AIoD
- [:simple-github: __AIoD Utils__](https://github.com/FrancisCrickInstitute/aiod_utils) — Centralized I/O, custom RLE mask encoding, preprocessing functions...anything needed across front-ends and the Nextflow pipeline!
- [:simple-github: __Napari Plugin__](https://github.com/FrancisCrickInstitute/ai-on-demand) — Our plugin for Napari to make using the pipeline easier, with [additional functionality for users](./sections/front_ends/napari_plugin/index.md)!
- [:simple-github: __AIoD Documentation__](https://github.com/FrancisCrickInstitute/aiod_docs) — This documentation!

</div>