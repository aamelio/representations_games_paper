#!/usr/bin/env python3
"""Normalize round-6 similarity ratings and make the requested grouped plots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
GAME_ORDER = ["DG", "UG", "TG"]
CATEGORY_ORDER = ["Moral", "Self-interest", "Cooperation"]
CATEGORY_SHORT = {"Moral": "M", "Self-interest": "S", "Cooperation": "C"}
SETTING_ORDER = ["P", "K"]
SETTING_LABEL = {"P": "Personal", "K": "Anonymous market"}
CATEGORY_COLOR = {"Moral": "#4C78A8", "Self-interest": "#E45756", "Cooperation": "#54A24B"}
SETTING_HATCH = {"P": "", "K": "//"}


def load_inputs(ratings_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ratings = pd.read_csv(ratings_path)
    mapping = json.loads((HERE / "anonymization_map.json").read_text(encoding="utf-8"))
    vignette_map = pd.DataFrame.from_dict(mapping["vignettes"], orient="index").rename_axis("vignette_id").reset_index()
    context_map = pd.DataFrame.from_dict(mapping["contexts"], orient="index").rename_axis("context_id").reset_index()
    required = {
        "provider",
        "model",
        "replicate",
        "context_id",
        "vignette_id",
        "rating",
    }
    missing = sorted(required.difference(ratings.columns))
    if missing:
        raise ValueError(f"Ratings file is missing columns: {missing}")
    ratings["rating"] = pd.to_numeric(ratings["rating"], errors="raise")
    if not ratings["rating"].between(0, 100).all():
        raise ValueError("Ratings must all lie in [0, 100]")
    if ratings.duplicated(["provider", "model", "replicate", "context_id", "vignette_id"]).any():
        raise ValueError("Duplicate provider-model-replicate-context-vignette rows found")
    unknown_contexts = sorted(set(ratings["context_id"]).difference(context_map["context_id"]))
    unknown_vignettes = sorted(set(ratings["vignette_id"]).difference(vignette_map["vignette_id"]))
    if unknown_contexts or unknown_vignettes:
        raise ValueError(
            f"Ratings contain identifiers absent from the private map: "
            f"contexts={unknown_contexts}, vignettes={unknown_vignettes}"
        )
    return ratings, vignette_map, context_map


def validate_coverage(ratings: pd.DataFrame, context_map: pd.DataFrame) -> None:
    counts = ratings.groupby(["provider", "model", "replicate", "context_id"]).size()
    if not (counts == 30).all():
        raise ValueError(f"Every completed rating unit must contain 30 scores; bad counts:\n{counts[counts != 30]}")
    expected_contexts = set(context_map["context_id"])
    for (provider, model, replicate), part in ratings.groupby(["provider", "model", "replicate"]):
        observed = set(part["context_id"])
        if observed != expected_contexts:
            raise ValueError(
                f"Incomplete context coverage for {(provider, model, replicate)}: "
                f"missing={sorted(expected_contexts - observed)}"
            )


def compute_weights(
    ratings: pd.DataFrame, vignette_map: pd.DataFrame, context_map: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Normalize each independent repetition first. This avoids giving a run with
    # a higher overall use of the rating scale greater weight in the average.
    raw = ratings.merge(context_map, on="context_id", validate="many_to_one").merge(
        vignette_map, on="vignette_id", validate="many_to_one", suffixes=("_context", "_vignette")
    )
    unit = ["provider", "model", "replicate", "context_id"]
    raw["weight_all30"] = raw["rating"] / raw.groupby(unit)["rating"].transform("sum")
    raw["matching_game"] = raw["game_context"] == raw["game_vignette"]
    raw["weight_within_game"] = np.nan
    matching = raw["matching_game"]
    within_totals = raw.loc[matching].groupby(unit)["rating"].transform("sum")
    if (within_totals <= 0).any():
        raise ValueError("At least one within-game similarity total is zero")
    raw.loc[matching, "weight_within_game"] = raw.loc[matching, "rating"] / within_totals

    # Average repetitions within model, and then weight provider-models equally.
    value_columns = ["rating", "weight_all30", "weight_within_game"]
    by_model = (
        raw.groupby(["provider", "model", "context_id", "vignette_id"], as_index=False, dropna=False)[value_columns]
        .mean()
        .rename(columns={"rating": "model_mean_rating"})
    )
    means = (
        by_model.groupby(["context_id", "vignette_id"], as_index=False, dropna=False)[
            ["model_mean_rating", "weight_all30", "weight_within_game"]
        ]
        .mean()
        .rename(columns={"model_mean_rating": "mean_rating"})
    )
    full = means.merge(context_map, on="context_id", validate="many_to_one").merge(
        vignette_map, on="vignette_id", validate="many_to_one", suffixes=("_context", "_vignette")
    )
    full["matching_game"] = full["game_context"] == full["game_vignette"]
    plot_values = full.loc[full["matching_game"]].copy()
    checks = plot_values.groupby("context_id")["weight_within_game"].sum()
    if not np.allclose(checks.to_numpy(), 1.0):
        raise AssertionError(f"Within-game weights do not sum to one:\n{checks}")
    return full, plot_values


def block_label(row: pd.Series) -> str:
    category = CATEGORY_SHORT[row["sender_category"]]
    if row["game_context"] == "DG":
        return category
    return f"{category}–{row['receiver_action']}"


def ordered_panel(frame: pd.DataFrame, game: str) -> pd.DataFrame:
    subset = frame.loc[frame["game_context"] == game].copy()
    subset["category_order"] = subset["sender_category"].map({name: i for i, name in enumerate(CATEGORY_ORDER)})
    subset["receiver_order"] = subset["receiver_action"].map({"None": 0, "C": 0, "D": 1}).fillna(0)
    subset["setting_order"] = subset["setting_code"].map({name: i for i, name in enumerate(SETTING_ORDER)})
    subset["block"] = subset.apply(block_label, axis=1)
    return subset.sort_values(["category_order", "receiver_order", "setting_order"])


def bar_positions(panel: pd.DataFrame) -> tuple[np.ndarray, list[float], list[str]]:
    positions: list[float] = []
    centers: list[float] = []
    labels: list[str] = []
    cursor = 0.0
    for block, group in panel.groupby("block", sort=False):
        block_positions = [cursor + index for index in range(len(group))]
        positions.extend(block_positions)
        centers.append(float(np.mean(block_positions)))
        labels.append(block)
        cursor += len(group) + 0.8
    return np.asarray(positions), centers, labels


def draw_panel(ax, panel: pd.DataFrame, value_column: str, game: str, difference: bool) -> None:
    positions, centers, labels = bar_positions(panel)
    values = panel[value_column].to_numpy() * 100
    colors = [CATEGORY_COLOR[category] for category in panel["sender_category"]]
    bars = ax.bar(positions, values, color=colors, edgecolor="#333333", linewidth=0.5, width=0.78)
    for bar, setting_code in zip(bars, panel["setting_code"]):
        bar.set_hatch(SETTING_HATCH[setting_code])
    if difference:
        ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set_xticks(centers, labels)
    ax.set_title(game, loc="left", fontweight="bold")
    ax.set_ylabel("Percentage points" if difference else "Normalized similarity (%)")
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    for position, value, (_, row) in zip(positions, values, panel.iterrows()):
        ax.text(
            position,
            value,
            f"{row['setting_code']}\n{row['vignette_id']}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=7,
        )


def make_figure(
    plot_values: pd.DataFrame,
    kind: str,
    weight_column: str,
    normalization_label: str,
    output_path: Path,
) -> None:
    titles = {
        "control": "Control: normalized similarity distribution",
        "market_control": "Market minus Control: change in normalized similarity",
        "aid_bonus": "Aid minus Bonus: change in normalized similarity",
    }
    fig, axes = plt.subplots(3, 1, figsize=(13, 13))

    if kind == "control":
        data = plot_values.loc[plot_values["frame"] == "Control"].copy()
        value_column = weight_column
        difference = False
    else:
        pair = ("Market", "Control") if kind == "market_control" else ("Aid", "Bonus")
        index_columns = [
            "game_context",
            "vignette_id",
            "setting_code",
            "sender_category",
            "receiver_action",
        ]
        wide = plot_values.pivot(index=index_columns, columns="frame", values=weight_column).reset_index()
        wide["difference"] = wide[pair[0]] - wide[pair[1]]
        data = wide
        value_column = "difference"
        difference = True

    for ax, game in zip(axes, GAME_ORDER):
        panel = ordered_panel(data, game)
        draw_panel(ax, panel, value_column, game, difference)
    maximum = max(abs(data[value_column].min()), abs(data[value_column].max())) * 100
    if difference:
        limit = maximum * 1.20 if maximum else 1
        for ax in axes:
            ax.set_ylim(-limit, limit)
    else:
        limit = maximum * 1.20 if maximum else 1
        for ax in axes:
            ax.set_ylim(0, limit)
    axes[-1].set_xlabel("Representation block (bar labels: P = personal, K = anonymous market)")
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor="#D9D9D9", edgecolor="#333333", hatch=SETTING_HATCH[code])
        for code in SETTING_ORDER
    ]
    fig.legend(
        handles,
        [SETTING_LABEL[code] for code in SETTING_ORDER],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.955),
        ncol=2,
    )
    fig.suptitle(f"{titles[kind]} ({normalization_label})", fontsize=15, y=0.992)
    fig.tight_layout(rect=(0, 0, 1, 0.925), h_pad=2.0)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", type=Path, default=HERE / "similarity_ratings.csv")
    parser.add_argument("--output-dir", type=Path, default=HERE / "output")
    parser.add_argument("--skip-coverage-check", action="store_true", help="Only for synthetic testing")
    args = parser.parse_args()

    ratings, vignette_map, context_map = load_inputs(args.ratings)
    if not args.skip_coverage_check:
        validate_coverage(ratings, context_map)
    full, plot_values = compute_weights(ratings, vignette_map, context_map)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    full.to_csv(args.output_dir / "similarity_normalized_all_vignettes.csv", index=False)
    family_shares = (
        full.groupby(
            ["context_id", "source_id_context", "game_context", "frame", "game_vignette"],
            as_index=False,
        )["weight_all30"]
        .sum()
        .rename(columns={"game_vignette": "vignette_family", "weight_all30": "family_weight_all30"})
    )
    family_shares.to_csv(args.output_dir / "structural_family_shares.csv", index=False)

    control = plot_values.loc[plot_values["frame"] == "Control"].copy()
    comparisons = []
    for label, first, second in [
        ("Market-Control", "Market", "Control"),
        ("Aid-Bonus", "Aid", "Bonus"),
    ]:
        index_columns = [
            "game_context",
            "vignette_id",
            "source_id_vignette",
            "setting_code",
            "sender_category",
            "receiver_action",
            "joint_action",
        ]
        wide = plot_values.pivot(
            index=index_columns,
            columns="frame",
            values=["weight_all30", "weight_within_game", "mean_rating"],
        ).reset_index()
        wide.columns = [
            column if isinstance(column, str) else "_".join(str(part) for part in column if part)
            for column in wide.columns
        ]
        wide["comparison"] = label
        wide["difference_all30"] = wide[f"weight_all30_{first}"] - wide[f"weight_all30_{second}"]
        wide["difference_within_game"] = (
            wide[f"weight_within_game_{first}"] - wide[f"weight_within_game_{second}"]
        )
        wide["raw_rating_difference"] = wide[f"mean_rating_{first}"] - wide[f"mean_rating_{second}"]
        comparisons.append(wide)
    comparison_values = pd.concat(comparisons, ignore_index=True)
    control.to_csv(args.output_dir / "control_plot_values.csv", index=False)
    comparison_values.to_csv(args.output_dir / "difference_plot_values.csv", index=False)

    # Primary figures follow the literal "total similarity" instruction: each
    # score is divided by the total across all 30 vignettes. The bars shown for
    # a game therefore sum to that vignette family's all-30 similarity share.
    make_figure(
        plot_values,
        "control",
        "weight_all30",
        "all 30 vignettes",
        args.output_dir / "control_similarity_distribution.png",
    )
    make_figure(
        plot_values,
        "market_control",
        "weight_all30",
        "all 30 vignettes",
        args.output_dir / "market_minus_control_similarity_differences.png",
    )
    make_figure(
        plot_values,
        "aid_bonus",
        "weight_all30",
        "all 30 vignettes",
        args.output_dir / "aid_minus_bonus_similarity_differences.png",
    )

    # Conditional versions separate the within-family composition from shifts
    # in total similarity mass assigned to the DG/UG/TG family.
    make_figure(
        plot_values,
        "control",
        "weight_within_game",
        "conditional within game family",
        args.output_dir / "control_similarity_distribution_within_game.png",
    )
    make_figure(
        plot_values,
        "market_control",
        "weight_within_game",
        "conditional within game family",
        args.output_dir / "market_minus_control_similarity_differences_within_game.png",
    )
    make_figure(
        plot_values,
        "aid_bonus",
        "weight_within_game",
        "conditional within game family",
        args.output_dir / "aid_minus_bonus_similarity_differences_within_game.png",
    )
    print(f"Wrote normalized data and six figures to {args.output_dir}")


if __name__ == "__main__":
    main()
