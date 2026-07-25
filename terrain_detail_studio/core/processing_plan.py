# -*- coding: utf-8 -*-
"""
Processing Plan Module
Resolves presets into resolved physical & pixel parameters per input raster.
"""
import math

class ProcessingPlan:
    """Calculates exact parameters (meters to pixels, sigma, block sizes) for a given DTM and preset."""

    @staticmethod
    def resolve_plan(dem_info: dict, preset_payload: dict) -> dict:
        pixel_size_m = dem_info['pixel_size_m']
        lrm_config = preset_payload['pipeline']['local_relief']

        radius_m = lrm_config.get('radius_m', 10.0)
        # Meter to pixel conversion: max(1, round(radius_m / pixel_size_m))
        radius_px = max(1, int(round(radius_m / pixel_size_m)))

        # Sigma mode: radius / 3.0
        sigma = radius_px / 3.0

        # Calculate halo padding size (3 * radius_px) to prevent window edge seam artifacts
        halo_px = radius_px * 3

        return {
            'preset_code': preset_payload.get('code', 'custom'),
            'preset_version': preset_payload.get('version', '1.0.0'),
            'input_filepath': dem_info['filepath'],
            'pixel_size_m': pixel_size_m,
            'mdhs_params': preset_payload['pipeline'].get('mdhs', {'altitude_deg': 45}),
            'slope_params': preset_payload['pipeline'].get('slope', {'unit': 'degree'}),
            'lrm_params': {
                'radius_m': radius_m,
                'radius_px': radius_px,
                'sigma': sigma,
                'halo_px': halo_px,
                'nodata_policy': lrm_config.get('nodata_policy', 'valid_cells_renormalized'),
            },
            'style_params': preset_payload.get('style', {}),
        }
