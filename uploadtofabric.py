import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import AzureCliCredential
import datetime
import os
from dotenv import load_dotenv

def writetofabric(dataframe):
    load_dotenv()
    # Replace with your OneLake account details
    account_name = os.getenv("ACCOUNT_NAME")
    account_url = f"https://{account_name}.dfs.fabric.microsoft.com"
    credential = AzureCliCredential()

    # Replace with your workspace and lakehouse details
    workspace_name = os.getenv("WORKSPACE_NAME")
    lakehouse_name = os.getenv("LAKEHOUSE_NAME")
    file_system_name = f"{workspace_name}"

    # Specify the directory within the Files section
    directory_name =os.getenv("DIRECTORY_NAME")
    file_path = f"{lakehouse_name}/{directory_name}"
    
    # Construct the filename.
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"audioinsights_{timestamp}.parquet"  

    try:
        # Create a DataLakeServiceClient
        service_client = DataLakeServiceClient(account_url, credential=credential)

        # Get a FileSystemClient for your OneLake filesystem
        file_system_client = service_client.get_file_system_client(file_system_name)

        # Get a DirectoryClient
        directory_client = file_system_client.get_directory_client(file_path)

        # Get a FileClient
        file_client = directory_client.get_file_client(filename)

        # Write the Pandas DataFrame to a Parquet file in memory
        parquet_buffer = dataframe.to_parquet(engine='pyarrow', compression='snappy')

        # Upload the in-memory Parquet data to OneLake
        file_client.upload_data(parquet_buffer, overwrite=True)

        print(f"Successfully wrote Parquet file {filename} to: abfss://{file_system_name}/{file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")