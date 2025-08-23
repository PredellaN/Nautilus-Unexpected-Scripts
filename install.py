requirements: list[str] = [
    "einops",
    "transformers",
    "torchvision",
    "scikit-image",
    "opencv-python-headless",
    "pillow",
    "numpy",
    "kornia",
    "timm",
    "torchaudio",
    "torchcodec",
    "stempeg",
    "demucs",
    "pye57",
]

import os, sys, subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
deps_dir = os.path.join(script_dir, ".dependencies")

subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", deps_dir, *requirements])