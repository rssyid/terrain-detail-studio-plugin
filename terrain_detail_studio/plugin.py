# -*- coding: utf-8 -*-
"""
Terrain Detail Studio QGIS Plugin Main Entry Class
"""
import os
import sys

class TerrainDetailStudioPlugin:
    """QGIS Plugin Main Class for Terrain Detail Studio."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dlg = None

    def initGui(self):
        """Called by QGIS when plugin is loaded into GUI."""
        from qgis.PyQt.QtWidgets import QAction
        from qgis.PyQt.QtGui import QIcon

        icon_path = os.path.join(self.plugin_dir, 'resources', 'icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.action = QAction(icon, "Terrain Detail Studio", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        # Add to Raster Menu and Toolbar
        self.iface.addPluginToRasterMenu("Terrain Detail Studio", self.action)
        self.iface.addRasterToolBarIcon(self.action)

    def unload(self):
        """Called when plugin is unloaded/disabled."""
        if self.action:
            self.iface.removePluginRasterMenu("Terrain Detail Studio", self.action)
            self.iface.removeRasterToolBarIcon(self.action)

    def run(self):
        """Execute plugin main dialog window."""
        try:
            from .gui.main_dialog import TerrainDetailStudioDialog
            if self.dlg is None:
                self.dlg = TerrainDetailStudioDialog(iface=self.iface)
            
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
        except Exception as e:
            print(f"Error opening Terrain Detail Studio dialog: {e}")
