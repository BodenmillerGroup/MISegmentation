# WIP analysis workflow: MISegmentation

[![Snakemake](https://img.shields.io/badge/snakemake-≥5.7.0-brightgreen.svg)](https://snakemake.bitbucket.io)
[![Build Status](https://travis-ci.org/snakemake-workflows/misegmentation.svg?branch=master)](https://travis-ci.org/snakemake-workflows/misegmentation)

This is a workflow that should compare segmentation performance of single cell segmentation masks generated via the `ImcSegmentationPipeline` (https://github.com/BodenmillerGroup/ImcSegmentationPipeline).

## Authors

* Vito RT Zanotelli (@votti)

## Datasets

This repository will host the segmentation performance comparison for 5 published dataset that were processed with the `ImcSegmentationPipeline`.

- 'Schulz2017': "Simultaneous Multiplexed Imaging of mRNA and Proteins with Subcellular Resolution in Breast Cancer Tissue Samples by Mass Cytometry", DOI: 10.1016/j.cels.2017.12.001
    - Data in Data/SegData/Her2_TMA
        - Ilp: 20161212_Her2_TMA_2.ilp
        - Cpproj: 20170116_Her2_TMA_2_expand_and_propagate_comparison.cpproj
        - Panel: panel.csv
        - analysis_stacks: analysis
        - ometiffs: ometiff
        - random crops: available
        
        => extracted labels look good and usable
        
        -> Good to go!
    
- 'Damond2018': "A Map of Human Type 1 Diabetes Progression by Imaging Mass Cytometry", DOI: 10.1016/j.cmet.2018.11.014
    - Data in: CM2017
        - ILP: CM2017_cells_NEW.ilp
        - Cpproj: CellsAndStructures_v1.1.cpproj
        - Panel: CM_Panel.csv
        - ometiff: ometiff
        - analysis_stacks: analysis -> only full stacks
        - random crops: via file names
        
        -> Good to go!

- 'Ali2020': "The single-cell pathology landscape of breast cancer", DOI: 10.1038/s41586-019-1876-x
    - Raw data: from aspera ~/.aspera/connect/bin/ascp -TQ -l40m -P 33001 -i "./asperaweb_id_dsa.openssh" idr0076@fasp.ebi.ac.uk:. .
    - Contains masks, full stack and pannel
    - Also have .ilp - but naming entierly different.
    - Data in: metabrik
        - ILP: metabric_new_classifier_20180108.ilp
        - Cpproj: 2_segment_ilastik_v2_graded_annular_masks.cpproj
        - Panel: metabric_panel_for_analysis_stacks.csv
        - ometiff: ??
        - analysis_stacks: analysis_stacks -> full stacks only
        - random crops: via file names
        => naming is standardized but ome files still missing
        
        -> No go
    
- 'Jackson2020': "The single-cell pathology landscape of breast cancer", DOI: 10.1038/s41586-019-1876-x
    - Data in: basel_zuri
        - Ilp: 20171130_pixelclassification_BaselZuri.ilp
        - cpproj: 20180102_Basel_Zuri_segmentation.cpproj
        - Panel: ??
        - ometiffs: ome
        - analysis_stacks: analysis_stacks
        - random crops: ilastik_random, no crop coordinates in filenames
            -> Had to get some data from the archive
            -> naming with exception of 4 
            -> fixed by matching
            
        -> Good to go!
        
- 'HubMAP2020': "The Human Body at Cellular Resolution: the NIH Human BioMolecular Atlas Program" DOI: 10.1038/s41586-019-1629-x
    - Data: HuBMAP/Data/20191211_analysis_HubMAP_LN_Spleen_thymus
        - cpproj: ??
        - Panel: 20191128_HubMAP.csv
        - ometiffs: ometiffiles
        - analyis_stacks: tiffs
        - random crops: ilastik
    
        -> Good to go!
d
