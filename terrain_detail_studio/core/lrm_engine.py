# -*- coding: utf-8 -*-
"""
Gaussian Local Relief Model (LRM) Engine
NoData-Safe Normalized Convolution Surface Subtraction Engine.
"""
import os
import numpy as np

try:
    from osgeo import gdal
except ImportError:
    import gdal

from scipy.ndimage import gaussian_filter


class LRMEngine:
    """Computes Gaussian LRM with normalized convolution NoData handling."""

    @staticmethod
    def process_tile(
        input_path: str,
        output_path: str,
        radius_m: float = 10.0,
        block_size: int = 1024
    ) -> str:
        """Processes input DTM GeoTIFF into Gaussian LRM GeoTIFF in windowed blocks."""
        ds = gdal.Open(input_path, gdal.GA_ReadOnly)
        if ds is None:
            raise ValueError(f"Could not open input raster: {input_path}")

        band = ds.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        width = ds.RasterXSize
        height = ds.RasterYSize
        gt = ds.GetGeoTransform()
        proj = ds.GetProjection()

        pixel_size_m = (abs(gt[1]) + abs(gt[5])) / 2.0
        radius_px = max(1, int(round(radius_m / pixel_size_m)))
        sigma = radius_px / 3.0
        halo = radius_px * 3 # Overlap padding to prevent window edge seams

        partial_output = output_path + ".partial.tif"

        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(
            partial_output,
            width,
            height,
            1,
            gdal.GDT_Float32,
            options=[
                'COMPRESS=DEFLATE',
                'PREDICTOR=3',
                'TILED=YES',
                'BLOCKXSIZE=512',
                'BLOCKYSIZE=512',
                'BIGTIFF=IF_SAFER',
            ]
        )
        out_ds.SetGeoTransform(gt)
        out_ds.SetProjection(proj)

        out_band = out_ds.GetRasterBand(1)
        if nodata is not None:
            out_band.SetNoDataValue(float(nodata))

        # Process in windowed blocks with halo padding
        for y in range(0, height, block_size):
            y_win = min(block_size, height - y)
            y_read_start = max(0, y - halo)
            y_read_end = min(height, y + y_win + halo)
            y_read_len = y_read_end - y_read_start

            y_offset = y - y_read_start

            for x in range(0, width, block_size):
                x_win = min(block_size, width - x)
                x_read_start = max(0, x - halo)
                x_read_end = min(width, x + x_win + halo)
                x_read_len = x_read_end - x_read_start

                x_offset = x - x_read_start

                # Read block with halo
                dtm_block = band.ReadAsArray(x_read_start, y_read_start, x_read_len, y_read_len).astype(np.float32)

                # Mask valid cells (M = 1 for valid, 0 for NoData)
                if nodata is not None:
                    valid_mask = (dtm_block != nodata) & (~np.isnan(dtm_block))
                else:
                    valid_mask = ~np.isnan(dtm_block)

                dtm_masked = np.where(valid_mask, dtm_block, 0.0)
                mask_float = valid_mask.astype(np.float32)

                # Normalized Convolution: S = G(DTM * M) / G(M)
                g_dtm = gaussian_filter(dtm_masked, sigma=sigma, mode='reflect')
                g_mask = gaussian_filter(mask_float, sigma=sigma, mode='reflect')

                # Avoid division by zero
                with np.errstate(divide='ignore', invalid='ignore'):
                    smooth_surface = np.where(g_mask > 1e-5, g_dtm / g_mask, np.nan)

                # LRM = DTM - SmoothSurface
                lrm_block = dtm_block - smooth_surface

                # Restore NoData
                if nodata is not None:
                    lrm_block = np.where(valid_mask, lrm_block, nodata)
                else:
                    lrm_block = np.where(valid_mask, lrm_block, np.nan)

                # Extract core tile without halo
                core_tile = lrm_block[y_offset:y_offset + y_win, x_offset:x_offset + x_win]

                # Write core tile to output
                out_band.WriteArray(core_tile, x, y)

        out_band.FlushCache()
        out_ds = None
        ds = None

        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(partial_output, output_path)

        return output_path
