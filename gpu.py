from brats import AdultGliomaPreAndPostTreatmentSegmenter
from brats.constants import AdultGliomaPreAndPostTreatmentAlgorithms

segmenter = AdultGliomaPreAndPostTreatmentSegmenter(
    algorithm=AdultGliomaPreAndPostTreatmentAlgorithms.BraTS25_1,
    cuda_devices="0"
)

segmenter.infer_single(
    t1c="data/t1c.nii.gz",
    t1n="data/t1n.nii.gz",
    t2f="data/t2f.nii.gz",
    t2w="data/t2w.nii.gz",
    output_file="data/segmentation.nii.gz",
)

print("BraTS initialized successfully!")