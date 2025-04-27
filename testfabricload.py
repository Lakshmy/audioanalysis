import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import AzureCliCredential
import uploadtofabric

# Replace with your OneLake account details
account_name = "onelake"
account_url = f"https://{account_name}.dfs.fabric.microsoft.com"
credential = AzureCliCredential()

# Replace with your workspace and lakehouse details
workspace_name = "audioanalysis"
lakehouse_name = "callsummary.Lakehouse"
#file_system_name = f"{workspace_name}@{account_name}.dfs.fabric.microsoft.com"
file_system_name = f"{workspace_name}"
directory_name = "Files/speechfiles"  # Specify the directory within the Files section
file_name = "output.parquet"
file_path = f"{lakehouse_name}/{directory_name}"

# Sample Pandas DataFrame
data = {'col1': [1, 2], 'col2': ['a', 'b']}
df = pd.DataFrame(data)

try:
    # Create a DataLakeServiceClient
    service_client = DataLakeServiceClient(account_url, credential=credential)

    # Get a FileSystemClient for your OneLake filesystem
    file_system_client = service_client.get_file_system_client(file_system_name)#file_system_name=file_system_name)

    # Get a DirectoryClient
    directory_client = file_system_client.get_directory_client(file_path)

    # Get a FileClient
    file_client = directory_client.get_file_client(file_name)

    # Write the Pandas DataFrame to a Parquet file in memory
    parquet_buffer = df.to_parquet(engine='pyarrow', compression='snappy')

    # Upload the in-memory Parquet data to OneLake
    file_client.upload_data(parquet_buffer, overwrite=True)

    print(f"Successfully wrote Parquet file to: abfss://{file_system_name}/{file_path}")
    uploadtofabric.writetofabric(df)
except Exception as e:
    print(f"An error occurred: {e}")