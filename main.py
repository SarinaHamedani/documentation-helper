from dotenv import load_dotenv

load_dotenv()
from typing import Set

import streamlit as st
from streamlit_chat import message

from backend.core import run_llm
import streamlit as st

st.set_page_config(
    page_title="Your App Title",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Add these imports
from PIL import Image
import requests
from io import BytesIO

# Sidebar for user information
with st.sidebar:
    st.title("👤 User Profile")
    
    # Initialize user info in session state if not exists
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = ""
    if "profile_picture" not in st.session_state:
        st.session_state["profile_picture"] = None
    
    # Profile picture upload
    st.subheader("Profile Picture")
    uploaded_file = st.file_uploader(
        "Upload your profile picture", 
        type=['png', 'jpg', 'jpeg'],
        key="profile_upload"
    )
    
    if uploaded_file is not None:
        st.session_state["profile_picture"] = uploaded_file
        st.image(uploaded_file, width=150, caption="Your profile picture")
    elif st.session_state["profile_picture"] is not None:
        st.image(st.session_state["profile_picture"], width=150, caption="Your profile picture")
    else:
        # Default avatar if no picture uploaded
        st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", 
                width=150, caption="Default avatar")
    
    # User name input
    st.subheader("Name")
    user_name = st.text_input(
        "Enter your name",
        value=st.session_state["user_name"],
        placeholder="John Doe",
        key="name_input"
    )
    if user_name != st.session_state["user_name"]:
        st.session_state["user_name"] = user_name
    
    # User email input
    st.subheader("Email")
    user_email = st.text_input(
        "Enter your email",
        value=st.session_state["user_email"],
        placeholder="john.doe@example.com",
        key="email_input"
    )
    if user_email != st.session_state["user_email"]:
        st.session_state["user_email"] = user_email
    
    # Display current user info
    if st.session_state["user_name"] or st.session_state["user_email"]:
        st.divider()
        st.subheader("Current User Info")
        if st.session_state["user_name"]:
            st.write(f"**Name:** {st.session_state['user_name']}")
        if st.session_state["user_email"]:
            st.write(f"**Email:** {st.session_state['user_email']}")
    
    # Clear profile button
    if st.button("Clear Profile", type="secondary"):
        st.session_state["user_name"] = ""
        st.session_state["user_email"] = ""
        st.session_state["profile_picture"] = None
        st.rerun()

def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string


# Add this function to get a profile picture
def get_profile_picture(email):
    # This uses Gravatar to get a profile picture based on email
    # You can replace this with a different service or use a default image
    gravatar_url = f"https://www.gravatar.com/avatar/{hash(email)}?d=identicon&s=200"
    response = requests.get(gravatar_url)
    img = Image.open(BytesIO(response.content))
    return img


# Custom CSS for dark theme and modern look
st.markdown(
    """
<style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stTextInput > div > div > input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: #FFFFFF;
    }
    .stSidebar {
        background-color: #252526;
    }
    .stMessage {
        background-color: #2D2D2D;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Set page config at the very beginning


# Sidebar user information
with st.sidebar:
    st.title("User Profile")

    # You can replace these with actual user data
    user_name = "John Doe"
    user_email = "john.doe@example.com"

    profile_pic = get_profile_picture(user_email)
    st.image(profile_pic, width=150)
    st.write(f"**Name:** {user_name}")
    st.write(f"**Email:** {user_email}")

st.header("LangChain🦜🔗 Udemy Course- Helper Bot")

# Initialize session state
if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []

# Create two columns for a more modern layout
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_input("Prompt", placeholder="Enter your message here...")

with col2:
    if st.button("Submit", key="submit"):
        prompt = prompt or "Hello"  # Default message if input is empty

if prompt:
    with st.spinner("Generating response..."):
        generated_response = run_llm(
            query=prompt, chat_history=st.session_state["chat_history"]
        )

        sources = set(doc.metadata["source"] for doc in generated_response["context"])
        formatted_response = (
            f"{generated_response['answer']} \n\n {create_sources_string(sources)}"
        )

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["answer"]))

# Display chat history
if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answers_history"],
        st.session_state["user_prompt_history"],
    ):
        st.chat_message("user").write(user_query)
        st.chat_message("assistant").write(generated_response)


# Add a footer
st.markdown("---")
st.markdown("Powered by LangChain and Streamlit")
