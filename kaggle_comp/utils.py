# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_utils.ipynb.

# %% ../nbs/00_utils.ipynb 3
from __future__ import annotations

import abc, datetime, random, os
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from fastai.losses import CrossEntropyLossFlat
from fastai.test_utils import show_install

# %% auto 0
__all__ = ['default_seed', 'kaggle_comp', 'run_env', 'detect_env', 'print_dev_environment', 'get_paths', 'setup_comp',
           'comp_metric_score', 'get_run_id']

# %% ../nbs/00_utils.ipynb 7
default_seed = int(os.getenv("RANDOM_SEED", 42))
kaggle_comp = os.getenv("KAGGLE_COMP","feedback-prize-english-language-learning")

# %% ../nbs/00_utils.ipynb 9
def detect_env():
    """A helper function that detects where you are running code"""
    if os.environ.get("KAGGLE_KERNEL_RUN_TYPE", False):
        run_env = "kaggle"
    elif os.path.isdir("/content"):
        run_env = "colab"
    elif os.path.isdir("../nbs") or  os.path.isdir("../../nbs"):
        run_env = "local_nb"
    else:
        run_env = "script"

    return run_env


run_env = detect_env()

if run_env != "kaggle":
    from kaggle import api

# %% ../nbs/00_utils.ipynb 11
def print_dev_environment():
    """Provides details on your development environment including packages installed, cuda/cudnn availability, GPUs, etc."""
    print(show_install())

# %% ../nbs/00_utils.ipynb 14
def get_paths(override_project_root=None):
    """Returns data, models, and log folder paths based on your where you are running the code"""
    if run_env == "kaggle":
        data_path = Path(".")
        comp_data_path = clean_data_path= Path(f"../input/{kaggle_comp}")
        working_path = Path("/kaggle/working")
        models_path = working_path / "models"
        logs_path = working_path / "logs"

    elif run_env == "colab":
        proj_root_path = override_project_root or Path(".")

        data_path = proj_root_path
        comp_data_path = clean_data_path = data_path
        models_path = data_path / "models"
        logs_path = data_path / "logs"

    elif run_env == "local_nb":
        proj_root_path = override_project_root or Path("..")

        data_path = Path(proj_root_path/"data")
        comp_data_path = data_path / "comp"
        clean_data_path = data_path / "clean"
        models_path = Path(proj_root_path/"models")
        logs_path = Path(proj_root_path/"logs")

        comp_data_path.mkdir(parents=True, exist_ok=True)
        clean_data_path.mkdir(parents=True, exist_ok=True)

    elif run_env == "script":
        proj_root_path = override_project_root or Path(".")

        data_path = Path(proj_root_path/"data")
        comp_data_path = data_path / "comp"
        clean_data_path = data_path / "clean"
        models_path = Path(proj_root_path/"models")
        logs_path = Path(proj_root_path/"logs")

        comp_data_path.mkdir(parents=True, exist_ok=True)
        clean_data_path.mkdir(parents=True, exist_ok=True)

    try:
        models_path.mkdir(parents=True, exist_ok=True)
        logs_path.mkdir(parents=True, exist_ok=True)
    except:
        print("Unable to create models and logs folders")
        
    return data_path, comp_data_path, clean_data_path, models_path, logs_path

# %% ../nbs/00_utils.ipynb 15
def setup_comp(override_project_root=None, comp_data_path_override=None):
    """Ensures that the expected data, models, and logs folders exist and that the competition data exists in the 'comp_data_path'."""

    if comp_data_path_override is not None:
        comp_data_path = comp_data_path_override
    else:
        _, comp_data_path, *_ = get_paths(override_project_root)

    if run_env != "kaggle":
        if not comp_data_path.exists() or not any(comp_data_path.iterdir()):
            import zipfile

            api.competition_download_cli(kaggle_comp)

            zipfile.ZipFile(f"{kaggle_comp}.zip").extractall(comp_data_path)
            Path(f"{kaggle_comp}.zip").unlink(missing_ok=True)

        return comp_data_path
    else:
        return Path(f"../input/{kaggle_comp}")

# %% ../nbs/00_utils.ipynb 18
def comp_metric_score(preds, targs):
    """This competition is evaluated using "multi-class logarithmic loss" (e.g., cross-entropy loss). Expects numpy arrays."""
    probs = np.exp(preds) / np.sum(np.exp(preds), axis=1, keepdims=True)

    correct_class_probs = probs[range(len(preds)), targs]
    nll = -np.log(correct_class_probs)
    return nll.mean()

# %% ../nbs/00_utils.ipynb 23
def get_run_id():
    run_id = str(datetime.datetime.now())[:16].replace(":", "_").replace(" ", "_").replace("-", "_")
    return run_id
