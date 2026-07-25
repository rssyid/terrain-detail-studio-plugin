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
        except ImportError:
            # Standalone python fallback mock for non-QGIS test environment
            print(f"[LayerBuilder Mock] Created QGIS Group 'Terrain Detail Studio — {run_name}'")
            return

        project = QgsProject.instance()
        root = project.layerTreeRoot()

        group_name = f"Terrain Detail Studio — {run_name}"
        group = root.addGroup(group_name)

        # 1. LRM (Top Layer, Multiply, Preset Opacity e.g. 25%)
        lrm_layer = QgsRasterLayer(lrm_path, "Local Relief (LRM)")
        if lrm_layer.isValid():
            project.addMapLayer(lrm_layer, False)
            group.addLayer(lrm_layer)
            lrm_opacity = style_params.get('lrm', {}).get('opacity_percent', 25) / 100.0
            lrm_layer.setOpacity(lrm_opacity)
            lrm_layer.setBlendMode(6) # Multiply blend mode in QGIS

        # 2. Slope Texture (Middle Layer, Multiply, Preset Opacity e.g. 18%)
        slope_layer = QgsRasterLayer(slope_path, "Slope Texture")
        if slope_layer.isValid():
            project.addMapLayer(slope_layer, False)
            group.addLayer(slope_layer)
            slope_opacity = style_params.get('slope', {}).get('opacity_percent', 18) / 100.0
            slope_layer.setOpacity(slope_opacity)
            slope_layer.setBlendMode(6) # Multiply blend mode in QGIS

        # 3. MDHS Base (Bottom Layer, Normal, 100%)
        mdhs_layer = QgsRasterLayer(mdhs_path, "MDHS Base")
        if mdhs_layer.isValid():
            project.addMapLayer(mdhs_layer, False)
            group.addLayer(mdhs_layer)
            mdhs_layer.setOpacity(1.0)
            mdhs_layer.setBlendMode(0) # Normal blend mode in QGIS
