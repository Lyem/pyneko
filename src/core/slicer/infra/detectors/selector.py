from core.slicer.infra.utils.constants import DETECTION_TYPE
from .direct_slicing import DirectSlicingDetector
from .pixel_comparison import PixelComparisonDetector

def select_detector(detection_type: str | DETECTION_TYPE):
    if detection_type == None or detection_type == DETECTION_TYPE.NO_DETECTION.value:
        return DirectSlicingDetector()
    elif (
        detection_type == "pixel"
        or detection_type == DETECTION_TYPE.PIXEL_COMPARISON.value
    ):
        return PixelComparisonDetector()
    else:
        raise Exception("Invalid Detection Type")