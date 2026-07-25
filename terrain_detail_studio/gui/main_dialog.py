# -*- coding: utf-8 -*-
"""
Main Processing Dialog for Single Tile DTM Run
"""
import os
import sys

try:
    from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox
    from qgis.PyQt.QtCore import Qt
except ImportError:
    # Standalone PyQt fallback for non-QGIS test envs
    QDialog = object

class MainDialog:
    """Single DTM Processing Dialog Class."""

    def __init__(self, parent=None):
        self.parent = parent
        self.input_file = ""
        self.output_dir = ""
        self.selected_preset = "balanced-detail"

    def run_preflight(self, filepath: str) -> dict:
        from ..core.dem_inspector import DEMInspector
        return DEMInspector.inspect(filepath)

    def execute_job(self, input_path: str, output_dir: str, preset_code: str):
        from ..core.dem_inspector import DEMInspector
        from ..core.processing_plan import ProcessingPlan
        from ..core.mdhs_engine import MDHSEngine
        from ..core.slope_engine import SlopeEngine
        from ..core.lrm_engine import LRMEngine
        from ..core.output_manager import OutputManager
        from ..core.layer_builder import LayerBuilder
        from ..presets.preset_manager import PresetManager

        dem_info = DEMInspector.inspect(input_path)
        pm = PresetManager()
        preset = pm.get_preset(preset_code)
        plan = ProcessingPlan.resolve_plan(dem_info, preset)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        mdhs_out = os.path.join(output_dir, f"{base_name}_mdhs.tif")
        slope_out = os.path.join(output_dir, f"{base_name}_slope.tif")
        lrm_out = os.path.join(output_dir, f"{base_name}_lrm.tif")

        # Execute engines
        MDHSEngine.process(input_path, mdhs_out, altitude_deg=plan['mdhs_params']['altitude_deg'])
        SlopeEngine.process(input_path, slope_out)
        LRMEngine.process_tile(input_path, lrm_out, radius_m=plan['lrm_params']['radius_m'])

        # Validate and write manifest
        v1 = OutputManager.validate_raster_output(mdhs_out)
        v2 = OutputManager.validate_raster_output(slope_out)
        v3 = OutputManager.validate_raster_output(lrm_out)

        if v1 and v2 and v3:
            manifest_path = OutputManager.write_manifest(
                output_dir,
                base_name,
                plan,
                {'mdhs': mdhs_out, 'slope': slope_out, 'lrm': lrm_out}
            )
            # Add to QGIS project
            LayerBuilder.add_styled_group_to_qgis(base_name, mdhs_out, slope_out, lrm_out, plan['style_params'])
            return {'success': True, 'manifest': manifest_path, 'files': [mdhs_out, slope_out, lrm_out]}
        else:
            return {'success': False, 'error': 'Raster output validation failed'}
