import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from dataclasses import dataclass

pseudo_ids = ["asin_1", "asin_2", "asin_3", "asin_4"]
pseudo_cols = [
    "emotion_1",
    "emotion_2",
    "emotion_3",
    "emotion_4",
    "emotion_5",
    "emotion_6",
    "emotion_7",
]
values = np.random.randn(4, 7)
table = pd.DataFrame(pseudo_ids, columns=["id"]).join(
    pd.DataFrame(values, columns=pseudo_cols)
)
print(table.head())
subset = table[pseudo_cols]
table.drop(pseudo_cols, inplace=True, axis=1)
print(subset.head())
pca = PCA(n_components=4).fit(subset)
df = pd.DataFrame(
    data=pca.transform(subset),
    columns=["vec_d1", "vec_d2", "vec_d3", "vec_d4"],
)
print(df.head())
df2 = table.join(df)
table.drop(table.columns, inplace=True, axis=1)
df.drop(df.columns, inplace=True, axis=1)
print(table.head())
print(df.head())
print(df2.head())


@dataclass
class Structure:
    id: str
    vec_d1: float
    vec_d2: float
    vec_d3: float
    vec_d4: float


for _, *data in df2.itertuples():
    print(Structure(*data))
