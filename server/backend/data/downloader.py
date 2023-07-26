from azure.storage.blob import BlobServiceClient
import os

SAS_URL = os.getenv("SAS_URL")
SAS_TOKEN = os.getenv("SAS_TOKEN")
container_name = "source-files"

blob_service_client = BlobServiceClient(account_url=f"{SAS_URL}?{SAS_TOKEN}")

container_client = blob_service_client.get_container_client(container_name)
blobs = container_client.list_blobs()

target_directory = "./blobs/"
os.makedirs(target_directory, exist_ok=True)

existing_files = os.listdir(target_directory)

counter = 1
import time

start_time = time.time()
for blob in blobs:
    blob_start = time.time()
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob.name
    )

    # Replace slashes or backslashes with underscores to ensure it's a valid file name.
    blob_name = blob.name.replace("/", "").replace("\\", "_")
    unique_filename = f"{counter}{blob_name}" 
    counter += 1
    if any(blob_name in filename for filename in existing_files):
        continue
    local_file_path = os.path.join(target_directory, unique_filename)

    with open(local_file_path, "wb") as local_file:
        blob_data = blob_client.download_blob()
        local_file.write(blob_data.readall())

    print(f"Blob '{blob.name}' downloaded to: {local_file_path}")
    print(f"took: {time.time() - blob_start}")
print(f"total time elapsed: {time.time() - start_time}")
