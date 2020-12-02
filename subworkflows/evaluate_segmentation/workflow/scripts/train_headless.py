"""
Adapted from: https://raw.githubusercontent.com/ilastik/ilastik/1.3.3-legacy/bin/train_headless.py
Note: This script does not make any attempt to be efficient with RAM usage.
      (The entire label volume is loaded at once.)  As a result, each image volume you
      train with must be significantly smaller than the available RAM on your machine.
"""
from __future__ import print_function
from builtins import range
import os
import pandas as pd
import pathlib

def main():
    # Cmd-line args to this script.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("new_project_name")
    parser.add_argument("fol_img_data")
    parser.add_argument("fol_label_data")
    parser.add_argument("fn_file_meta")
    parser.add_argument("fn_feature_matrix")
    parsed_args = parser.parse_args()

    # Optional: Customize classifier settings
    classifier_factory = None
    # from lazyflow.classifiers import ParallelVigraRfLazyflowClassifierFactory
    # classifier_factory = ParallelVigraRfLazyflowClassifierFactory(100)

    # sklearn classifier:
    # from lazyflow.classifiers import SklearnLazyflowClassifier
    # classifier_factory = SklearnLazyflowClassifierFactory( AdaBoostClassifier, n_estimators=50 )

    feature_matrix = pd.read_csv(parsed_args.fn_feature_matrix,
                                 index_col=0)
    print(feature_matrix)

    fol_label_data = pathlib.Path(parsed_args.fol_label_data)
    fol_img_data = pathlib.Path(parsed_args.fol_img_data)
    dat_meta = pd.read_csv(parsed_args.fn_file_meta).query("use==1")
    dat_meta['fn_labels'] = dat_meta['filename']
    dat_meta['fn_img'] = dat_meta.apply(lambda r: '{basename}_x{x}_y{y}_w{w}_h{h}.h5'.format(**dict(r)),
                                        axis=1
                                        )

    # check if all input files are there:
    fns_img = [fol_img_data / f for f in dat_meta.fn_img.values]
    fns_labels = [fol_label_data / f for f in dat_meta.fn_labels.values]
    missing = []
    for f in fns_img:
        if not f.exists():
            missing.append(f)
    assert len(missing) == 0, f'Following input imgs are missing: {missing}'

    for f in fns_labels:
        if not f.exists():
            missing.append(f)
    assert len(missing) == 0, f'Following input labels are missing: {missing}'

    generate_trained_project_file(
        parsed_args.new_project_name,
        [str(f) for f in fns_img],
        [str(f) for f in fns_labels],
        feature_matrix,
        classifier_factory,
    )
    print("DONE.")


# Don't touch these constants!
ScalesList = [0.3, 0.7, 1, 1.6, 3.5, 5.0, 10.0]
FeatureIds = [
    "GaussianSmoothing",
    "LaplacianOfGaussian",
    "GaussianGradientMagnitude",
    "DifferenceOfGaussians",
    "StructureTensorEigenvalues",
    "HessianOfGaussianEigenvalues",
]

def generate_trained_project_file(
    new_project_path, raw_data_paths, label_data_paths, feature_selections, classifier_factory=None
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
    assert len(raw_data_paths) == len(label_data_paths), "Number of label images must match number of raw images."

    import ilastik_main
    from ilastik.workflows.pixelClassification import PixelClassificationWorkflow
    from lazyflow.graph import Graph
    from lazyflow.operators.ioOperators import OpInputDataReader
    from lazyflow.roi import roiToSlice, roiFromShape
    from ilastik.applets.dataSelection.opDataSelection import FilesystemDatasetInfo

    ##
    ## CREATE PROJECT
    ##

    # Manually configure the arguments to ilastik, as if they were parsed from the command line.
    # (Start with empty args and fill in below.)
    ilastik_args = ilastik_main.parse_args([])
    ilastik_args.new_project = new_project_path
    ilastik_args.headless = True
    ilastik_args.workflow = "Pixel Classification"

    shell = ilastik_main.main(ilastik_args)
    assert isinstance(shell.workflow, PixelClassificationWorkflow)

    ##
    ## CONFIGURE FILE PATHS
    ##

    data_selection_applet = shell.workflow.dataSelectionApplet
    input_infos = [FilesystemDatasetInfo(filePath=path) for path
                   in raw_data_paths]

    opDataSelection = data_selection_applet.topLevelOperator

    existing_lanes = len(opDataSelection.DatasetGroup)
    opDataSelection.DatasetGroup.resize(max(len(input_infos), existing_lanes))
    # Not sure if assuming role_index = 0 is allways valid
    role_index = 0
    for lane_index, info in enumerate(input_infos):
        if info:
            opDataSelection.DatasetGroup[lane_index][role_index].setValue(info)

    ##
    ## APPLY FEATURE MATRIX (from matrix above)
    ##

    opFeatures = shell.workflow.featureSelectionApplet.topLevelOperator
    opFeatures.Scales.setValue([float(s) for s in feature_selections.columns])
    opFeatures.FeatureIds.setValue(list(feature_selections.index))
    opFeatures.SelectionMatrix.setValue(feature_selections.values)

    ##
    ## CUSTOMIZE CLASSIFIER TYPE
    ##

    opPixelClassification = shell.workflow.pcApplet.topLevelOperator
    if classifier_factory is not None:
        opPixelClassification.ClassifierFactory.setValue(classifier_factory)

    ##
    ## READ/APPLY LABEL VOLUMES
    ##

    # Read each label volume and inject the label data into the appropriate training slot
    cwd = os.getcwd()
    max_label_class = 0
    for lane, label_data_path in enumerate(label_data_paths):
        graph = Graph()
        opReader = OpInputDataReader(graph=graph)
        try:
            opReader.WorkingDirectory.setValue(cwd)
            opReader.FilePath.setValue(label_data_path)

            print("Reading label volume: {}".format(label_data_path))
            label_volume = opReader.Output[:].wait()
        finally:
            opReader.cleanUp()

        raw_shape = opPixelClassification.InputImages[lane].meta.shape
        if label_volume.ndim != len(raw_shape):
            # Append a singleton channel axis
            assert label_volume.ndim == len(raw_shape) - 1
            label_volume = label_volume[..., None]

        # Auto-calculate the max label value
        max_label_class = max(max_label_class, label_volume.max())

        print("Applying label volume to lane #{}".format(lane))
        entire_volume_slicing = roiToSlice(*roiFromShape(label_volume.shape))
        opPixelClassification.LabelInputs[lane][entire_volume_slicing] = label_volume

    assert max_label_class > 1, "Not enough label classes were found in your label data."
    label_names = list(map(str, list(range(max_label_class))))
    opPixelClassification.LabelNames.setValue(label_names)

    ##
    ## TRAIN CLASSIFIER
    ##

    # Make sure the caches in the pipeline are not 'frozen'.
    # (This is the equivalent of 'live update' mode in the GUI.)
    opPixelClassification.FreezePredictions.setValue(False)

    # Request the classifier object from the pipeline.
    # This forces the pipeline to produce (train) the classifier.
    _ = opPixelClassification.Classifier.value

    ##
    ## SAVE PROJECT
    ##

    # save project file (includes the new classifier).
    shell.projectManager.saveProject(force_all_save=False)


if __name__ == "__main__":
    main()
