# -*- coding: utf-8 -*-
"""
Slope Engine
Calculates Slope in degrees (Float32).
"""
import os

try:
    from osgeo import gdal
except ImportError:
    import gdal


class SlopeEngine:
    """Generates Float32 Slope in degrees GeoTIFF."""

    @staticmethod
    def process(input_path: str, output_path: str) -> str:
        """Executes GDAL DEMProcessing slope calculation."""
        partial_output = output_path + ".partial.tif"

        options = gdal.DEMProcessingOptions(
            format='GTiff',
            slopeFormat='degree',
            computeEdges=True,
            creationOptions=[
                'COMPRESS=DEFLATE',
                'PREDICTOR=3',
                'TILED=YES',
                'BLOCKXSIZE=512',
                'BLOCKYSIZE=512',
                'BIGTIFF=IF_SAFER',
            ],
        )

        res = gdal.DEMProcessing(partial_output, input_path, 'slope', options=options)
        res = None # Flush raster

        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(partial_output, output_path)

        return output_path
