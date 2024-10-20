import gc
import math
from pathlib import Path
from core.config.img_conf import get_config
from core.slicer.infra.detectors import select_detector
from core.download.domain.dowload_entity import Chapter
from core.slicer.infra.utils.constants import WIDTH_ENFORCEMENT
from core.slicer.infra.services import ImageHandler, ImageManipulator

class SmartStitch():
    def run(self, ch: Chapter, fn = None) -> Chapter:
        conf = get_config()
        img_handler = ImageHandler()
        img_manipulator = ImageManipulator()
        detector = select_detector(detection_type=conf.detection_type)
        if conf.custom_width > 0 and not conf.automatic_width:
            width_enforce_mode = WIDTH_ENFORCEMENT.MANUAL
        elif conf.automatic_width:
            width_enforce_mode = WIDTH_ENFORCEMENT.AUTOMATIC
        else:
            width_enforce_mode = WIDTH_ENFORCEMENT.NONE
        imgs = img_handler.load(ch.files)
        imgs = img_manipulator.resize(
            imgs, width_enforce_mode, conf.custom_width
        )
        combined_img = img_manipulator.combine(imgs)
        slice_points = detector.run(
            combined_img,
            conf.split_height,
            sensitivity=conf.detection_senstivity,
            ignorable_pixels=conf.ignorable_pixels,
            scan_step=conf.scan_line_step,
        )
        imgs = img_manipulator.slice(combined_img, slice_points)
        files = []
        img_iteration = 1
        for i, img in enumerate(imgs):
            filename=img_handler.save(
                str(Path.joinpath(Path(ch.files[0]).parent.parent, f'{ch.number} [stitched]')),
                img,
                img_iteration,
                img_format=conf.img,
                quality=100,
            )
            files.append(str(Path.joinpath(Path(ch.files[0]).parent.parent, f'{ch.number} [stitched]', filename)))
            img_iteration += 1

            if fn != None:
                fn(math.ceil(i * 100)/len(imgs))

        gc.collect()
        if fn != None:
            fn(math.ceil(len(imgs) * 100)/len(imgs))
        
        return Chapter(ch.number, files)