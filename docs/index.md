# AI OnDemand (AIoD)

## Overview
AI OnDemand (AIoD) is a framework developed by the [Software Engineering & AI STP](https://www.crick.ac.uk/research/platforms-and-facilities/software-engineering-and-artificial-intelligence) at the [Francis Crick Institute](https://www.crick.ac.uk/) that enables running any model on any compute environment without requiring user knowledge on how to install and run these models, let alone run them at scale on HPC/cloud compute (via [Nextflow](https://www.nextflow.io/docs/latest/index.html)).

It is designed to allow the use of arbitrary user interfaces (currently with a fully-fledged [Napari plugin](sections/front_ends/napari_plugin.md)) to simplify usage and immediately visualise results while separating compute from visualiation.


<!-- Image -->


This documentation covers how to setup and use the framework, with separate information for the main different user groups of AIoD:

- Wet lab scientists
- ML practioners/experts
- HPC facility staff

!!! note

    Users within the Francis Crick Institute have automatic access to AIoD, and have no setup. If users outside of the Crick want to use AIoD on their HPC and are not HPC admins/specialists, please forward [this page]() to your HPC admins. Alternatively, see our [AIoD over SSH]() to use AIoD on your HPC without the need for OnDemand/virtual desktop. 

## Contribution

AIoD is developed as an extendable platform, allowing users to easily add preprocessing functions and new models, that can become available to all or restricted users as desired.

If you want to use a model that is not currently available, see [how to add a model]() or get in [contact](). 

## Repositories

<!-- <table>
 <tr>
  <td>Napari Plugin</td><td><img alt="Napari Plugin" src="https://img.shields.io/maven-central/v/com.google.accompanist/accompanist-permissions?versionPrefix=0.20"></td>
 </tr>
</table> -->