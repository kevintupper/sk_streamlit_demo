#***********************************************************************************************
# Demonstration app for Semantic Kernel and Streamlit
#***********************************************************************************************

# Standard imports
import asyncio

# Third-party imports
import streamlit as st

# Local imports
from helpers import helper_utils as utils
from helpers import helper_sk as sk


#***********************************************************************************************
# Menu Definition
#***********************************************************************************************
MENU_ITEMS = [
    {"menu_title": "Chat Services", "return_value": "chat_services", "submenu": []},
    {"menu_title": "Chat Compare", "return_value": "chat_compare", "submenu": []},

    # Add your menu items (and submenus) 
    # {"menu_title": "Agents", "return_value": "agents", "submenu": []},
    # {"menu_title": "Demo 2", "return_value": "demo_2", "submenu": [
    #     {"menu_title": "Next 1", "return_value": "demo_2_next_1"},
    #     {"menu_title": "Next 2", "return_value": "demo_2_next_2"},
    # ]},
]


#***********************************************************************************************
# Page content functions
#***********************************************************************************************
async def chat_services():
    """
    Display the chat services page content.
    """

    # Display the header and description
    st.markdown("### Chat Services")
    st.write("The following semantic kernel chat services are initialized and ready for use:")

    # Display the chat services
    st.write(st.session_state.chat_services)
    
    # Show information about semantic kernel
    st.write("Semantic Kernel is an open-source SDK that lets you easily build agents that can call your existing code. As a highly extensible SDK, you can use Semantic Kernel with models from OpenAI, Azure OpenAI, Hugging Face, and more! By combining your existing C#, Python, and Java code with these models, you can build agents that answer questions and automate processes.")

    st.markdown("- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/overview/)")
    st.markdown("- [Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)")


async def chat_compare():
    """
    Display the chat compare page content.
    """


    # Function to display message history
    def display_message_history(container, chat_history):
        """
        Display the message history.
        """
        if container != None and chat_history != None:
            for message in chat_history.messages:
                with container.chat_message(message.role):
                    st.markdown(message.content)


    # Display the header and description
    st.markdown("### Chat Compare")
    st.write("Compare chat responses from two different chat services.")


    # Setup the sidebar
    await setup_chat_compare_sidebar()

    # Create two columns
    col1, col2 = st.columns(2)

    # Display the chat service name, set the chat service, and get the chat history, display the chat history   
    with col1:
        st.markdown(f"**{st.session_state.chat_service_1}**")
        chat_service_1 = st.session_state.get(f"{st.session_state.chat_service_1}_service")
        chat_history_1 = st.session_state.get(f"{st.session_state.chat_service_1}_history")    
        display_message_history(col1, chat_history_1)

    # Display the chat service name, set the chat service, and get the chat history, display the chat history   
    with col2:
        st.markdown(f"**{st.session_state.chat_service_2}**")
        chat_service_2 = st.session_state.get(f"{st.session_state.chat_service_2}_service")
        chat_history_2 = st.session_state.get(f"{st.session_state.chat_service_2}_history")
        display_message_history(col2, chat_history_2)


    # Get the user prompt
    if prompt := st.chat_input():

        # Add the user input to the chat history and display the user input
        chat_history_1.add_user_message(prompt)
        chat_history_2.add_user_message(prompt)
        
        # Display the user input
        col1.chat_message("user").markdown(prompt)
        col2.chat_message("user").markdown(prompt)

        # Create placeholders for the assistant's response and setup the routine to get the responses
        with col1.chat_message("assistant"):
            placeholder_1 = st.empty()
            
            # Initialize the response coroutine
            response_1 = sk.generate_streaming_response(
                response_holder=placeholder_1,
                chat_service=chat_service_1,
                system_message="You are a helpful AI assistant.",
                chat_history=chat_history_1,
                user_input=None, # Already added to chat history.
            )

        # Placeholder for the assistant's response
        with col2.chat_message("assistant"):
            placeholder_2 = st.empty()

            # Initialize the response coroutine
            response_2 = sk.generate_streaming_response(
                response_holder=placeholder_2,
                chat_service=chat_service_2,
                system_message="You are a helpful AI assistant.",
                chat_history=chat_history_2,
                user_input=None, # Already added to chat history.
            )
                
        # Build and gather the response coroutines
        coroutines = [response_1, response_2]
        responses = await asyncio.gather(*coroutines)

        # Add the assistant's response to the chat history
        chat_history_1.add_assistant_message(responses[0])
        chat_history_2.add_assistant_message(responses[1])

        # Important: Update the session state with the modified chat history
        st.session_state[f"{chat_service_1}_history"] = chat_history_1
        st.session_state[f"{chat_service_2}_history"] = chat_history_2 


