# -*- coding: utf-8 -*-
"""
Batch Folder Processing Dialog
Scans input folder, manages persistent SQLite job queue, and creates VRT mosaics.
"""
import os

class BatchDialog:
    """Batch Processing Dialog Class."""

    def __init__(self, input_folder: str, output_root: str, db_path: str):
        self.input_folder = input_folder
        self.output_root = output_root
        self.db_path = db_path

    def scan_folder(self) -> list:
        """Recursively scans folder for compatible GeoTIFF files."""
        tif_files = []
        if os.path.exists(self.input_folder):
            for root, _, files in os.walk(self.input_folder):
                for f in files:
                    if f.lower().endswith(('.tif', '.tiff')) and not f.endswith('.partial.tif'):
                        tif_files.append(os.path.join(root, f))
        return tif_files

    def run_batch_pipeline(self, preset_code: str = 'balanced-detail') -> dict:
        from ..core.batch_queue import BatchQueue
        from ..core.mdhs_engine import MDHSEngine
        from ..core.slope_engine import SlopeEngine
        from ..core.lrm_engine import LRMEngine
        from ..core.vrt_builder import VRTBuilder
        from ..core.layer_builder import LayerBuilder
        from ..presets.preset_manager import PresetManager

        queue = BatchQueue(self.db_path)
        tif_files = self.scan_folder()

        for f in tif_files:
            rel_name = os.path.splitext(os.path.basename(f))[0]
            out_prefix = os.path.join(self.output_root, rel_name)
            queue.add_job(f, out_prefix)

        pm = PresetManager()
        preset = pm.get_preset(preset_code)

        mdhs_tiles = []
        slope_tiles = []
        lrm_tiles = []

        while True:
            job = queue.get_next_job()
            if not job:
                break

            job_id, input_path, out_prefix = job
            queue.update_status(job_id, 'Running')

            try:
                mdhs_out = f"{out_prefix}_mdhs.tif"
                slope_out = f"{out_prefix}_slope.tif"
                lrm_out = f"{out_prefix}_lrm.tif"

                radius_m = preset['pipeline']['local_relief']['radius_m']

                MDHSEngine.process(input_path, mdhs_out)
                SlopeEngine.process(input_path, slope_out)
                LRMEngine.process_tile(input_path, lrm_out, radius_m=radius_m)

                mdhs_tiles.append(mdhs_out)
                slope_tiles.append(slope_out)
                lrm_tiles.append(lrm_out)

                queue.update_status(job_id, 'Completed')
            except Exception as e:
                queue.update_status(job_id, 'Failed', str(e))

        # Build VRT Mosaics if multiple tiles
        vrt_mdhs = os.path.join(self.output_root, "batch_MDHS.vrt")
        vrt_slope = os.path.join(self.output_root, "batch_Slope.vrt")
        vrt_lrm = os.path.join(self.output_root, "batch_LRM.vrt")

        if mdhs_tiles:
            VRTBuilder.build_vrt(mdhs_tiles, vrt_mdhs)
            VRTBuilder.build_vrt(slope_tiles, vrt_slope)
            VRTBuilder.build_vrt(lrm_tiles, vrt_lrm)

            LayerBuilder.add_styled_group_to_qgis("Batch Folder Run", vrt_mdhs, vrt_slope, vrt_lrm, preset['style'])

        return {
            'processed_count': len(mdhs_tiles),
            'vrts': {'mdhs': vrt_mdhs, 'slope': vrt_slope, 'lrm': vrt_lrm},
            'summary': queue.get_summary(),
        }
