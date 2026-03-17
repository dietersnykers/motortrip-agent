from pathlib import Path
import pandas as pd


def load_csv(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def get_row_for_day(df: pd.DataFrame, day_number: int):
    row = df[df["day_number"] == day_number]
    if row.empty:
        return None
    return row.iloc[0]


def get_day_highlights(highlights_df: pd.DataFrame, day_number: int) -> list:
    day_rows = highlights_df[highlights_df["day_number"] == day_number]
    highlights = []

    for _, row in day_rows.iterrows():
        highlights.append(
            {
                "name": row["name"],
                "type": row["type"],
                "description": row["description"],
            }
        )

    return highlights