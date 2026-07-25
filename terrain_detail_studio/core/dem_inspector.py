# -*- coding: utf-8 -*-
"""
DEM Inspector and Preflight Validation Module
"""
import os
import shutil

try:
    from osgeo import gdal, osr
except ImportError:
    import gdal
    import osr


class DEMInspector:
    """Preflight validator for input bare-earth DTM GeoTIFF files."""

    @staticmethod
    def inspect(filepath: str, min_pixel_size: float = 0.1, max_pixel_size: float = 2.0) -> dict:
        """Inspects input DTM raster and returns detailed metadata and validation warnings."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file does not exist: {filepath}")

        ds = gdal.Open(filepath, gdal.GA_ReadOnly)
        if ds is None:
            raise ValueError(f"File is not a readable GDAL raster: {filepath}")

        band_count = ds.RasterCount
        if band_count != 1:
            raise ValueError(f"Expected single-band DTM, found {band_count} bands.")

        band = ds.GetRasterBand(1)
        data_type = gdal.GetDataTypeName(band.DataType)
        nodata = band.GetNoDataValue()

        gt = ds.GetGeoTransform()
        pixel_width = abs(gt[1])
        pixel_height = abs(gt[5])

        # CRS Check
        projection = ds.GetProjection()
        srs = osr.SpatialReference()
        srs.ImportFromWkt(projection)
        
        is_projected = srs.IsProjected() == 1
        unit_name = srs.GetLinearUnitName()

        warnings = []
        if not is_projected or unit_name.lower() not in ['metre', 'meter', 'm']:
            warnings.append(f"Geographic/Non-meter CRS detected ({unit_name}). Projected CRS in meters is recommended.")

        avg_pixel_size = (pixel_width + pixel_height) / 2.0
        if avg_pixel_size < min_pixel_size or avg_pixel_size > max_pixel_size:
            warnings.append(f"Pixel size {avg_pixel_size:.2f}m is outside recommended 0.1m - 2.0m range.")

        # Check free disk space
        file_size_bytes = os.path.getsize(filepath)
        estimated_output_space = file_size_bytes * 5 # Expect 5x output storage space
        output_dir = os.path.dirname(filepath)
        free_space = shutil.disk_usage(output_dir).free
        if free_space < estimated_output_space:
            warnings.append("Insufficient disk space available for processing outputs.")

        ds = None # Close dataset

        return {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'width': ds.RasterXSize if ds else 0,
            'height': ds.RasterYSize if ds else 0,
            'band_count': band_count,
            'data_type': data_type,
            'nodata': nodata,
            'pixel_size_m': avg_pixel_size,
            'is_projected': is_projected,
            'unit_name': unit_name,
            'file_size_mb': round(file_size_bytes / (1024 * 1024), 2),
            'warnings': warnings,
            'is_valid': len(warnings) == 0 or not any('Single-band' in w for w in warnings),
        }
