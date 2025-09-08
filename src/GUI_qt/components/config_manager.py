import os
import json
from PyQt6.QtCore import QLocale
from PyQt6.QtWidgets import QFileDialog
from GUI_qt.utils.config import get_config, update_lang, update_external_path, update_external
from core.config.img_conf import (
    get_config as get_img_config,
    update_img, update_save, update_automatic_width, update_custom_width,
    update_detection_type, update_group,
    update_group_format,
    update_slice, update_slice_replace_original_files,
    update_group_replace_original_files
)
from GUI_qt.utils.load_providers import base_path


class ConfigManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.initial_data = True
        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')

    def initialize_config(self):
        """Inicializa a configuração da interface"""
        self.lang_changed()
        self.img_format_changed()
        self.set_folder()
        self.set_external_path_folder()

        data = get_img_config()
        self.parent_window.group_imgs.setChecked(data.group)
        self.parent_window.slicer_box.setChecked(data.slice)
        self.parent_window.replaceslicecheckBox.setChecked(
            data.slice_replace_original_files)
        self.parent_window.replacegroupcheckBox.setChecked(
            data.group_replace_original_files)
        self.parent_window.group_imgs_combo.setCurrentText(data.group_format)
        self.parent_window.slicer_height.setValue(data.split_height)
        self.parent_window.slicer_width_spin.setValue(data.custom_width)
        self.parent_window.slicer_detection_sensivity.setValue(
            data.detection_sensitivity)
        self.parent_window.slicer_scan_line.setValue(data.scan_line_step)
        self.parent_window.slicer_ignorable_margin.setValue(
            data.ignorable_pixels)

        if data.automatic_width:
            self.parent_window.slicer_width_select.setCurrentIndex(1)
        else:
            if data.custom_width == 0:
                self.parent_window.slicer_width_select.setCurrentIndex(0)
            else:
                self.parent_window.slicer_width_select.setCurrentIndex(2)

        if data.detection_type == 'pixel':
            self.parent_window.slicer_detector_select.setCurrentIndex(0)
        else:
            self.parent_window.slicer_detector_select.setCurrentIndex(1)
            self._hide_detection_controls()

        width_select_index = self.parent_window.slicer_width_select.currentIndex()
        if width_select_index < 2:
            self._hide_width_controls()

        conf = get_config()
        if conf.external_provider:
            self.parent_window.external.setChecked(conf.external_provider)

        self.initial_data = False

    def set_folder(self):
        data = get_img_config()
        if not self.initial_data:
            folder_path = QFileDialog.getExistingDirectory(
                self.parent_window, "Select Folder", data.save)
            if folder_path:
                update_save(folder_path)
                self.parent_window.path.setText(folder_path)
        else:
            self.parent_window.path.setText(data.save)

    def set_external_path_folder(self):
        data = get_config()
        if not self.initial_data:
            folder_path = QFileDialog.getExistingDirectory(
                self.parent_window, "Select Folder", data.external_provider_path)
            if folder_path:
                update_external_path(folder_path)
                self.parent_window.selected_external.setText(folder_path)
        else:
            if data.external_provider_path:
                self.parent_window.selected_external.setText(
                    data.external_provider_path)

    def external_provider_changed(self, checked):
        if not self.initial_data:
            data = get_config()
            if not data.external_provider_path:
                folder_path = QFileDialog.getExistingDirectory(
                    self.parent_window, "Select Folder", data.external_provider_path)
                if folder_path:
                    update_external_path(folder_path)
                    self.parent_window.selected_external.setText(folder_path)
                    update_external(checked)
            else:
                update_external(checked)

    def lang_changed(self, lang=None):
        translations = {}
        with open(os.path.join(self.assets, 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)

        language = lang
        if not lang:
            config = get_config()
            if not config:
                language = QLocale.system().name()
                update_lang(language)
            else:
                language = config.lang
            if language not in translations:
                language = 'en'
            self.parent_window.langs.setCurrentText(language)
        else:
            update_lang(language)

        translation = translations[language]
        self._update_translations(translation)

    def img_format_changed(self, img=None):
        if not img:
            data = get_img_config()
            self.parent_window.format_img.setCurrentText(data.img)
        else:
            update_img(img)

    def group_imgs_combo_changed(self, img=None):
        if img:
            update_group_format(img)

    def group_detection_type_changed(self, model=None):
        if not self.initial_data and model:
            detection_type_index = self.parent_window.slicer_detector_select.currentIndex()
            if detection_type_index == 0:
                update_detection_type('pixel')
                self._show_detection_controls()
            else:
                update_detection_type(None)
                self._hide_detection_controls()

    def group_slicer_width_combo_changed(self, model=None):
        if not self.initial_data and model:
            width_select_index = self.parent_window.slicer_width_select.currentIndex()
            if width_select_index < 2:
                update_custom_width(0)
                if width_select_index == 1:
                    update_automatic_width(True)
                else:
                    update_automatic_width(False)
                self._hide_width_controls()
            else:
                update_automatic_width(False)
                self._show_width_controls()

    def toggle_group_img(self, checked):
        if not self.initial_data:
            update_group(checked)

    def toggle_group_slice(self, checked):
        if not self.initial_data:
            update_slice(checked)

    def toggle_group_replace(self, checked):
        if not self.initial_data:
            update_group_replace_original_files(checked)

    def toggle_slice_replace(self, checked):
        if not self.initial_data:
            update_slice_replace_original_files(checked)

    def _update_translations(self, translation):
        self.parent_window.websites.setText(translation['websites'])
        self.parent_window.link.setText(translation['paste'])
        self.parent_window.downloadAll.setText(translation['download_all'])
        self.parent_window.invert.setText(translation['invert'])
        self.parent_window.search.setPlaceholderText(
            translation['search_caps'])
        self.parent_window.progress.setText(translation['progress'])
        self.parent_window.label.setText(translation['loading'])
        self.parent_window.config.setText(translation['config'])
        self.parent_window.config_back.setText(translation['back'])
        self.parent_window.language_label.setText(translation['language'])
        self.parent_window.img_format.setText(translation['format'])
        self.parent_window.open_folder.setText(translation['open_folder'])
        self.parent_window.open_external_folder.setText(
            translation['open_folder'])
        self.parent_window.path_label.setText(translation['path_label'])
        self.parent_window.simul_label.setText(translation['download_qtd'])
        self.parent_window.dev_label.setText(translation['dev_label'])
        self.parent_window.dev_check.setText(translation['dev_check'])
        self.parent_window.group_imgs.setTitle(translation['group_images'])
        self.parent_window.slicer_box.setTitle(translation['slicer'])
        self.parent_window.slicer_height_label.setText(
            translation['height_output'])
        self.parent_window.slicer_width_label.setText(
            translation['width_enforcement_type'])
        self.parent_window.slicer_width_spin_label.setText(
            translation['width_custom'])
        self.parent_window.slicer_detector_label.setText(
            translation['detector_type'])

        self.parent_window.slicer_width_select.clear()
        self.parent_window.slicer_width_select.addItems([
            translation['no_enforcement'],
            translation['automatic_uniform_width'],
            translation['user_customized_width']
        ])
        self.parent_window.slicer_detector_select.clear()
        self.parent_window.slicer_detector_select.addItems([
            translation['smart_pixel'],
            translation['direct_slicing'],
        ])

        self.parent_window.slicer_detection_sensivity_label.setText(
            translation['detection_sensitivity'])
        self.parent_window.slicer_scan_line_label.setText(
            translation['scan_line_step'])
        self.parent_window.slicer_ignorable_margin_label.setText(
            translation['ignore_horizontal_margins'])
        self.parent_window.replaceslicecheckBox.setText(
            translation['overwrite'])
        self.parent_window.replacegroupcheckBox.setText(
            translation['overwrite'])
        self.parent_window.external.setTitle(translation['external'])

    def _hide_detection_controls(self):
        self.parent_window.slicer_detection_sensivity_label.hide()
        self.parent_window.slicer_detection_sensivity.hide()
        self.parent_window.slicer_scan_line_label.hide()
        self.parent_window.slicer_scan_line.hide()
        self.parent_window.slicer_ignorable_margin_label.hide()
        self.parent_window.slicer_ignorable_margin.hide()

    def _show_detection_controls(self):
        self.parent_window.slicer_detection_sensivity_label.show()
        self.parent_window.slicer_detection_sensivity.show()
        self.parent_window.slicer_scan_line_label.show()
        self.parent_window.slicer_scan_line.show()
        self.parent_window.slicer_ignorable_margin_label.show()
        self.parent_window.slicer_ignorable_margin.show()

    def _hide_width_controls(self):
        self.parent_window.slicer_width_spin_label.hide()
        self.parent_window.slicer_width_spin.hide()

    def _show_width_controls(self):
        self.parent_window.slicer_width_spin_label.show()
        self.parent_window.slicer_width_spin.show()
