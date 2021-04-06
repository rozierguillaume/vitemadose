import pandas as pd
from pathlib import Path

df = pd.read_csv(
    Path("data/input/centres-vaccination.csv"), sep=";", dtype={"com_cp": "object"}
)
print(df.com_cp)
df_dep = df[df.com_cp.str.match(r"(^{}.*)".format("01")) == True]
print(df_dep)
