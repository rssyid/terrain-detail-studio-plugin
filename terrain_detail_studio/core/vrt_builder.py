# -*- coding: utf-8 -*-
"""
VRT Builder Module
Constructs Virtual Raster Mosaics (VRT) for MDHS, Slope, and LRM batch runs.
"""
import os

try:
    from osgeo import gdal
except ImportError:
    import gdal


class VRTBuilder:
    """Builds GDAL Virtual Rasters (VRT) from list of valid GeoTIFF tiles."""

    @staticmethod
    def build_vrt(input_tiles: list, output_vrt_path: str) -> str:
        """Constructs a seamless VRT mosaic from multiple raster tiles."""
        if not input_tiles:
            raise ValueError("No input tiles provided for VRT building.")

        vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
        vrt_ds = gdal.BuildVRT(output_vrt_path, input_tiles, options=vrt_options)
        vrt_ds = None # Flush to disk

        if not os.path.exists(output_vrt_path):
            raise RuntimeError(f"Failed to build VRT at {output_vrt_path}")

        return output_vrt_path
