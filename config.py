"""
This module provides functions to load and dump configurations
"""

import os
import json
from typing import Any


def load_config(config_path: str) -> dict[str, Any] | None:
    """
    Load a configuration file from the given path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict[str, Any]: The loaded configuration as a dictionary.
    """
    if not os.path.exists(config_path):
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    return config


def dump_config(config: dict[str, Any], config_path: str) -> None:
    """
    Dump a configuration dictionary to a file.

    Args:
        config (dict[str, Any]): The configuration to dump.
        config_path (str): The path to the configuration file.
    """
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
