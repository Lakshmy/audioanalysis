
import os  
import base64
import json
import datetime
import uuid
import uploadpdf
from openai import AzureOpenAI  
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobBlock, BlobClient, StandardBlobTier

load_dotenv()   
     
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("OPENAI_MODEL_DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "REPLACE_WITH_YOUR_KEY_VALUE_HERE")  
aoi_api_version= os.getenv("OPENAI_API_VERSION")     
pdf_file_path = os.getenv("PDF_FILE_LOCATION")    
pdf_container = os.getenv("PDF_CONTAINER_NAME")  

# Initialize Azure OpenAI Service client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version=aoi_api_version,
)

#Prepare the chat prompt 
chat_prompt = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": "You are a quality control specialist for contact center at a financial company named Pepper Money. Your role is to analyse the conversation between agents and customers and call out any issues related to the quality of the call. Use these questions to specifically answer any non-complaint issues during the conversation\nGive the answer to the following questions with relevant section headlines, followed by question and answers\n\t\nGreeting and Identification:\n\t• What is the name of the agent who attended the call? \n\t• How long was the meeting? \n\t• Did the agent greet the customer appropriately and professionally?\n\t• Did the agent verify the customer's identity according to the company's security protocols?\n\t\nCall Handling and Resolution:\n\t• Did the agent listen actively and empathetically to the customer's concerns?\n\t• Was the agent able to resolve the customer's issue or provide a clear path to resolution?\n\t• Did the agent follow the correct procedures for handling the specific type of enquiry or complaint?\n\t\nCommunication Skills:\n\t• Did the agent communicate clearly and effectively, avoiding jargon and ensuring the customer understood the information provided?\n\t• Was the agent polite, respectful, and patient throughout the call?\n\nData Protection and Privacy:\n\t• Did the agent comply with all relevant regulatory requirements during the call (e.g., responsible lending practices, disclosure of terms and conditions)?\n\t• Were any sensitive details discussed securely, and was the customer advised not to share sensitive information via insecure channels?\n\t\nCustomer Satisfaction and Feedback:\n\t• Did the agent ask if there was anything else they could assist the customer with before ending the call?\n\t• Was the customer given an opportunity to provide feedback on their experience?\n\t• Were any follow-up actions clearly communicated to the customer?\n\nHandling Difficult Situations:\n\t• Were there any hardship issues during the meeting? \n\t• How did the agent handle situation where the customer was upset or frustrated?\n\t• Was the agent able to provide accurate and helpful information about the products or services in question?\n\t\n\nHere is the transcript of the conversation -\n00:00.960 --> 00:01.600\n<v Agent>Good afternoon.\n00:01.600 --> 00:02.240\n<v Agent>This is Sam.\n00:02.240 --> 00:03.280\n<v Agent>Thank you for calling Contoso.\n00:03.280 --> 00:03.920\n<v Agent>How can I help?\n00:05.040 --> 00:05.440\n<v Customer>Hi there.\n00:05.440 --> 00:06.240\n<v Customer>My name is Mary.\n00:06.240 --> 00:09.280\n<v Customer>I'm currently living in Los Angeles, but I'm planning to move to Las Vegas.\n00:09.280 --> 00:10.560\n<v Customer>I would like to apply for a loan.\n00:12.680 --> 00:12.880\n<v Agent>Okay.\n00:13.120 --> 00:14.880\n<v Agent>I see you're currently living in California.\n00:14.960 --> 00:16.640\n<v Agent>Let me make sure I understand you correctly.\n00:17.160 --> 00:20.200\n<v Agent>You'd like to apply for a loan, even though you'll be moving soon, is that right?\n00:21.440 --> 00:22.320\n<v Customer>Yes, exactly.\n00:22.560 --> 00:27.280\n<v Customer>So I'm planning to relocate soon, but I would like to apply for the loan first so that I can purchase a new home once I move there.\n00:28.880 --> 00:30.800\n<v Agent>And are you planning to sell your current home?\n00:32.000 --> 00:35.440\n<v Customer>Yes, I will be listing it on the market soon and hopefully it'll sell quickly.\n00:35.760 --> 00:41.120\n<v Customer>That's why I'm applying for a loan now so that I can purchase a new house in Nevada and close on it quickly as well once my current home sells.\n00:42.560 --> 00:42.880\n<v Agent>I see.\n00:43.680 --> 00:46.240\n<v Agent>Would you mind holding for a moment while I take your information down?\n00:47.200 --> 00:47.920\n<v Customer>Yeah, no problem.\n00:47.920 --> 00:48.640\n<v Customer>Thank you for your help.\n00:50.200 --> 00:51.080\n<v Agent>Just one moment.\n00:58.720 --> 01:00.360\n<v Agent>All right, thank you for your patience, ma'am.\n01:00.400 --> 01:02.400\n<v Agent>May I have your first and last name, please?\n01:03.520 --> 01:05.360\n<v Customer>Yes, my name is Mary Smith.\n01:07.520 --> 01:08.200\n<v Agent>Thank you, Ms.\n01:08.200 --> 01:08.560\n<v Agent>Smith.\n01:08.880 --> 01:10.320\n<v Agent>May I have your current address, please?\n01:11.440 --> 01:18.560\n<v Customer>Yes, so my address is 123 Main Street in Los Angeles, California, and the zip code is 90923.\n01:20.480 --> 01:22.640\n<v Agent>Sorry, that was a 90 what?\n01:24.160 --> 01:26.080\n<v Customer>90923.\n01:27.600 --> 01:30.800\n<v Agent>Nine zero nine two three on Main Street.\n01:30.800 --> 01:31.200\n<v Agent>Got it.\n01:31.480 --> 01:32.000\n<v Agent>Thank you.\n01:32.240 --> 01:33.680\n<v Agent>May I have your phone number as well, please?\n01:34.920 --> 01:42.400\n<v Customer>Yes, my phone number is five zero four five two nine two three five one and then yeah.\n01:43.560 --> 01:44.800\n<v Agent>Two three five one.\n01:46.560 --> 01:46.880\n<v Agent>Got it.\n01:47.520 --> 01:52.400\n<v Agent>And do you have an e-mail address I can associate with this application?\n01:53.640 --> 01:54.000\n<v Customer>Yes.\n01:54.800 --> 02:00.800\n<v Customer>So my e-mail address is mary.a.sm78@gmail.com.\n02:02.600 --> 02:08.240\n<v Agent>Mary.a, was that a S-N as in November or M as in Mike?\n02:09.440 --> 02:10.240\n<v Customer>M as in Mike.\n02:11.440 --> 02:12.800\n<v Agent>Mike 78.\n02:13.280 --> 02:14.480\n<v Agent>Got it.\n02:14.480 --> 02:15.040\n<v Agent>Thank you, Ms.\n02:15.200 --> 02:15.520\n<v Agent>Smith.\n02:15.520 --> 02:17.840\n<v Agent>Do you currently have any other loans?\n02:19.560 --> 02:22.320\n<v Customer>Yes, so I currently have two other loans through Contoso.\n02:22.720 --> 02:25.840\n<v Customer>So my first one is my car loan, and then my other is my student loan.\n02:26.160 --> 02:31.000\n<v Customer>They total about $1,400 per month combined, and my interest rate is 8%.\n02:32.560 --> 02:32.800\n<v Agent>I see.\n02:32.840 --> 02:35.360\n<v Agent>And you're currently paying those loans off monthly, is that right?\n02:36.400 --> 02:37.200\n<v Customer>Yes, of course I do.\n02:39.280 --> 02:40.000\n<v Agent>Okay, thank you.\n02:40.400 --> 02:41.560\n<v Agent>Here's what I suggest we do.\n02:41.560 --> 02:47.520\n<v Agent>Let me place you on a brief hold again so that I can talk with one of our loan officers and get this started for you immediately.\n02:47.800 --> 02:57.240\n<v Agent>In the meantime, it would be great if you could take a few minutes and complete the remainder of the secure application online at www.contosoloans.com.\n02:57.240 --> 02:59.240\n<v Customer>Yeah, that sounds good.\n02:59.240 --> 03:00.240\n<v Customer>I can go ahead and get started.\n03:00.320 --> 03:01.000\n<v Customer>Thank you for your help.\n03:01.960 --> 03:02.240\n<v Agent>Thank you.```\n"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Generate the quality assurance report using the questions and instructions provided"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "### Quality Assurance Report for Call Transcript\n\n---\n\n### **Greeting and Identification**\n\n**What is the name of the agent who attended the call?**  \nThe agent who attended the call is Sam.  \n\n**How long was the meeting?**  \nThe call lasted approximately 3 minutes and 2 seconds.  \n\n**Did the agent greet the customer appropriately and professionally?**  \nYes, the agent greeted the customer appropriately and professionally at the beginning of the call: \"Good afternoon. This is Sam. Thank you for calling Contoso. How can I help?\"  \n\n**Did the agent verify the customer's identity according to the company's security protocols?**  \nYes, the agent verified the customer’s identity by collecting the customer's full name, current address, phone number, and email address. This aligns with standard security protocols.  \n\n---\n\n### **Call Handling and Resolution**\n\n**Did the agent listen actively and empathetically to the customer's concerns?**  \nYes, the agent actively listened to the customer's concerns, restating the customer's situation to confirm understanding and asking follow-up questions to clarify details.  \n\n**Was the agent able to resolve the customer's issue or provide a clear path to resolution?**  \nYes, the agent provided a clear path to resolution by suggesting the customer complete the secure online loan application and promised to speak with a loan officer to expedite the process.  \n\n**Did the agent follow the correct procedures for handling the specific type of enquiry or complaint?**  \nYes, the agent followed the correct procedures by collecting all necessary information for the loan application and directing the customer to the secure online portal for further steps.  \n\n---\n\n### **Communication Skills**\n\n**Did the agent communicate clearly and effectively, avoiding jargon and ensuring the customer understood the information provided?**  \nYes, the agent communicated clearly and effectively, ensuring the customer understood the instructions for completing the loan application online.  \n\n**Was the agent polite, respectful, and patient throughout the call?**  \nYes, the agent was polite, respectful, and patient throughout the call, using courteous language such as \"Thank you for your patience\" and responding calmly to clarifications.  \n\n---\n\n### **Data Protection and Privacy**\n\n**Did the agent comply with all relevant regulatory requirements during the call (e.g., responsible lending practices, disclosure of terms and conditions)?**  \nYes, the agent complied with regulatory requirements by suggesting the use of a secure online portal for completing the loan application. No sensitive information was requested or shared via insecure channels.  \n\n**Were any sensitive details discussed securely, and was the customer advised not to share sensitive information via insecure channels?**  \nYes, the agent directed the customer to complete the remainder of the application through the secure portal (www.contosoloans.com), which ensures data protection.  \n\n---\n\n### **Customer Satisfaction and Feedback**\n\n**Did the agent ask if there was anything else they could assist the customer with before ending the call?**  \nNo, the agent did not ask if there was anything else they could assist the customer with before ending the call.  \n\n**Was the customer given an opportunity to provide feedback on their experience?**  \nNo, the agent did not ask the customer for feedback on their experience during the call.  \n\n**Were any follow-up actions clearly communicated to the customer?**  \nYes, the agent clearly communicated the next steps, which involved completing the secure online loan application and consulting a loan officer to expedite the process.  \n\n---\n\n### **Handling Difficult Situations**\n\n**Were there any hardship issues during the meeting?**  \nNo, there were no hardship issues raised during the call.  \n\n**How did the agent handle situations where the customer was upset or frustrated?**  \nNot applicable, as the customer did not express frustration or upset during the call.  \n\n**Was the agent able to provide accurate and helpful information about the products or services in question?**  \nYes, the agent provided accurate and helpful information about the loan application process and directed the customer to the appropriate resources.  \n\n---\n\n### **Summary of Non-Compliant Issues**\n\n1. **Missed Opportunity for Additional Assistance:**  \n   The agent did not ask if there was anything else they could assist the customer with before ending the call.  \n\n2. **Lack of Customer Feedback Opportunity:**  \n   The agent did not provide the customer with an opportunity to share feedback about their experience.  \n\n---\n\n### **Recommendations**\n\n- **Ensure Comprehensive Closure:**  \n   Agents should ask customers if there is anything else they need assistance with before ending the call to ensure customer satisfaction.  \n\n- **Request Feedback:**  \n   Agents should incorporate a process to collect feedback from customers at the end of the call to improve service quality.  \n\n---\n\n**End of Report**"
            }
        ]
    }
] 
    
# Include speech result if speech is enabled  
messages = chat_prompt  

def createauditreport(speech):    
    # Generate the completion  
    completion = client.chat.completions.create(  
        model=deployment,
        messages=messages,
        max_tokens=2500,  
        temperature=0.7,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,
        stop=None,  
        stream=False
    )
    response = completion.to_json()
    data = json.loads(response)
    report =  data["choices"][0]["message"]["content"]
    create_and_write_pdf(report)
    return report

def create_and_write_pdf(content):
    """
    Creates a PDF file with the specified filename and writes the given content to it.
    Args:
        filename (str, optional): 
        content (str, optional): 
    """
    try:
        # Get the current timestamp in the format YYYYMMDDHHMMSS.
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # Construct the filename.
        filename = f"audit_{timestamp}.pdf"  # You can change the extension if needed
        
        # Create a PDF canvas object
        c = canvas.Canvas(filename, pagesize=letter)

        # Set font and size (optional)
        c.setFont("Helvetica", 12)

        # Write the content to the PDF
        textobject = c.beginText()
        textobject.setTextOrigin(100, 750)  # Adjust coordinates as needed
        for line in content.splitlines():
            textobject.textLine(line)
        c.drawText(textobject)

        # Save the PDF file
        c.save()
        print(f"Successfully created PDF file: {filename}")
        uploadpdf.upload_pdf_to_azure(filename)

    except Exception as e:
        print(f"An error occurred while creating the PDF: {e}")
        
if __name__ == "__main__":
    report = createauditreport("test")
    create_and_write_pdf(report)
    