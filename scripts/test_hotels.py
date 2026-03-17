import pandas as pd

df = pd.read_csv("data/sample/hotels_example.csv")

print("Hotels in je trip:\n")

for _, row in df.iterrows():
    print(f"Dag {row['day_number']}: {row['hotel_name']} in {row['city']}")