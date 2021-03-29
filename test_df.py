import pandas as pd

df = pd.read_csv('data/input/centres-vaccination.csv', sep=';', dtype={'com_cp': 'object'})
print(df.com_cp)
df_dep = df[df.com_cp.str.match(r'(^{}.*)'.format("01"))==True]
print(df_dep)