import os
import json


PRESET_DIR = "presets"
os.makedirs(PRESET_DIR, exist_ok=True)

def save_preset(name, config):
    path = os.path.join(PRESET_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

def load_preset(name):
    path = os.path.join(PRESET_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Preset '{name}' does not exist.")
    with open(path, "r") as f:
        return json.load(f)

def list_presets():
    return [f[:-5] for f in os.listdir(PRESET_DIR) if f.endswith(".json")]