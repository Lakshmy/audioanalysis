import os
import uuid
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobBlock, BlobClient, StandardBlobTier
from dotenv import load_dotenv
load_dotenv()  

def upload_pdf_to_azure(local_file_path):
    """
    Uploads a PDF file to Azure Blob Storage.

    Args:
        storage_account_name (str): The name of your Azure Storage account.
        container_name (str): The name of the container where you want to upload the PDF.
        local_file_path (str): The path to the PDF file on your local system.
    """
    try:
        # Use DefaultAzureCredential for authentication.  This works in Azure environments
        # and can also work locally if you've configured your development environment
        # with the Azure CLI or PowerShell.  For local development, you may need to
        # install the azure-cli: `pip install azure-cli` and then login using `az login`.
        #credential = DefaultAzureCredential()
        credential = AzureCliCredential()
        # Construct the full URL to your storage account.
        account_url = os.getenv("PDF_FILE_LOCATION") 

        # Create a BlobServiceClient using the credential.
        blob_service_client = BlobServiceClient(account_url, credential=credential)

        # Get a client for the container.  This will create the container if it does not exist.
        container_name = os.getenv("PDF_CONTAINER_NAME") 
        container_client = blob_service_client.get_container_client(container_name)
        try:
            container_client.create_container()
            print(f"Container '{container_name}' created successfully.")
        except:
            print(f"Container '{container_name}' already exists.")

        # Get the name of the PDF file from the local path.
        blob_name = os.path.basename(local_file_path)

        # Create a BlobClient for the specific PDF file.
        blob_client = container_client.get_blob_client(blob=blob_name)

        # Upload the PDF file.
        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)  # overwrite if it exists

        print(f"Uploaded '{blob_name}' to '{container_name}' in storage account '{account_url}'.")

    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return False  # Indicate failure
    return True # Indicate success


if __name__ == "__main__":
    local_file_path = "dummy.pdf"  #  Replace with the actual path to your PDF file

    # Create a dummy pdf for testing
    from reportlab.pdfgen import canvas
    canvas_path = "dummy.pdf"
    c = canvas.Canvas(canvas_path)
    c.drawString(100,750,"Hello World")
    c.save()
    local_file_path = canvas_path # change the local file path to the dummy pdf

    # Call the function to upload the PDF.
    upload_successful = upload_pdf_to_azure(local_file_path)

    if upload_successful:
        print("PDF upload process completed.")
    else:
        print("PDF upload process failed.")
