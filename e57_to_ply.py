import subprocess
import sys

# Function to install packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# install if not already available
try:
    import pye57
except ImportError:
    install('pye57')
    import pye57

import numpy as np
import struct

def transform_points(points, translation, rotation):
    """Apply translation and rotation to the points."""
    # Convert rotation to a rotation matrix
    rotation_matrix = np.array(rotation).reshape(3, 3)
    # Apply rotation and translation
    transformed_points = np.dot(points, rotation_matrix.T) + translation
    return transformed_points

def convert_e57_to_ply(e57_filename, ply_filename):
    """Converts an E57 file to a PLY file."""

    with pye57.E57(e57_filename, 'r') as e57:
        num_scans = e57.scan_count
        
        all_points = []
        all_colors = []
        has_colors = False

        for scan_index in range(num_scans):
            data = e57.read_scan_raw(scan_index)
            header = e57.get_header(scan_index)

            # Accumulate point data
            points = np.column_stack([
                data['cartesianX'],
                data['cartesianY'],
                data['cartesianZ'],
            ])

            points_absolute = e57.to_global(points, header.rotation, header.translation)

            # Transform points based on origin and rotation
            all_points.append(points_absolute)

            # Check and accumulate color data if available
            if 'colorRed' in data:
                if not has_colors:
                    has_colors = True
                colors = np.column_stack([
                    data['colorRed'],
                    data['colorGreen'],
                    data['colorBlue']
                ]).astype(np.uint8)
                all_colors.append(colors)

        # Concatenate all scans
        all_points = np.vstack(all_points)
        if has_colors:
            all_colors = np.vstack(all_colors)
        else:
            all_colors = None
    
    with open(ply_filename, 'wb') as ply_file:
    	# header
        ply_file.write(b'ply\n')
        ply_file.write(b'format binary_little_endian 1.0\n')
        ply_file.write(f'element vertex {len(all_points)}\n'.encode())
        ply_file.write(b'property float x\n')
        ply_file.write(b'property float y\n')
        ply_file.write(b'property float z\n')
        if has_colors:
            ply_file.write(b'property uchar red\n')
            ply_file.write(b'property uchar green\n')
            ply_file.write(b'property uchar blue\n')
        ply_file.write(b'end_header\n')
        
	#content
        for point, color in zip(all_points, all_colors):
            ply_file.write(struct.pack("<fff", *point))
            ply_file.write(struct.pack("BBB", *color))

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        convert_e57_to_ply('test.e57', 'test.ply')
        print("Usage: python convert_e57_to_ply.py <input_e57_file> <output_ply_file>")
    else:
        convert_e57_to_ply(sys.argv[1], sys.argv[2])

