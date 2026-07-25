# -*- coding: utf-8 -*-
"""
Standalone Reference Script for Terrain Detail Studio
Generates synthetic DEM raster and runs full MDHS + Slope + Gaussian LRM pipeline.
"""
import os
import sys
import numpy as np

try:
    from osgeo import gdal, osr
except ImportError:
    import gdal
    import osr

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from terrain_detail_studio.core.dem_inspector import DEMInspector
from terrain_detail_studio.core.processing_plan import ProcessingPlan
from terrain_detail_studio.core.mdhs_engine import MDHSEngine
from terrain_detail_studio.core.slope_engine import SlopeEngine
from terrain_detail_studio.core.lrm_engine import LRMEngine
from terrain_detail_studio.core.output_manager import OutputManager
from terrain_detail_studio.presets.preset_manager import PresetManager


def create_synthetic_dem(filepath: str, width: int = 500, height: int = 500, pixel_size: float = 1.0):
    """Creates a synthetic bare-earth DTM GeoTIFF with a mound, trench, and NoData hole."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(filepath, width, height, 1, gdal.GDT_Float32)

    # Set GeoTransform & SRS (UTM Zone 48N in meters)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(32648)
    ds.SetProjection(srs.ExportToWkt())
    ds.SetGeoTransform([500000.0, pixel_size, 0.0, 9000000.0, 0.0, -pixel_size])

    # Generate synthetic elevation grid
    y, x = np.ogrid[:height, :width]
    center_y, center_x = height // 2, width // 2

    # Base planar slope
    elevation = 100.0 + (x * 0.05) + (y * 0.02)

    # Add 15m elevation mound in center
    mound = 15.0 * np.exp(-((x - center_x)**2 + (y - center_y)**2) / (50.0**2))
    elevation += mound

    # Add 5m trench/canal feature
    trench = -5.0 * np.exp(-((y - (center_y + 100))**2) / (10.0**2))
    elevation += trench

    # Add NoData void in top-right corner
    nodata_val = -9999.0
    elevation[50:100, 350:400] = nodata_val

    band = ds.GetRasterBand(1)
    band.SetNoDataValue(nodata_val)
    band.WriteArray(elevation.astype(np.float32))
    band.FlushCache()
    ds = None
    print(f"✅ Synthetic DEM created at: {filepath}")


def run_reference_pipeline():
    print("🚀 Starting Terrain Detail Studio Reference Engine...")
    test_dir = os.path.dirname(__file__)
    output_dir = os.path.join(test_dir, 'output_ref')
    input_dem = os.path.join(output_dir, 'synthetic_dem.tif')

    # Step 1: Create synthetic DTM
    create_synthetic_dem(input_dem)

    # Step 2: Preflight Inspection
    dem_info = DEMInspector.inspect(input_dem)
    print(f"📊 DEM Info: {dem_info['width']}x{dem_info['height']} @ {dem_info['pixel_size_m']}m/pixel")

    # Step 3: Resolve Preset Plan
    pm = PresetManager()
    preset = pm.get_preset('balanced-detail')
    plan = ProcessingPlan.resolve_plan(dem_info, preset)
    print(f"🎯 Resolved LRM Radius: {plan['lrm_params']['radius_m']}m ({plan['lrm_params']['radius_px']} px)")

    # Step 4: Process MDHS Base
    mdhs_out = os.path.join(output_dir, 'ref_mdhs.tif')
    MDHSEngine.process(input_dem, mdhs_out, altitude_deg=plan['mdhs_params']['altitude_deg'])
    print(f"✅ MDHS Generated: {mdhs_out}")

    # Step 5: Process Slope
    slope_out = os.path.join(output_dir, 'ref_slope.tif')
    SlopeEngine.process(input_dem, slope_out)
    print(f"✅ Slope Generated: {slope_out}")

    # Step 6: Process Gaussian LRM
    lrm_out = os.path.join(output_dir, 'ref_lrm.tif')
    LRMEngine.process_tile(input_dem, lrm_out, radius_m=plan['lrm_params']['radius_m'])
    print(f"✅ Gaussian LRM Generated: {lrm_out}")

    # Step 7: Validate & Write Manifest
    v1 = OutputManager.validate_raster_output(mdhs_out)
    v2 = OutputManager.validate_raster_output(slope_out)
    v3 = OutputManager.validate_raster_output(lrm_out)

    if v1 and v2 and v3:
        manifest_path = OutputManager.write_manifest(
            output_dir,
            'synthetic_reference_run',
            plan,
            {'mdhs': mdhs_out, 'slope': slope_out, 'lrm': lrm_out}
        )
        print(f"📄 Manifest Written: {manifest_path}")
        print("🎉 Reference Pipeline Execution Completed Successfully!")
    else:
        print("❌ Output validation failed!")


if __name__ == '__main__':
    run_reference_pipeline()
