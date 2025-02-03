import os
import json

import numpy as np

def hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    color_hex = color_hex.lstrip('#')
    return (int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16))

def read_config(path: str) -> dict:

	with open(path) as f:
		result = json.load(f)

	result['output_path'] = os.path.abspath(result['output_path'])
	result['brush_color'] = [hex_to_rgb(color) for color in result['brush_color']]

	os.system('clear')
 
	if result['debug']:
		print(f'Config values:\n{result}')

	return result

def create_canvas(config: dict) -> None:
    return np.zeros((config['height'], config['width'], 3), dtype=np.uint8)
