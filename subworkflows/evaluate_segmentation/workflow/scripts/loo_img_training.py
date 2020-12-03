"""
Adapted from: https://raw.githubusercontent.com/ilastik/ilastik/1.3.3-legacy/bin/train_headless.py
Note: This script does not make any attempt to be efficient with RAM usage.
      (The entire label volume is loaded at once.)  As a result, each image volume you
      train with must be significantly smaller than the available RAM on your machine.
"""
from __future__ import print_function
from builtins import range
import numpy as np

import shutil

def main():
    # Cmd-line args to this script.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("name_loo_img")
    parser.add_argument("output_project_name")
    parsed_args = parser.parse_args()

    input_project = parsed_args.project_name
    name_loo_img = parsed_args.name_loo_img
    output_project = parsed_args.output_project_name
    shutil.copy(input_project, output_project)

    generate_trained_loo_project_file(
        output_project,
        name_loo_img
    )
    print("DONE.")



def generate_trained_loo_project_file(
    project_path,
    name_loo_img
):
    """
    Create a new project file from scratch, add the given raw data files,
    inject the corresponding labels, configure the given feature selections,
    and (if provided) override the classifier type ('factory').

    Finally, request the classifier object from the pipeline (which forces training),
    and save the project.

    new_project_path: Where to save the new project file
    raw_data_paths: A list of paths to the raw data images to train with
    label_data_paths: A list of paths to the label image data to train with
    feature_selections: A matrix of bool, representing the selected features
    classifier_factory: Override the classifier type.  Must be a subclass of either:
                        - lazyflow.classifiers.LazyflowVectorwiseClassifierFactoryABC
                        - lazyflow.classifiers.LazyflowPixelwiseClassifierFactoryABC
    """
    import ilastik_main
    from ilastik.workflows.pixelClassification import PixelClassificationWorkflow
    from lazyflow.roi import fullSlicing

    ##
    ## CREATE PROJECT
    ##

    # Manually configure the arguments to ilastik, as if they were parsed from the command line.
    # (Start with empty args and fill in below.)
    ilastik_args = ilastik_main.parse_args([])
    ilastik_args.project = project_path
    ilastik_args.headless = True
    ilastik_args.readonly = False

    shell = ilastik_main.main(ilastik_args)
    assert isinstance(shell.workflow, PixelClassificationWorkflow)

    ##
    ## CONFIGURE FILE PATHS
    ##

    data_selection_applet = shell.workflow.dataSelectionApplet

    opDataSelection = data_selection_applet.topLevelOperator

    existing_lanes = len(opDataSelection.DatasetGroup)
    # Not sure if assuming role_index = 0 is allways valid
    role_index = 0

    cur_lane = None
    for lane, dataset in enumerate(opDataSelection.DatasetGroup):
        dat = dataset[role_index][0].wait()[0]
        if dat.nickname == name_loo_img:
            cur_lane = lane
            break

    if cur_lane is None:
        raise ValueError(f'{name_loo_img} not found in project.')

    # Set delete the label fro this image by setting all labels to 0
    opPixelClassification = shell.workflow.pcApplet.topLevelOperator
    #label_input_slot = opPixelClassification.LabelInputs[cur_lane]
    #label_output_slot = opPixelClassification.LabelImages[cur_lane]
    #shape = label_output_slot.meta.shape
    #zero_labels = np.zeros(shape=shape, dtype=np.uint8)
    #label_input_slot[fullSlicing(shape)] = zero_labels
    #label_input_slot.setDirty()
    #label_output_slot.disconnect()
    #label_output_slot.setValue(zero_labels)
    #label_output_slot.setDirty()
    ##
    ## TRAIN CLASSIFIER
    ##

    # Make sure the caches in the pipeline are not 'frozen'.
    # (This is the equivalent of 'live update' mode in the GUI.)
    opPixelClassification.FreezePredictions.setValue(False)

    # Mark the classifier as dirty to force re-training it
    cur_labs = opPixelClassification.opTrain.Labels[cur_lane]
    up_lab=cur_labs.upstream_slot.upstream_slot.upstream_slot
    zero_labels = np.zeros(shape=up_lab.meta.shape, dtype=np.uint8)
    up_lab.setValue(zero_labels)
    up_lab.setDirty()
    #cur_labs.disconnect()
    #cur_labs.value[:] = 0
    #opPixelClassification.opTrain.ClassifierFactory.setDirty()
    # Request the classifier object from the pipeline.
    # This forces the pipeline to produce (train) the classifier.
    _ = opPixelClassification.Classifier.value

    ##
    ## SAVE PROJECT
    ##

    # save project file (includes the new classifier).
    shell.projectManager.saveProject(force_all_save=True)


if __name__ == "__main__":
    main()
