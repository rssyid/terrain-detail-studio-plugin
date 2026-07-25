# -*- coding: utf-8 -*-
"""
Main Processing Dialog for Terrain Detail Studio QGIS Plugin
Full PyQt GUI Dialog Window for Single DTM Processing & Preflight Validation.
"""
import os
import sys

try:
    from qgis.PyQt.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QGroupBox, QProgressBar
    )
    from qgis.PyQt.QtCore import Qt
    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False
    QDialog = object


class TerrainDetailStudioDialog(QDialog if HAS_PYQT else object):
    """QGIS PyQt Dialog Window for Terrain Detail Studio."""

    def __init__(self, iface=None, parent=None):
        if HAS_PYQT:
            super().__init__(parent or (iface.mainWindow() if iface else None))
        self.iface = iface
        self.input_file = ""
        self.output_dir = ""
        self.selected_preset_code = "balanced-detail"
        
        if HAS_PYQT:
            self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Terrain Detail Studio v1.0.0 — Cartographic Relief Generator")
        self.setMinimumWidth(620)
        self.setMinimumHeight(520)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Header Title Banner
        header = QLabel("<b>TERRAIN DETAIL STUDIO FOR QGIS</b><br><small>Local-first LiDAR DTM Cartographic Relief Package (MDHS + Slope + Gaussian LRM)</small>")
        header.setStyleSheet("background-color: #FFE600; color: #000000; padding: 10px; border: 2px solid #000000; font-size: 13px;")
        layout.addWidget(header)

        # Group 1: Input & Output Selection
        io_group = QGroupBox("1. File & Directory Selection")
        io_layout = QVBoxLayout()

        # Input DTM GeoTIFF
        in_layout = QHBoxLayout()
        in_layout.addWidget(QLabel("Input DTM GeoTIFF:"))
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Select input LiDAR bare-earth DTM (.tif)...")
        in_layout.addWidget(self.input_edit)
        btn_browse_in = QPushButton("Browse...")
        btn_browse_in.clicked.connect(self.browse_input_file)
        in_layout.addWidget(btn_browse_in)
        io_layout.addLayout(in_layout)

        # Output Directory
        out_layout = QHBoxLayout()
        out_layout.addWidget(QLabel("Output Folder:"))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Select destination folder for outputs...")
        out_layout.addWidget(self.output_edit)
        btn_browse_out = QPushButton("Browse...")
        btn_browse_out.clicked.connect(self.browse_output_dir)
        out_layout.addWidget(btn_browse_out)
        io_layout.addLayout(out_layout)

        io_group.setLayout(io_layout)
        layout.addWidget(io_group)

        # Group 2: Preset Selection
        preset_group = QGroupBox("2. Pro Cartographic Preset")
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Select Preset:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced Detail (Radius: 10m | General Terrain)", "balanced-detail")
        self.preset_combo.addItem("Linear Feature (Radius: 20m | Canals, Drains, Roads, Bunds)", "linear-feature")
        self.preset_combo.addItem("Subtle Basemap (Radius: 6m | Thematic Overlays)", "subtle-basemap")
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Group 3: Preflight Inspection Log
        log_group = QGroupBox("3. Preflight Inspection & Plan Preview")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Select an input GeoTIFF file to run automatic preflight validation...")
        self.log_text.setStyleSheet("font-family: monospace; font-size: 11px; background-color: #F8F9FA;")
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Action Buttons & Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        btn_layout.addStretch()

        self.btn_run = QPushButton("RUN LOCAL JOB ▶")
        self.btn_run.setStyleSheet("background-color: #00FF66; color: #000000; font-weight: bold; padding: 8px 20px; border: 2px solid #000000;")
        self.btn_run.clicked.connect(self.run_job)
        btn_layout.addWidget(self.btn_run)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def browse_input_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Input DTM GeoTIFF", "", "GeoTIFF Rasters (*.tif *.tiff)"
        )
        if filename:
            self.input_edit.setText(filename)
            self.input_file = filename
            if not self.output_edit.text():
                self.output_edit.setText(os.path.dirname(filename))
                self.output_dir = os.path.dirname(filename)
            self.inspect_input()

    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder:
            self.output_edit.setText(folder)
            self.output_dir = folder

    def on_preset_changed(self):
        self.selected_preset_code = self.preset_combo.currentData()
        if self.input_file:
            self.inspect_input()

    def inspect_input(self):
        if not self.input_file or not os.path.exists(self.input_file):
            return

        try:
            from ..core.dem_inspector import DEMInspector
            from ..core.processing_plan import ProcessingPlan
            from ..presets.preset_manager import PresetManager

            info = DEMInspector.inspect(self.input_file)
            pm = PresetManager()
            preset = pm.get_preset(self.selected_preset_code)
            plan = ProcessingPlan.resolve_plan(info, preset)

            log_lines = []
            log_lines.append(f"✓ Raster File: {info['filename']}")
            log_lines.append(f"✓ Dimensions: {info['width']} x {info['height']} pixels")
            log_lines.append(f"✓ Pixel Size: {info['pixel_size_m']:.2f} m/pixel")
            log_lines.append(f"✓ Projected Meter CRS: {info['is_projected']} ({info['unit_name']})")
            log_lines.append(f"✓ Data Type / NoData: {info['data_type']} / {info['nodata']}")
            log_lines.append(f"--------------------------------------------------")
            log_lines.append(f"🎯 RESOLVED PLAN [{preset['name']} v{preset['version']}]:")
            log_lines.append(f"   • MDHS Altitude: {plan['mdhs_params']['altitude_deg']}°")
            log_lines.append(f"   • Slope Unit: Float32 Degrees")
            log_lines.append(f"   • LRM Radius: {plan['lrm_params']['radius_m']} m ({plan['lrm_params']['radius_px']} px, sigma={plan['lrm_params']['sigma']:.2f})")
            log_lines.append(f"   • NoData Policy: {plan['lrm_params']['nodata_policy']}")

            if info['warnings']:
                log_lines.append(f"\n⚠️ WARNINGS:")
                for w in info['warnings']:
                    log_lines.append(f"   ! {w}")

            self.log_text.setPlainText("\n".join(log_lines))
        except Exception as e:
            self.log_text.setPlainText(f"Error inspecting file: {str(e)}")

    def run_job(self):
        input_path = self.input_edit.text().strip()
        output_dir = self.output_edit.text().strip()

        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, "Error", "Please select a valid input GeoTIFF file.")
            return

        if not output_dir or not os.path.exists(output_dir):
            QMessageBox.warning(self, "Error", "Please select a valid output directory.")
            return

        self.btn_run.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)

        try:
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
            preset = pm.get_preset(self.selected_preset_code)
            plan = ProcessingPlan.resolve_plan(dem_info, preset)

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            mdhs_out = os.path.join(output_dir, f"{base_name}_mdhs.tif")
            slope_out = os.path.join(output_dir, f"{base_name}_slope.tif")
            lrm_out = os.path.join(output_dir, f"{base_name}_lrm.tif")

            self.progress_bar.setValue(30)
            MDHSEngine.process(input_path, mdhs_out, altitude_deg=plan['mdhs_params']['altitude_deg'])

            self.progress_bar.setValue(60)
            SlopeEngine.process(input_path, slope_out)

            self.progress_bar.setValue(85)
            LRMEngine.process_tile(input_path, lrm_out, radius_m=plan['lrm_params']['radius_m'])

            self.progress_bar.setValue(95)
            manifest_path = OutputManager.write_manifest(
                output_dir, base_name, plan,
                {'mdhs': mdhs_out, 'slope': slope_out, 'lrm': lrm_out}
            )

            # Add styled group to QGIS
            LayerBuilder.add_styled_group_to_qgis(base_name, mdhs_out, slope_out, lrm_out, plan['style_params'])

            self.progress_bar.setValue(100)
            QMessageBox.information(
                self, "Success",
                f"Job Completed Successfully!\n\nOutputs created:\n- MDHS: {os.path.basename(mdhs_out)}\n- Slope: {os.path.basename(slope_out)}\n- LRM: {os.path.basename(lrm_out)}\n\nStyled layer group added to QGIS canvas."
            )
        except Exception as e:
            QMessageBox.critical(self, "Job Error", f"Processing failed: {str(e)}")
        finally:
            self.btn_run.setEnabled(True)
            self.progress_bar.setVisible(False)
