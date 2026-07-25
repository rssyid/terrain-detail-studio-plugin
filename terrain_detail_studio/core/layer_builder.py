# -*- coding: utf-8 -*-
"""
Layer & QGIS Group Builder
Adds styled raster layers in mandatory cartographic order to active QGIS project.
"""
import os

class LayerBuilder:
    """Builds QGIS layer group and applies cartographic blending modes and opacities."""

    @staticmethod
    def add_styled_group_to_qgis(
        run_name: str,
        mdhs_path: str,
        slope_path: str,
        lrm_path: str,
        style_params: dict
    ):
        """Adds layers to QGIS Layer Tree in mandatory order: LRM -> Slope -> MDHS."""
        try:
            from qgis.core import QgsProject, QgsRasterLayer
            from qgis.PyQt.QtGui import QPainter
            blend_multiply = QPainter.CompositionMode_Multiply
            blend_normal = QPainter.CompositionMode_SourceOver
        except ImportError:
            # Standalone python fallback mock for non-QGIS test environment
            print(f"[LayerBuilder Mock] Created QGIS Group 'Terrain Detail Studio — {run_name}'")
            return

        project = QgsProject.instance()
        root = project.layerTreeRoot()

        group_name = f"Terrain Detail Studio — {run_name}"
        group = root.addGroup(group_name)

        style_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'styles'))

        # 1. LRM (Top Layer, Multiply, Preset Opacity e.g. 25%)
        lrm_layer = QgsRasterLayer(lrm_path, "Local Relief (LRM)")
        if lrm_layer.isValid():
            lrm_qml = os.path.join(style_dir, 'lrm.qml')
            if os.path.exists(lrm_qml):
                lrm_layer.loadNamedStyle(lrm_qml)
            project.addMapLayer(lrm_layer, False)
            group.addLayer(lrm_layer)
            lrm_opacity = style_params.get('lrm', {}).get('opacity_percent', 25) / 100.0
            lrm_layer.setOpacity(lrm_opacity)
            if blend_multiply is not None:
                try:
                    lrm_layer.setBlendMode(blend_multiply)
                except Exception:
                    pass

        # 2. Slope Texture (Middle Layer, Multiply, Preset Opacity e.g. 18%)
        slope_layer = QgsRasterLayer(slope_path, "Slope Texture")
        if slope_layer.isValid():
            slope_qml = os.path.join(style_dir, 'slope.qml')
            if os.path.exists(slope_qml):
                slope_layer.loadNamedStyle(slope_qml)
            project.addMapLayer(slope_layer, False)
            group.addLayer(slope_layer)
            slope_opacity = style_params.get('slope', {}).get('opacity_percent', 18) / 100.0
            slope_layer.setOpacity(slope_opacity)
            if blend_multiply is not None:
                try:
                    slope_layer.setBlendMode(blend_multiply)
                except Exception:
                    pass

        # 3. MDHS Base (Bottom Layer, Normal, 100%)
        mdhs_layer = QgsRasterLayer(mdhs_path, "MDHS Base")
        if mdhs_layer.isValid():
            mdhs_qml = os.path.join(style_dir, 'mdhs.qml')
            if os.path.exists(mdhs_qml):
                mdhs_layer.loadNamedStyle(mdhs_qml)
            project.addMapLayer(mdhs_layer, False)
            group.addLayer(mdhs_layer)
            mdhs_layer.setOpacity(1.0)
            if blend_normal is not None:
                try:
                    mdhs_layer.setBlendMode(blend_normal)
                except Exception:
                    pass
