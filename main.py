import model
import pandas as pd

model.create_tables()
model.fill_values()
model.conn.commit()
# print(model.find_tournament_tags(1))
tournaments = model.find_tournaments()
print(tournaments)