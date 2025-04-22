# Call Center Conversation Analysis

This Python program demonstrates how to use the `AzureContentUnderstandingClient` to analyze audio files . It takes an audio file (either a local path or a URL), sends it to the Azure service, polls for the results, and then prints the speech-to-text transcription and any extracted field values.
There are 3 parts to this program
1. main.py - Main file which uses the AzureContentUnderstandingClient to parse the audio file to create transcription and audio analysis
2. audit.py - This file uses the transciption from main.py to create a quality control report based 
3. uploadpdf.py- uploads the quality control report as pdf file to a storage blob container

To run the function --> Upload the audio file to a storage blob container and configure the name rest of the env variable in the .env file

Make sure that user has the following functions to upload the pdf file to storage container
- Storage Blob Data Contributor
- Storage Queue Data Contributor

## Prerequisites

Before running this program, ensure you have the following:

* **Python 3.6 or higher** installed on your system.
* **Required Python packages** installed. You can install them using pip:
    ```bash
    pip install requests
    ```
* **An Azure Content Understanding service endpoint and API version.** You can obtain these from your Azure portal.
* **Authentication credentials** for your Azure Content Understanding service. This can be either:
    * A **subscription key**.
    * An **Azure Active Directory (AAD) token**.

## Setup

1.  **Save the Python code:** Save the provided Python code as a `.py` file (e.g., `main.py`).

2.  **Configure Settings:** Open the `main.py` file and modify the `Settings` dataclass within the `main()` function with your specific details:
    * Make a copy of the .env_sample and rename it as .env file.  Edit the values of the following
    * `CONTENT_UNDERSTANDING_ENDPOINT`: Replace `<>` with your Azure Content Understanding service endpoint.
    * `CONTENT_UNDERSTANDING_API_VERSION`: Ensure `<>` matches the API version you want to use.
    **Note:** The program prioritizes the `subscription_key` if both `subscription_key` and `aad_token` are provided.
    * `CONTENT_UNDERSTANDING_SUBSCRIPTION_KEY`: Replace `<>` with your Azure Content Understanding subscription key. **Important:** If you are using an AAD token, you can leave this as is or set it to `None`.
    * `CONTENT_UNDERSTANDING_AAD_TOKEN`: If you are using an AAD token for authentication, replace `<>` with your actual AAD token. Otherwise, you can leave it as is or set it to `None`.
    * `CONTENT_UNDERSTANDING_ANALYZER_ID`: Replace `"<>"` with the name or ID of the analyzer you have deployed in your Azure Content Understanding service (e.g., `audiosummarizer`, `my-custom-analyzer`).
    * `AUDIO_FILE_LOCATION`: Update <storage_account> and <container> in `"https://<storage_account>.blob.core.windows.net/<container>/Call6_mono_16k_az_apply_loan.wav"` with the URL or the file path of the audio file you want to analyze.

## Running the Program

Once you have configured the settings, you can run the program from your terminal using the following command:


    python main.py


## audit.py

This Python script analyzes a contact center call transcript using Azure OpenAI to generate a quality assurance report. The report identifies key aspects of the call, including greeting and identification, call handling and resolution, communication skills, data protection, customer satisfaction, and handling of difficult situations. It then generates a PDF audit report and uploads it to Azure Blob Storage.

## Prerequisites

Before running this script, ensure you have the following:

* **Required Python libraries** installed. You can install them using pip:
    ```bash
    pip install openai python-dotenv reportlab azure-storage-blob
    ```
