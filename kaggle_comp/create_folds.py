# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_create_folds.ipynb.

# %% auto 0
__all__ = ['build_folds']

# %% ../nbs/03_create_folds.ipynb 3
import argparse
from pathlib import Path

import pandas as pd
from sklearn import model_selection
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold

from . import utils, config, preprocessing
from .config import CFG


# %% ../nbs/03_create_folds.ipynb 6
def build_folds(
    n_folds: int = CFG.n_fold,
    seed: int = CFG.random_seed,
    subset: float =CFG.subset,
    #strat_feat=CFG.strat_feat,
    preprocess: str = CFG.preprocess,
    save_file: bool = True,
    return_file: bool = False,
    ds: str = "train",
    save_pre: bool = False,
    return_pre: bool = True
):
    _, raw_data_path, clean_data_path, *_ = utils.get_paths()

    train_df = pd.read_csv(raw_data_path / "train.csv")

    target_cols = [x for x in train_df.columns if x not in ['text_id', 'full_text']]

    train_df = preprocessing.preprocess_data(ds = ds, preprocess = preprocess, save_file = save_pre, return_file = return_pre)

    train_df["k_fold"] = -1

    # shuffle dataset - optional subset for faster iteration
    train_df = train_df.sample(frac=subset, random_state=seed).reset_index(drop=True)

    skf = MultilabelStratifiedKFold(n_splits=5, shuffle=True, random_state=4321)

    for fold, (_, val_index) in enumerate(skf.split(X = train_df, y = train_df[target_cols])):
        train_df.loc[val_index, 'k_fold'] = fold
    train_df['k_fold'] = train_df['k_fold'].astype(int)
    
    if save_file:
        train_df.to_csv(config.TRAINING_FILE, index=False)

    if return_file:
        return train_df


# %% ../nbs/03_create_folds.ipynb 12
if __name__ == "__main__" and utils.run_env != "local_nb":
    # instantiate argparser
    parser = argparse.ArgumentParser()

    # define args
    parser.add_argument("--n_folds", type=int, default=CFG.n_fold)
    parser.add_argument("--seed", type=int, default=CFG.random_seed)
    parser.add_argument("--subset", type=float, default=CFG.subset)
    #parser.add_argument("--strat_feat", type=str, default=CFG.strat_feat)
    parser.add_argument("--preprocess", type=str, default=CFG.preprocess)
    args = parser.parse_args()

    build_folds(
        n_folds=args.n_folds,
        seed=args.seed,
        subset=args.subset,
        #strat_feat=args.strat_feat,
        preprocess=args.preprocess,
        save_file=True,
        return_file=False,
    )
