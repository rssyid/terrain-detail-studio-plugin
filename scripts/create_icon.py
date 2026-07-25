import os
import struct
import zlib

def create_png_icon(filepath: str):
    """Generates a 64x64 PNG icon for Terrain Detail Studio QGIS plugin."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    width = 64
    height = 64

    # PNG Header
    png_header = b'\x89PNG\r\n\x1a\n'

    # IHDR Chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # IDAT Chunk (Image Data: Mountain/Terrain icon with Yellow/Cyan accent)
    raw_rows = []
    for y in range(height):
        row = [0] # Filter byte
        for x in range(width):
            # Draw mountain terrain contour
            terrain_y = int(32 + 12 * np_sin((x - 16) / 8.0) - 8 * np_cos((x - 32) / 12.0)) if 'np_sin' in globals() else int(32 + 10 * ((x % 16) - 8)/8.0)
            if y < 8 or y > 56 or x < 8 or x > 56:
                # Border (Black)
                r, g, b, a = 0, 0, 0, 255
            elif y >= terrain_y:
                # Terrain Base (Vivid Yellow/Green gradient)
                r = int(255 - (y * 2))
                g = int(230)
                b = int(0)
                a = 255
            else:
                # Sky (Vivid Cyan)
                r, g, b, a = 0, 240, 255, 255
            row.extend([max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), a])
        raw_rows.append(bytes(row))

    uncompressed = b''.join(raw_rows)
    compressed = zlib.compress(uncompressed)

    idat_crc = zlib.crc32(b'IDAT' + compressed)
    idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)

    # IEND Chunk
    iend_crc = zlib.crc32(b'IEND')
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

    with open(filepath, 'wb') as f:
        f.write(png_header + ihdr_chunk + idat_chunk + iend_chunk)

    print(f"Created plugin icon at {filepath}")

def np_sin(x):
    import math
    return math.sin(x)

def np_cos(x):
    import math
    return math.cos(x)

if __name__ == '__main__':
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'terrain_detail_studio', 'resources', 'icon.png'))
    create_png_icon(icon_path)
