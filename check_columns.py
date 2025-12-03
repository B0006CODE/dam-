import pandas as pd

df = pd.read_excel('水库信息.xlsx')
print('Actual columns:')
for i, col in enumerate(df.columns):
    print(f'{i}: {repr(col)}')
