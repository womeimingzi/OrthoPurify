"""Canonical project paths — import from here instead of hardcoding."""
import os
from pathlib import Path


def _find_project_root(start: Path) -> Path:
    """Walk up from *start* until we find the directory containing vlm_backdoor/."""
    for path in (start, *start.parents):
        if (path / "vlm_backdoor").is_dir() and (path / "experiments").is_dir():
            return path
    return start


PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", "")) if os.environ.get("PROJECT_ROOT") else _find_project_root(Path(__file__).resolve())

# ── Model paths ──────────────────────────────────────────────────────────
LLAVA_7B_MODEL_PATH = str(PROJECT_ROOT / "models" / "llava-1.5-7b-hf")
LLAVA_13B_MODEL_PATH = str(PROJECT_ROOT / "models" / "llava-1.5-13b-hf")
QWEN3VL_8B_MODEL_PATH = str(PROJECT_ROOT / "models" / "Qwen3-VL-8B-Instruct")
QWEN3VL_4B_MODEL_PATH = str(PROJECT_ROOT / "models" / "Qwen3-VL-4B-Instruct")

MODEL_PATHS = {
    "llava": LLAVA_7B_MODEL_PATH,
    "qwen3vl": QWEN3VL_8B_MODEL_PATH,
}

# ── Data paths ───────────────────────────────────────────────────────────
DATA_ROOT = str(PROJECT_ROOT / "data")
COCO_DATA_DIR = str(PROJECT_ROOT / "data" / "coco2017")
COCO_ANN_PATH = str(PROJECT_ROOT / "data" / "coco2017" / "annotations" / "captions_train2017.json")
COCO_TRAIN_IMGS = str(PROJECT_ROOT / "data" / "coco2017" / "train2017")
VQAV2_DATA_DIR = str(PROJECT_ROOT / "data" / "vqav2" / "data")
VQAV2_TRAIN_GLOB = str(PROJECT_ROOT / "data" / "vqav2" / "data" / "train-*.parquet")
VQAV2_VAL_GLOB = str(PROJECT_ROOT / "data" / "vqav2" / "data" / "validation-*.parquet")

# ── Dataset loader scripts ───────────────────────────────────────────────
COCO_LOADER_SCRIPT = str(PROJECT_ROOT / "dataset_loaders" / "coco_dataset_script.py")
