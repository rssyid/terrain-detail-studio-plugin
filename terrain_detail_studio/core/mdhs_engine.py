# -*- coding: utf-8 -*-
"""
Multidirectional Hillshade (MDHS) Engine
Uses GDAL multidirectional hillshade algorithm.
"""
import os

try:
    from osgeo import gdal
except ImportError:
    import gdal


class MDHSEngine:
    """Generates 8-bit UInt8 Multidirectional Hillshade GeoTIFF."""

    @staticmethod
    def process(input_path: str, output_path: str, altitude_deg: float = 45.0) -> str:
        """Executes GDAL DEMProcessing multidirectional hillshade."""
        partial_output = output_path + ".partial.tif"

        options = gdal.DEMProcessingOptions(
            format='GTiff',
            computeEdges=True,
            options=['-multidirectional', '-alt', str(altitude_deg)],
            creationOptions=[
                'COMPRESS=DEFLATE',
                'PREDICTOR=2',
                'TILED=YES',
                'BLOCKXSIZE=512',
                'BLOCKYSIZE=512',
                'BIGTIFF=IF_SAFER',
            ],
        )

        res = gdal.DEMProcessing(partial_output, input_path, 'hillshade', options=options)
        res = None # Flush raster

        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(partial_output, output_path)

        return output_path
