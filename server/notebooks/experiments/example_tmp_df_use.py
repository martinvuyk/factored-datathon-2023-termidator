from utils import json_gz_to_df
import os

root_dir = "../../backend/data/blobs"
partitions = [filename for filename in os.listdir(root_dir) if ".json.gz" in filename]
print(partitions)
df = json_gz_to_df(f"{root_dir}/{partitions[0]}")
print("dataset cols:\n")
print(df.columns)
print(df.shape)
