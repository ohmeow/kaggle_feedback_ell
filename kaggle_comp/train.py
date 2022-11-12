# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_train.ipynb.

# %% auto 0
__all__ = ['run_fold']

# %% ../nbs/05_train.ipynb 3
import argparse, os
from pathlib import Path
import warnings

import pandas as pd
from transformers import logging

from . import config, train_dispatcher, utils
from .config import CFG

# silence all the HF warnings
warnings.simplefilter("ignore")
logging.set_verbosity_error()
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# %% ../nbs/05_train.ipynb 6
def run_fold(
    CFG,
    n_fold: int,
    experiment_name: str,
    run_id: str,
    grid_id: str,
    train_data=config.TRAINING_FILE,
    verbose: bool = True,
):

    train_config = train_dispatcher.experiments[experiment_name]
    model_name = f"{experiment_name}_{run_id}_{grid_id}_fold_{n_fold}"

    comp_trainer_cls = train_config["comp_trainer_cls"]
    comp_trainer = comp_trainer_cls(
        train_config=train_config, model_name=model_name, model_output_path=config.MODEL_OUTPUT, log_output_path=config.LOG_OUTPUT
    )

    if isinstance(train_data, pd.DataFrame):
        train_df = train_data.copy()
    else:
        train_df = pd.read_csv(train_data)
    
    train_df["is_valid"] = train_df["k_fold"] == n_fold

    log_df, oof_df = comp_trainer.train(
        CFG,
        train_df,
        n_fold=n_fold,
        run_id=run_id,
        grid_id=grid_id,
        experiment_name=experiment_name,
        verbose=verbose,
    )

    oof_preds = oof_df[[col for col in oof_df.columns if col.startswith("pred")]].values
    oof_targs = oof_df[[col for col in oof_df.columns if col.startswith("targ")]].values

    score = utils.comp_metric_score(oof_preds, oof_targs)

    if verbose:
        print("--- logging results ---")

    log_df.to_csv(Path(config.LOG_OUTPUT) / str(model_name + ".csv"), index=False)
    oof_df.to_csv(Path(config.LOG_OUTPUT) / str("oof_" + model_name + ".csv"), index=False)

    if verbose:
        print(f"Fold={n_fold}, Score={score}")


# %% ../nbs/05_train.ipynb 7
if __name__ == "__main__" and utils.run_env != "local_nb":
    # instantiate argparser
    parser = argparse.ArgumentParser()

    # define args
    parser.add_argument("--experiment_name", type=str)
    parser.add_argument("--n_fold", type=int, default=0)
    parser.add_argument("--run_id", type=str, default="dummy")
    parser.add_argument("--grid_id", type=int, default=0)
    parser.add_argument("--verbose", type=str, default=True)

    # read in args from terminal
    args = parser.parse_args()

    run_fold(
        CFG=CFG,
        n_fold=args.n_fold,
        experiment_name=args.experiment_name,
        run_id=args.run_id,
        grid_id=args.grid_id,
        train_data=config.TRAINING_FILE,
        verbose=args.verbose,
    )

