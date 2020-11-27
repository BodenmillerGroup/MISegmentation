# WIP analysis workflow: MISegmentation

[![Snakemake](https://img.shields.io/badge/snakemake-≥5.7.0-brightgreen.svg)](https://snakemake.bitbucket.io)
[![Build Status](https://travis-ci.org/snakemake-workflows/misegmentation.svg?branch=master)](https://travis-ci.org/snakemake-workflows/misegmentation)

This is a workflow that should compare segmentation performance of single cell segmentation masks generated via the `ImcSegmentationPipeline` (https://github.com/BodenmillerGroup/ImcSegmentationPipeline).

## Authors

* Vito RT Zanotelli (@votti)

## Issues:
- Files were re-named for final export, so I am lacking the mapping
    of raw data -> published masks

## Datasets

This repository will host the segmentation performance comparison for 5 published dataset that were processed with the `ImcSegmentationPipeline`. Each analysis
will be separate branch in this repository, with the 'main' branch orchestrating everything.

- 'Schulz2017': "Simultaneous Multiplexed Imaging of mRNA and Proteins with Subcellular Resolution in Breast Cancer Tissue Samples by Mass Cytometry", DOI: 10.1016/j.cels.2017.12.001
- 'Damond2018': "A Map of Human Type 1 Diabetes Progression by Imaging Mass Cytometry", DOI: 10.1016/j.cmet.2018.11.014
- 'Ali2020': "The single-cell pathology landscape of breast cancer", DOI: 10.1038/s41586-019-1876-x
- 'Jackson2020': "The single-cell pathology landscape of breast cancer", DOI: 10.1038/s41586-019-1876-x
- 'HubMAP2020': "The Human Body at Cellular Resolution: the NIH Human BioMolecular Atlas Program" DOI: 10.1038/s41586-019-1629-x
