# -*- coding: utf-8 -*-
"""
Terrain Detail Studio QGIS Plugin
"""

def classFactory(iface):
    """Factory method called by QGIS to initialize the plugin."""
    from .plugin import TerrainDetailStudioPlugin
    return TerrainDetailStudioPlugin(iface)
