"""Демо-данные и импорты для code.ipynb (можно вызывать из любой ячейки)."""
from __future__ import annotations

import tempfile
import warnings
from pathlib import Path
from typing import Any


def ensure_viz_context(g: dict[str, Any]) -> None:
    """Импорты + df, train, clf, … в namespace ячейки (идемпотентно)."""
    if g.get("_viz_demo_ready"):
        return

    warnings.filterwarnings("ignore", category=FutureWarning)

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from scipy import stats
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs, make_classification
    from sklearn.decomposition import PCA
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import DecisionBoundaryDisplay, permutation_importance
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.manifold import TSNE
    from sklearn.metrics import (
        ConfusionMatrixDisplay,
        PrecisionRecallDisplay,
        RocCurveDisplay,
        mean_squared_error,
        precision_recall_curve,
        r2_score,
        roc_curve,
        silhouette_score,
    )
    from sklearn.model_selection import GridSearchCV, LearningCurveDisplay, cross_val_score, train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    try:
        import plotly.express as px
    except ImportError:
        px = None

    try:
        import missingno as msno
    except ImportError:
        msno = None

    np.random.seed(42)
    rng = np.random.default_rng(42)
    n = 240
    cities = rng.choice(["Москва", "СПб", "Казань"], n, p=[0.45, 0.35, 0.20])
    area = rng.uniform(30, 120, n)
    price = 2.8 * area + np.where(
        cities == "Москва", 400, np.where(cities == "СПб", 250, 100)
    )
    price += rng.normal(0, 45, n)
    income = np.where(
        cities == "Москва",
        rng.normal(120, 25, n),
        np.where(cities == "СПб", rng.normal(85, 18, n), rng.normal(55, 12, n)),
    )
    df = pd.DataFrame(
        {
            "area": area,
            "price": price,
            "city": cities,
            "income": income,
            "category": rng.choice(["A", "B", "C"], n),
            "segment": rng.choice(["std", "vip"], n, p=[0.7, 0.3]),
            "target": rng.integers(0, 2, n),
            "id": np.arange(n),
            "x": rng.normal(0, 1, n),
            "y": rng.normal(0, 1, n),
            "z": rng.normal(0, 1, n),
            "year": rng.integers(2018, 2024, n),
            "value": rng.normal(50, 15, n),
        }
    )
    df.loc[rng.choice(n, 20, replace=False), "income"] = np.nan

    train = df.sample(frac=0.7, random_state=42)
    test = df.drop(train.index)
    train_df = pd.concat(
        [train.assign(dataset="train"), test.assign(dataset="test")],
        ignore_index=True,
    )
    train_arr = train["income"].dropna().to_numpy()
    test_arr = test["income"].dropna().to_numpy()
    train_scores = np.linspace(0.55, 0.92, 10)
    val_scores = np.linspace(0.52, 0.78, 10)

    X_clf, y_clf = make_classification(
        n_samples=200, n_features=2, n_redundant=0, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X_clf, y_clf, test_size=0.3, random_state=42, stratify=y_clf
    )
    clf = make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=500, random_state=42)
    )
    clf.fit(X_train, y_train)
    model = clf

    x_reg = np.linspace(0, 10, 120).reshape(-1, 1)
    y_reg = 2.2 * x_reg.ravel() + rng.normal(0, 1.8, 120)
    reg = LinearRegression().fit(x_reg, y_reg)
    y_true = y_reg
    y_pred = reg.predict(x_reg)
    residuals = y_true - y_pred
    r2 = r2_score(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))

    proba = clf.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, proba)
    prec, rec, _ = precision_recall_curve(y_test, proba)

    cv_scores = pd.DataFrame(
        {
            "fold": [f"fold{i}" for i in range(5)],
            "score": cross_val_score(clf, X_clf, y_clf, cv=5),
        }
    )

    param_grid = {"max_depth": [2, 4, 6, 8], "min_samples_leaf": [1, 2, 4]}
    gs = GridSearchCV(
        DecisionTreeClassifier(random_state=42),
        param_grid,
        cv=3,
        scoring="accuracy",
        return_train_score=False,
    )
    gs.fit(X_train, y_train)
    grid_arr = gs.cv_results_["mean_test_score"].reshape(
        len(param_grid["max_depth"]), len(param_grid["min_samples_leaf"])
    )
    grid_results = pd.DataFrame(
        grid_arr,
        index=param_grid["max_depth"],
        columns=param_grid["min_samples_leaf"],
    )

    rf = RandomForestClassifier(n_estimators=80, random_state=42)
    rf.fit(X_train, y_train)
    perm = permutation_importance(rf, X_test, y_test, n_repeats=8, random_state=42)
    feature_names = [f"f{i}" for i in range(X_clf.shape[1])]
    perm_std = perm.importances_std
    perm_y = np.arange(len(feature_names))
    perm_x = perm.importances_mean

    pca = PCA(n_components=3, random_state=42).fit_transform(
        np.c_[X_clf, rng.normal(0, 0.3, (len(X_clf), 1))]
    )

    g.update(
        {
            "plt": plt,
            "np": np,
            "pd": pd,
            "sns": sns,
            "stats": stats,
            "px": px,
            "msno": msno,
            "df": df,
            "train": train,
            "test": test,
            "train_df": train_df,
            "train_arr": train_arr,
            "test_arr": test_arr,
            "train_scores": train_scores,
            "val_scores": val_scores,
            "X_clf": X_clf,
            "y_clf": y_clf,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "clf": clf,
            "model": model,
            "reg": reg,
            "y_true": y_true,
            "y_pred": y_pred,
            "residuals": residuals,
            "r2": r2,
            "rmse": rmse,
            "proba": proba,
            "fpr": fpr,
            "tpr": tpr,
            "prec": prec,
            "rec": rec,
            "cv_scores": cv_scores,
            "grid_results": grid_results,
            "result": perm,
            "perm_std": perm_std,
            "perm_y": perm_y,
            "perm_x": perm_x,
            "feature_names": feature_names,
            "pca": pca,
            "rng": rng,
            "make_blobs": make_blobs,
            "KMeans": KMeans,
            "silhouette_score": silhouette_score,
            "DecisionBoundaryDisplay": DecisionBoundaryDisplay,
            "ConfusionMatrixDisplay": ConfusionMatrixDisplay,
            "RocCurveDisplay": RocCurveDisplay,
            "PrecisionRecallDisplay": PrecisionRecallDisplay,
            "LearningCurveDisplay": LearningCurveDisplay,
            "DecisionTreeClassifier": DecisionTreeClassifier,
            "TSNE": TSNE,
            "PCA": PCA,
            "_OUT": Path(tempfile.mkdtemp()),
            "_viz_demo_ready": True,
        }
    )
