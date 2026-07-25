# -*- coding: utf-8 -*-
"""
Unit Test Suite for Gaussian LRM & Processing Engines
"""
import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from terrain_detail_studio.core.processing_plan import ProcessingPlan
from terrain_detail_studio.licensing.offline_lease import OfflineLeaseVerifier


class TestProcessingEngines(unittest.TestCase):

    def test_meter_to_pixel_conversion(self):
        dem_info = {
            'filepath': 'dummy.tif',
            'pixel_size_m': 0.5,
        }
        preset = {
            'code': 'balanced-detail',
            'version': '1.0.0',
            'pipeline': {
                'local_relief': {'radius_m': 10.0, 'nodata_policy': 'valid_cells_renormalized'}
            }
        }

        plan = ProcessingPlan.resolve_plan(dem_info, preset)
        # 10m / 0.5m = 20 pixels
        self.assertEqual(plan['lrm_params']['radius_px'], 20)
        self.assertAlmostEqual(plan['lrm_params']['sigma'], 20 / 3.0)

    def test_offline_lease_verification(self):
        # Sample signed lease payload
        sample_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "ZXlKMGIzMGxYMmxrSWpvaWJHVmhjMlZmTVRJeU0wRXlOaklpTENKbWFXNWtZWFI1Y0dVaU9pSk1"
            "TVk5GVTFWU1NpaTkuZXlKMGIzMGxYMmxrSWpvaWJHVmhjMlZmTVRJeU0wRXlOaklpTENKbWFXNWt"
            "ZWFI1Y0dVaU9pSk1TVk5GVTFWU1NpaTku"
        )
        res = OfflineLeaseVerifier.verify_lease(sample_token)
        # Should gracefully return invalid or decoded state without crashing
        self.assertIn('is_valid', res)


if __name__ == '__main__':
    unittest.main()
