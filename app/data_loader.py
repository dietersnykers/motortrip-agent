from pathlib import Path
import pandas as pd
from pandas.errors import ParserError


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def load_csv(csv_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
        print(f"[CSV] geladen met komma-separator: {csv_path}")
    except ParserError:
        print(f"[CSV] standaard komma-formaat mislukt voor {csv_path}, probeer puntkomma")
        df = pd.read_csv(csv_path, sep=";")
        print(f"[CSV] geladen met puntkomma-separator: {csv_path}")

    df = normalize_columns(df)
    print(f"[CSV] kolommen: {df.columns.tolist()}")
    return df


def get_row_for_day(df: pd.DataFrame, day_number: int):
    if "day_number" not in df.columns:
        raise KeyError(f"Kolom 'day_number' ontbreekt. Beschikbare kolommen: {df.columns.tolist()}")

    row = df[df["day_number"] == day_number]
    if row.empty:
        return None
    return row.iloc[0]


def get_day_highlights(highlights_df: pd.DataFrame, day_number: int) -> list:
    if "day_number" not in highlights_df.columns:
        raise KeyError(
            f"Kolom 'day_number' ontbreekt in highlights. Beschikbare kolommen: {highlights_df.columns.tolist()}"
        )

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