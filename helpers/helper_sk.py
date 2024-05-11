# Helper for Semantic kernel

# Imports

# Standard imports
import os
import json
from dotenv import load_dotenv

# Streamlit imports
import streamlit as st

# SK imports
import semantic_kernel as sk
from semantic_kernel.contents.chat_history import ChatHistory
import semantic_kernel.connectors.ai.open_ai as sk_aoai
import semantic_kernel.connectors.ai.ollama as sk_ollama
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings


# Load settings and keys from .env
 
# Assign environment settings and keys to variables
load_dotenv(override=True)

# gpt-4
GPT_4_SERVICE_ID = os.getenv("GPT_4_SERVICE_ID")
GPT_4_AOAI_API_KEY = os.getenv("GPT_4_AOAI_API_KEY")
GPT_4_AOAI_ENDPOINT = os.getenv("GPT_4_AOAI_ENDPOINT")
GPT_4_AOAI_API_VERSION = os.getenv("GPT_4_AOAI_API_VERSION")
GPT_4_AOAI_DEPLOYMENT_NAME = os.getenv("GPT_4_AOAI_DEPLOYMENT_NAME")

# gpt-3.5
GPT_3_5_SERVICE_ID = os.getenv("GPT_3_5_SERVICE_ID")
GPT_3_5_AOAI_API_KEY = os.getenv("GPT_3_5_AOAI_API_KEY")
GPT_3_5_AOAI_ENDPOINT = os.getenv("GPT_3_5_AOAI_ENDPOINT")
GPT_3_5_AOAI_API_VERSION = os.getenv("GPT_3_5_AOAI_API_VERSION")
GPT_3_5_AOAI_DEPLOYMENT_NAME = os.getenv("GPT_3_5_AOAI_DEPLOYMENT_NAME")

# phi-3
PHI3_MINI_OLLAMA_SERVICE_ID = os.getenv("PHI3_MINI_OLLAMA_SERVICE_ID")
PHI3_MINI_OLLAMA_MODEL_ID = os.getenv("PHI3_MINI_OLLAMA_MODEL_ID")
PHI3_MINI_OLLAMA_URL = os.getenv("PHI3_MINI_OLLAMA_URL")

# mixtral
MIXTRAL_8x7B_OLLAMA_SERVICE_ID = os.getenv("MIXTRAL_8x7B_OLLAMA_SERVICE_ID")
MIXTRAL_8x7B_OLLAMA_MODEL_ID = os.getenv("MIXTRAL_8x7B_OLLAMA_MODEL_ID")
MIXTRAL_8x7B_OLLAMA_URL = os.getenv("MIXTRAL_8x7B_OLLAMA_URL")



# Return a new chat history
def new_chat_history():
    """
    Return a new chat history.
    """
    return ChatHistory()


# Initialize the application chat services.
def initialize_chat_services():
    """
    Initialize the chat services for the application.

    For each model (chat service) that is to be initialized, the following steps are taken:

    1. Create the chat service.
    2. Add the chat service to the kernel.
    3. Add the chat service to the session state.
    4. Add the service name to the chat_services list in the session state.

    Each chat service is stored in the session state with the service name as a key.
    A list of chat services is stored in the session state as chat_services.

    """

    # Initialize only if not already initialized
    if "chat_services" not in st.session_state:

        # Initialize the kernel
        if "kernel" not in st.session_state:  
            st.session_state.kernel = sk.Kernel()

        # Initialize list of chat services
        st.session_state.chat_services = []

        # AOAI GPT-4
        # Create the chat service and add it to the kernel, then add the service to the session state, and the service name to the chat_services list
        if GPT_4_SERVICE_ID and GPT_4_AOAI_API_KEY and GPT_4_AOAI_ENDPOINT and GPT_4_AOAI_DEPLOYMENT_NAME:
            chat_service = sk_aoai.AzureChatCompletion(service_id=GPT_4_SERVICE_ID, deployment_name=GPT_4_AOAI_DEPLOYMENT_NAME, endpoint=GPT_4_AOAI_ENDPOINT, api_key=GPT_4_AOAI_API_KEY)
            st.session_state.kernel.add_service(chat_service)
            st.session_state[f"{GPT_4_SERVICE_ID}_service"] = chat_service
            st.session_state.chat_services.append(GPT_4_SERVICE_ID)

        # AOAI GPT-3.5
        # Create the chat service and add it to the kernel, then add the service to the session state, and the service name to the chat_services list
        if GPT_3_5_SERVICE_ID and GPT_3_5_AOAI_API_KEY and GPT_3_5_AOAI_ENDPOINT and GPT_3_5_AOAI_DEPLOYMENT_NAME:
            chat_service = sk_aoai.AzureChatCompletion(service_id=GPT_3_5_SERVICE_ID, deployment_name=GPT_3_5_AOAI_DEPLOYMENT_NAME, endpoint=GPT_3_5_AOAI_ENDPOINT, api_key=GPT_3_5_AOAI_API_KEY)
            st.session_state.kernel.add_service(chat_service)
            st.session_state[f"{GPT_3_5_SERVICE_ID}_service"] = chat_service
            st.session_state.chat_services.append(GPT_3_5_SERVICE_ID)

        # OLLAMA PHI-3
        # Create the chat service and add it to the kernel, then add the service to the session state, and the service name to the chat_services list
        if PHI3_MINI_OLLAMA_SERVICE_ID and PHI3_MINI_OLLAMA_MODEL_ID and PHI3_MINI_OLLAMA_URL:
            chat_service = sk_ollama.OllamaChatCompletion(service_id=PHI3_MINI_OLLAMA_SERVICE_ID,  ai_model_id=PHI3_MINI_OLLAMA_MODEL_ID, url=PHI3_MINI_OLLAMA_URL)
            st.session_state.kernel.add_service(chat_service)
            st.session_state[f"{PHI3_MINI_OLLAMA_SERVICE_ID}_service"] = chat_service
            st.session_state.chat_services.append(PHI3_MINI_OLLAMA_SERVICE_ID)

        # OLLAMA MIXTRAL 8x7B
        # Create the chat service and add it to the kernel, then add the service to the session state, and the service name to the chat_services list
        if MIXTRAL_8x7B_OLLAMA_SERVICE_ID and MIXTRAL_8x7B_OLLAMA_MODEL_ID and MIXTRAL_8x7B_OLLAMA_URL:
            chat_service = sk_ollama.OllamaChatCompletion(service_id=MIXTRAL_8x7B_OLLAMA_SERVICE_ID,  ai_model_id=MIXTRAL_8x7B_OLLAMA_MODEL_ID, url=MIXTRAL_8x7B_OLLAMA_URL)
            st.session_state.kernel.add_service(chat_service)
            st.session_state[f"{MIXTRAL_8x7B_OLLAMA_SERVICE_ID}_service"] = chat_service
            st.session_state.chat_services.append(MIXTRAL_8x7B_OLLAMA_SERVICE_ID)



