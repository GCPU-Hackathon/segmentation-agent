from brats import AdultGliomaPreAndPostTreatmentSegmenter
from brats.constants import AdultGliomaPreAndPostTreatmentAlgorithms

# segmenter = AdultGliomaPreTreatmentSegmenter(
#     algorithm=AdultGliomaPreTreatmentAlgorithms.BraTS23_1,
#     cuda_devices="0"
# )

segmenter = AdultGliomaPreAndPostTreatmentSegmenter(algorithm=AdultGliomaPreAndPostTreatmentAlgorithms.BraTS25_1)
# these parameters are optional, by default the latest winning algorithm will be used on cuda:0
segmenter.infer_single(
    t1c="data/t1c.nii.gz",
    t1n="data/t1n.nii.gz",
    t2f="data/t2f.nii.gz",
    t2w="data/t2w.nii.gz",
    output_file="segmentation.nii.gz",
)

print("BraTS initialized successfully!")

# To run segmentation (need actual files):
# segmenter.infer_single(
#     t1c="data/t1c.nii.gz",
#     t1n="data/t1n.nii.gz",
#     t2f="data/t2f.nii.gz",
#     t2w="data/t2w.nii.gz",
#     output_file="output/segmentation.nii.gz",
# )