# -*- coding: utf-8 -*-
"""
Packaging Script for Terrain Detail Studio QGIS Plugin
Creates distribution ZIP archive: terrain_detail_studio-1.0.0.zip
"""
import os
import zipfile
import hashlib

def package_plugin():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    plugin_src_dir = os.path.join(root_dir, 'terrain_detail_studio')
    dist_dir = os.path.join(root_dir, 'dist')
    os.makedirs(dist_dir, exist_ok=True)

    zip_filename = 'terrain_detail_studio-1.0.0.zip'
    zip_path = os.path.join(dist_dir, zip_filename)

    print(f"Packaging QGIS plugin from {plugin_src_dir} into {zip_path}...")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(plugin_src_dir):
            # Skip pycache and temporary files
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for file in files:
                if file.endswith(('.pyc', '.pyo', '.partial.tif', '.DS_Store')):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, rel_path)

    # Compute SHA-256 checksum
    hasher = hashlib.sha256()
    with open(zip_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    sha256_hash = hasher.hexdigest()

    file_size_kb = round(os.path.getsize(zip_path) / 1024, 2)
    print(f"Plugin ZIP Archive created successfully!")
    print(f"   File Path: {zip_path}")
    print(f"   Size: {file_size_kb} KB")
    print(f"   SHA-256: {sha256_hash}")

    return zip_path, sha256_hash

if __name__ == '__main__':
    package_plugin()