* **Environment variables** configured in a `.env` file in the same directory as the script. These variables should include your Azure OpenAI and Azure Blob Storage credentials:

    ```dotenv
    AZURE_OPENAI_ENDPOINT="YOUR_AZURE_OPENAI_ENDPOINT"
    OPENAI_MODEL_DEPLOYMENT_NAME="YOUR_DEPLOYMENT_NAME"
    AZURE_OPENAI_API_KEY="YOUR_AZURE_OPENAI_API_KEY"
    OPENAI_API_VERSION="YOUR_OPENAI_API_VERSION"
    PDF_FILE_LOCATION="./"  # Or your desired local path for PDF creation
    PDF_CONTAINER_NAME="your-blob-container-name"
    AZURE_STORAGE_CONNECTION_STRING="YOUR_AZURE_STORAGE_CONNECTION_STRING"
    ```

    **Note:** Replace the placeholder values with your actual credentials and desired settings.

## Functionality

The script performs the following actions:

1.  **Loads Environment Variables:** Reads configuration details from the `.env` file.
2.  **Initializes Azure OpenAI Client:** Authenticates with the Azure OpenAI service using the provided API key and endpoint.
3.  **Defines Chat Prompt:** Constructs a detailed prompt for the Azure OpenAI model. This prompt includes:
    * A system message defining the role of a quality control specialist for Pepper Money.
    * Specific questions to analyze non-complaint issues during the call.
    * A sample call transcript for analysis.
4.  **`createauditreport(speech)` Function:**
    * Takes an optional `speech` parameter (currently not used in the main execution but intended for potential future integration with speech-to-text).
    * Sends the defined `chat_prompt` to the Azure OpenAI model for completion.
    * Parses the JSON response to extract the generated quality assurance report.
    * Calls the `create_and_write_pdf()` function to generate a PDF report.
    * Returns the generated report content.
5.  **`create_and_write_pdf(content)` Function:**
    * Takes the generated `content` (the quality assurance report) as input.
    * Generates a unique filename for the PDF report based on the current timestamp (e.g., `audit_YYYYMMDDHHMMSS.pdf`).
    * Creates a PDF file using the `reportlab` library.
    * Writes the report content to the PDF, formatting it with line breaks.
    * Saves the PDF file locally.
    * Calls the `uploadpdf.upload_pdf_to_azure()` function (from a separate `uploadpdf.py` file, assumed to be in the same directory) to upload the generated PDF to Azure Blob Storage.
