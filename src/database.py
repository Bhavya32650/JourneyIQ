
import sqlite3
from pathlib import Path
import pandas as pd


def load_csvs_to_sqlite(
    data_dir="data/raw/starter",
    db_path="data/journeyiq.db"
):
    Path(db_path).parent.mkdir(
        parents=True, exist_ok=True
    )

    conn = sqlite3.connect(db_path)

    try:
        conn.execute("PRAGMA foreign_keys = ON")

        folder = Path(data_dir)

        for file in folder.glob("*.csv"):
            try:
                df = pd.read_csv(file)
            except pd.errors.EmptyDataError:
                continue

            table_name = file.stem

            df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False,
                chunksize=10000
            )

            print(f"Loaded: {table_name}")

    finally:
        conn.close()

    print("Database created successfully!")


if __name__ == "__main__":
    load_csvs_to_sqlite()
