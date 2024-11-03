import gc
import math
import shutil
import tempfile
import pillow_avif
from pathlib import Path
from PIL import Image as pil
pil.Image.MAX_IMAGE_PIXELS = 933120000
from core.config.img_conf import get_config
from core.slicer.infra.detectors import select_detector
from core.download.domain.dowload_entity import Chapter
from core.slicer.infra.utils.constants import WIDTH_ENFORCEMENT
from core.slicer.infra.services import ImageHandler, ImageManipulator
from core.__seedwork.infra.utils.sanitize_folder import sanitize_folder_name

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
        files = []
        continue_index = -1
        img_iteration = 1
        while continue_index < len(ch.files) - 1:
            group_height = 0
            img_objs = []
            for i in range(continue_index + 1, len(ch.files)):
                img = pil.open(ch.files[i])
                img_objs.append(img)
                width, height = img.size
                group_height += height
                if group_height >= 5 * conf.split_height or i == len(ch.files) - 1:
                    if continue_index < len(ch.files) - 1:
                        continue_index = i
                    if i == len(ch.files):
                        continue_index = len(ch.files) - 1
                    break

            imgs = img_manipulator.resize(
                img_objs, width_enforce_mode, conf.custom_width
            )
            combined_img = img_manipulator.combine(imgs)
            slice_points = detector.run(
                combined_img,
                conf.split_height,
                sensitivity=conf.detection_sensitivity,
                ignorable_pixels=conf.ignorable_pixels,
                scan_step=conf.scan_line_step,
            )
            imgs = img_manipulator.slice(combined_img, slice_points)
            for img in imgs:
                filename=img_handler.save(
                    str(Path.joinpath(Path(tempfile.gettempdir()), 'pyneko', Path(ch.files[0]).parent.parent.name, f'{sanitize_folder_name(ch.number)} [stitched]')),
                    img,
                    img_iteration,
                    img_format=conf.img,
                    quality=100,
                )
                files.append(str(Path.joinpath(Path(tempfile.gettempdir()), 'pyneko', Path(ch.files[0]).parent.parent.name, f'{sanitize_folder_name(ch.number)} [stitched]', filename)))
                img_iteration += 1

            if fn != None:
                fn(math.ceil(continue_index * 80)/len(ch.files))

        imgs = img_handler.load(files)
        combined_img = img_manipulator.combine(imgs)
        slice_points = detector.run(
            combined_img,
            conf.split_height,
            sensitivity=conf.detection_sensitivity,
            ignorable_pixels=conf.ignorable_pixels,
            scan_step=conf.scan_line_step,
        )
        files = []
        img_iteration = 1
        imgs = img_manipulator.slice(combined_img, slice_points)
        path = str(Path.joinpath(Path(ch.files[0]).parent.parent, f'{sanitize_folder_name(ch.number)} [stitched]'))
        if conf.slice_replace_original_files:
            path = str(Path.joinpath(Path(ch.files[0]).parent.parent, f'{sanitize_folder_name(ch.number)}'))
            shutil.rmtree(path)
        for i, img in enumerate(imgs):
            filename=img_handler.save(
                path,
                img,
                img_iteration,
                img_format=conf.img,
                quality=100,
            )
            if fn != None:
                fn(80 + (math.ceil(i * 50)/len(ch.files)))
            files.append(str(Path.joinpath(Path(path), filename)))
            img_iteration += 1
        
        shutil.rmtree(Path.joinpath(Path(tempfile.gettempdir()), 'pyneko', Path(ch.files[0]).parent.parent.name, f'{sanitize_folder_name(ch.number)} [stitched]'))

        gc.collect()

        if fn != None:
            fn(math.ceil(len(ch.files) * 100)/len(ch.files))
        
        return Chapter(ch.number, files)