6.  **`if __name__ == "__main__":` Block:**
    * This block executes when the script is run directly.
    * Calls `createauditreport("test")` to generate the report (the "test" argument is currently not used).
    * Calls `create_and_write_pdf()` again with the generated report (this second call might be redundant as it's already called within `createauditreport`).

## Setup and Usage

1.  **Clone or download** the Python script (`call_quality_analyzer.py`) and the `uploadpdf.py` file (if you have it) to your local machine.
2.  **Create a `.env` file** in the same directory as the script and populate it with your Azure OpenAI and Azure Blob Storage credentials as described in the "Prerequisites" section.
3.  **Ensure the `uploadpdf.py` file** contains the necessary function (`upload_pdf_to_azure`) to handle the PDF upload to your Azure Blob Storage container. This file is not included in this code snippet, so you'll need to have it implemented separately.
4.  **Run the script** from your terminal:
    ```bash
    python call_quality_analyzer.py
    ```
5.  **Check the output:** The script will print messages indicating the successful creation and upload of the PDF report. You can find the generated PDF in your specified local `PDF_FILE_LOCATION` and in your Azure Blob Storage container.

## Customization

* **Modify the `chat_prompt`:** You can adjust the system message, the specific questions, and the sample call transcript in the `chat_prompt` list to analyze different aspects of call quality or different call scenarios.
* **Adjust PDF formatting:** You can customize the font, size, and layout of the generated PDF by modifying the parameters in the `create_and_write_pdf()` function.
* **Implement `uploadpdf.py`:** Ensure your `uploadpdf.py` file correctly handles the connection to Azure Blob Storage using the `AZURE_STORAGE_CONNECTION_STRING` and uploads the PDF to the specified `PDF_CONTAINER_NAME`. You might need to adapt the function based on your specific Azure Storage setup.
* **Error Handling:** The script includes basic error handling for PDF creation. You might want to add more robust error handling for API calls and file operations.
* **Dynamic Transcript Input:** Currently, the call transcript is hardcoded in the `chat_prompt`. You could modify the script to read the transcript from a file or another source, making it more versatile.

## uploadpdf.py

This Python script uploads a PDF file to Azure Blob Storage. It authenticates using Azure CLI credentials, allowing it to run in environments where you've logged in with the Azure CLI.

## Prerequisites

* **Required Python libraries** installed. You can install them using pip:
    ```bash
    pip install azure-storage-blob azure-identity python-dotenv
    ```
* **Azure CLI** installed (`pip install azure-cli`) and you are logged in to your Azure account (`az login`).
* **Environment variables** configured in a `.env` file in the same directory as the script. These variables should include:
    ```dotenv
    PDF_FILE_LOCATION="YOUR_STORAGE_ACCOUNT_URL"
    PDF_CONTAINER_NAME="your-blob-container-name"
    ```
    **Note:**
    * `YOUR_STORAGE_ACCOUNT_URL`: Replace this with the primary endpoint URL of your Azure Storage account (e.g., `https://youraccountname.blob.core.windows.net`). You can find this in the Azure portal under your Storage account's "Overview" or "Endpoints" section.
    * `your-blob-container-name`: Replace this with the name of the Azure Blob Storage container where you want to upload the PDF.

## Functionality

The script performs the following actions:

1.  **Loads Environment Variables:** Reads the Storage Account URL and Container Name from the `.env` file.
2.  **Authenticates with Azure:** Uses `AzureCliCredential` to authenticate with Azure using your logged-in Azure CLI credentials.
3.  **Creates BlobServiceClient:** Initializes a `BlobServiceClient` instance to interact with your Azure Blob Storage account.
4.  **Gets or Creates ContainerClient:** Retrieves a client for the specified container. If the container does not exist, it attempts to create it.
5.  **Constructs BlobClient:** Creates a `BlobClient` for the PDF file you intend to upload within the specified container. The blob name will be the same as the local filename.
6.  **Uploads PDF:** Opens the local PDF file in binary read mode (`"rb"`) and uploads its contents to the Azure Blob Storage blob, overwriting any existing blob with the same name.
7.  **Prints Status:** Displays messages indicating whether the upload was successful or if any errors occurred.

## Setup and Usage

1.  **Clone or download** the Python script (`uploadpdf.py`) to your local machine.
2.  **Create a `.env` file** in the same directory as the script and populate it with your Azure Storage Account URL and Container Name as described in the "Prerequisites" section.
3.  **Ensure you are logged in to your Azure account** using the Azure CLI:
    ```bash
    az login
    ```
4.  **Replace `"dummy.pdf"`** in the `if __name__ == "__main__":` block with the actual path to the PDF file you want to upload.
5.  **Run the script** from your terminal:
    ```bash
    python uploadpdf.py
    ```
6.  **Check the output:** The script will print messages indicating whether the container was created (if it didn't exist) and whether the PDF file was uploaded successfully. You can also verify the upload by checking your Azure Blob Storage container in the Azure portal.

## Testing (Optional)

The script includes a section within the `if __name__ == "__main__":` block that demonstrates how to create a simple "dummy.pdf" file using the `reportlab` library for testing purposes. If you don't have a PDF file readily available, you can run the script as is, and it will create a basic PDF and then attempt to upload it. Make sure you have `reportlab` installed (`pip install reportlab`) if you want to use this testing functionality.

## Important Notes

* **Authentication:** This script relies on Azure CLI credentials. Ensure you are logged into the correct Azure account with the necessary permissions to write to the specified Blob Storage container.
* **Error Handling:** The script includes basic error handling to catch exceptions during the upload process. You might want to enhance this further based on your specific requirements.
* **Environment Variables:** Using a `.env` file is a good practice for managing sensitive information like storage account URLs. Ensure your `.env` file is not committed to version control systems if it contains sensitive data.
* **Dependencies:** Make sure all the required Python libraries are installed before running the script.