# -*- coding: utf-8 -*-
"""
Output Manager and Manifest Serializer
Handles atomic file operations, raster output validation, and manifest generation.
"""
import os
import json
import time

try:
    from osgeo import gdal
except ImportError:
    import gdal


class OutputManager:
    """Manages output directory structure, validation, and execution manifests."""

    @staticmethod
    def validate_raster_output(filepath: str, expected_dtype: str = None) -> bool:
        """Validates that output raster exists, is readable, non-empty, and valid."""
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return False

        ds = gdal.Open(filepath, gdal.GA_ReadOnly)
        if ds is None:
            return False

        if ds.RasterCount < 1:
            ds = None
            return False

        band = ds.GetRasterBand(1)
        stats = band.GetStatistics(True, True)
        ds = None

        # Ensure valid statistics can be calculated
        return stats is not None and len(stats) == 4

    @staticmethod
    def write_manifest(output_dir: str, run_name: str, plan: dict, generated_files: dict) -> str:
        """Serializes resolved processing manifest for reproducibility."""
        manifest_path = os.path.join(output_dir, f"{run_name}_manifest.json")

        manifest = {
            'plugin_version': '1.0.0',
            'run_name': run_name,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'plan': plan,
            'outputs': generated_files,
        }

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        return manifest_path