#***********************************************************************************************
# Page display and styling helper functions
#***********************************************************************************************
async def setup_chat_compare_sidebar():
    """
    Setup the sidebar for the chat compare page and detect changes in the selection.
    """
    with st.sidebar:
        # Display the chat service options and track their selections
        st.sidebar.markdown("**Chat Service 1**")
        chat_service_1_selection = st.radio(
            "Chat Service 1", 
            st.session_state.chat_services, 
            index=st.session_state.chat_services.index(st.session_state.chat_service_1), 
            label_visibility="collapsed" 
        )
        
        st.sidebar.markdown("**Chat Service 2**")
        chat_service_2_selection = st.radio(
            "Chat Service 2", 
            st.session_state.chat_services, 
            index=st.session_state.chat_services.index(st.session_state.chat_service_2), 
            label_visibility="collapsed"
        )

        # Detect changes, update session state, reinitialize histories, and rerun the app
        if st.session_state.chat_service_1 != chat_service_1_selection or st.session_state.chat_service_2 != chat_service_2_selection:
            st.session_state.chat_service_1 = chat_service_1_selection
            st.session_state[f"{chat_service_1_selection}_history"] = sk.new_chat_history()
            st.session_state.chat_service_2 = chat_service_2_selection
            st.session_state[f"{chat_service_2_selection}_history"] = sk.new_chat_history()
            st.rerun()


async def initialize_app_session_state():
    """
    Initialize the session state variables for the application.
    """
    
    # Initialize chat_sevices if necssary
    if "chat_services" not in st.session_state:
        sk.initialize_chat_services()
        

    # Initialize chat app specific settings
    if "chat_compare_initialized" not in st.session_state:
        
        # Create a chat_history for each service
        for service_name in st.session_state.chat_services:
            st.session_state[f"{service_name}_history"] = sk.new_chat_history()

        # Initialize chat service 1 and 2
        st.session_state.chat_service_1 = st.session_state.chat_services[0]
        st.session_state.chat_service_2 = st.session_state.chat_services[1]

        # Set the chat compare initialized flag
        st.session_state.chat_compare_initialized = True


async def setup_styling_and_menu():
    """
    Setup the page styling and sidebar options and show the menu.
    """
    
    # Insert custom CSS into the page
    utils.insert_custom_css('./helpers/style_helpers/site.css')
    utils.insert_custom_css('./helpers/style_helpers/menu.css')

    # Setup the menu
    menu_items = []
    for item in MENU_ITEMS:
        # Filter submenu items if present
        submenu = item.get("submenu", [])
        
        # Add the parent menu item if not in hidden items, with filtered submenu
        item["submenu"] = submenu
        menu_items.append(item)

    # Setup the sidebar menu options
    with st.sidebar:
        with st.container():
            st.markdown("<div class='logo-divider'></div>", unsafe_allow_html=True)

            # Get the selected title from filtered_menu_items
            selected_title = st.radio("Main navigation", [item["menu_title"] for item in menu_items], label_visibility="collapsed")

            st.markdown("<div class='tight-divider'></div>", unsafe_allow_html=True)

            # Get the selected menu item
            selected_menu_item = [item for item in menu_items if item["menu_title"] == selected_title][0]

            # Filter submenu based on selected main navigation and aoai_mode
            submenu_items = selected_menu_item["submenu"]

            # Check if there is a submenu
            if submenu_items:
                # Display the submenu as radio buttons
                selected_submenu_title = st.radio("Sub navigation", [item["menu_title"] for item in submenu_items], label_visibility="collapsed")
                selected_return_value = [item["return_value"] for item in submenu_items if item["menu_title"] == selected_submenu_title][0]
            else:
                selected_return_value = selected_menu_item["return_value"]

    return selected_return_value    


async def display_page_content(selected_return_value):
    """
    Display the page content based on the selected menu item.
    """
    # Check if the function exists in the global namespace
    if selected_return_value in globals():
    
        # Call the function based on its name
        await globals()[selected_return_value]()



#***********************************************************************************************
# Main function
#***********************************************************************************************
async def main():
        """
        Main function that runs Streamlit app.
        """
    
        # Configure the Streamlit app settings
        st.set_page_config(
            page_title="Semantic Kernal and Streamlit Demo",            # Set the page title
            page_icon="",                                               # Set the page icon
            layout="wide",                                              # Set the page layout to wide
            initial_sidebar_state="expanded",                           # Set the initial state of the sidebar to expanded
        )
    
        # Initialize the session state vars for the application
        await initialize_app_session_state()

        # Setup the page, get the selected_title, display the page content
        selected_return_value = await setup_styling_and_menu()
        await display_page_content(selected_return_value)


# Call the main function
if __name__ == "__main__":
    asyncio.run(main())
