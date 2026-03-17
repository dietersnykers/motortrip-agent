from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
csv_path = project_root / "data" / "sample" / "hotels_example.csv"

print(f"CSV pad: {csv_path}")

df = pd.read_csv(csv_path)

print("Hotels in je trip:\n")

for _, row in df.iterrows():
    print(f"Dag {row['day_number']}: {row['hotel_name']} in {row['city']}")