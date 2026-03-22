import pytest
import os
import tempfile
import json
import sys

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_loader import load_config

def test_load_valid_config():
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        json.dump({"test": 123}, f)
        temp_name = f.name
    try:
        conf = load_config(temp_name)
        assert conf["test"] == 123
    finally:
        os.remove(temp_name)

def test_load_invalid_config():
    with pytest.raises(FileNotFoundError):
        load_config("missing_file.json")
