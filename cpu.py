from brats import AfricaSegmenter
from brats.constants import AfricaAlgorithms

segmenter = AfricaSegmenter(
    algorithm=AfricaAlgorithms.BraTS24_2,  # CPU-compatible!
    cuda_devices=None
)

segmenter.infer_single(
    t1c="data/t1c.nii.gz",
    t1n="data/t1n.nii.gz",
    t2f="data/t2f.nii.gz",
    t2w="data/t2w.nii.gz",
    output_file="segmentation.nii.gz",
)
print("Africa BraTS initialized successfully!")