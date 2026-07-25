# -*- coding: utf-8 -*-
"""
Preset Manager Module
Manages builtin and published Pro presets.
"""
import os
import json

class PresetManager:
    """Loads and validates cartographic presets."""

    def __init__(self, builtin_dir: str = None):
        if builtin_dir is None:
            builtin_dir = os.path.join(os.path.dirname(__file__), 'builtin')
        self.builtin_dir = builtin_dir

    def get_preset(self, code: str) -> dict:
        """Loads preset JSON recipe by code."""
        preset_file = os.path.join(self.builtin_dir, f"{code}.json")
        if not os.path.exists(preset_file):
            raise FileNotFoundError(f"Builtin preset '{code}' not found.")

        with open(preset_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_builtin_presets(self) -> list:
        """Lists all builtin presets."""
        presets = []
        if os.path.exists(self.builtin_dir):
            for fname in os.listdir(self.builtin_dir):
                if fname.endswith('.json'):
                    with open(os.path.join(self.builtin_dir, fname), 'r', encoding='utf-8') as f:
                        presets.append(json.load(f))
        return presets