# Generate streaming response
async def generate_streaming_response(response_holder, chat_service, system_message, chat_history, user_input, **kwargs):

    # Initialize the chat settings based on the service ID and kwargs
    service_id = chat_service.service_id
    chat_settings = sk_aoai.OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=kwargs.get("max_tokens", 2000),
        temperature=kwargs.get("temperature", 0.7),
        top_p=kwargs.get("top_p", 0.8),
        frequency_penalty=kwargs.get("frequency_penalty", 0.0),
        presence_penalty=kwargs.get("presence_penalty", 0.0),
        stream=True,
    )
    
    
    # Build the chat history based on the system message and user input
    
    # If no chat history is provided, create a new one
    if not chat_history:
        chat_history = new_chat_history()
        
    # Add the user input to the chat history
    if user_input:
        chat_history.add_user_message(user_input)
        
    # If system message is provided, initialize the chat for the prompt with it and the chat history, otherwise just the chat history
    if system_message:
        chat = ChatHistory(messages=chat_history.messages, system_message=system_message)
    else:
        chat = chat_history

    # Execute the prompt 
    output = ""
    stream = chat_service.complete_chat_stream(chat_history=chat, settings=chat_settings)

    # Stream the response
    async for message in stream:
        output += str(message[0])
        response_holder.write(output)

    # Post-process the entire stream for JSON formatting at the end of streaming
    try:
        # Attempt to parse the JSON and reformat it
        parsed_json = json.loads(output)
        response_holder.json(output)  # Display the pretty-printed JSON
    except json.JSONDecodeError:
        # If JSON parsing fails, do nothing or handle it accordingly
        print(f"JSON parsing failed. {service_id}")
        pass

    # Return the output
    return output


# Generate a response
async def generate_response(response_holder, chat_service, system_message, chat_history, user_input, **kwargs):
    
    # Initialize the chat settings based on the service ID and kwargs
    service_id = chat_service.service_id
    chat_settings = sk_aoai.AzureChatPromptExecutionSettings(
        service_id=service_id,
        max_tokens=kwargs.get("max_tokens", 2000),
        temperature=kwargs.get("temperature", 0.0),
        top_p=kwargs.get("top_p", 0.2),
        frequency_penalty=kwargs.get("frequency_penalty", 0.0),
        presence_penalty=kwargs.get("presence_penalty", 0.0),
        stream=False,  # Set stream to False for non-streaming execution
    )
    
    # Build the chat history based on the system message and user input
    
    # If no chat history is provided, create a new one
    if not chat_history:
        chat_history = new_chat_history()
        
    # Add the user input to the chat history
    if user_input:
        chat_history.add_user_message(user_input)
        
    # If system message is provided, initialize the chat for the prompt with it and the chat history, otherwise just the chat history
    if system_message:
        chat = ChatHistory(messages=chat_history.messages, system_message=system_message)
    else:
        chat = chat_history
        
    # Await the completion of the chat
    completions = await chat_service.complete_chat(chat_history=chat, settings=chat_settings)

    # Use the concatenated response
    response_holder.write(completions[0].content)
 
    return completions[0].content
        
