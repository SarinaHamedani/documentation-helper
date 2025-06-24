from typing import Set
from backend.core import run_llm
import streamlit as st

# Inject custom CSS for dark theme (LangChain docs style)
st.markdown(
    """
    <style>
    /* Background and main text */
    body, .stApp {
        background-color: #18181b !important;
        color: #f3f4f6 !important;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #232329 !important;
        color: #f3f4f6 !important;
    }
    /* Headers and titles */
    .st-emotion-cache-10trblm, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq, .st-emotion-cache-1avcm0n {
        color: #f3f4f6 !important;
    }
    /* Accent color for links and highlights */
    a, .st-emotion-cache-16idsys, .st-emotion-cache-1c7y2kd {
        color: #10b981 !important;
    }
    /* Input fields and widgets */
    .stTextInput > div > div > input, .stTextInput > div > div > textarea, .stTextArea > div > textarea {
        background-color: #232329 !important;
        color: #f3f4f6 !important;
        border: 1px solid #27272a !important;
    }
    /* Buttons */
    button, .stButton > button {
        background-color: #27272a !important;
        color: #f3f4f6 !important;
        border: 1px solid #10b981 !important;
    }
    button:hover, .stButton > button:hover {
        background-color: #10b981 !important;
        color: #18181b !important;
    }
    /* Divider */
    hr, .stDivider {
        border-color: #27272a !important;
    }
    /* Chat message bubbles */
    .st-emotion-cache-1c7y2kd, .st-emotion-cache-16idsys {
        background-color: #232329 !important;
        color: #f3f4f6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Page configuration
st.set_page_config(
    page_title="Langchain Documentation Helper",
    page_icon="🤖",
    layout="wide"
)

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

# Main content area
st.header("🤖 Langchain Documentation Helper Bot")

# Display user info in main area if available
if st.session_state["user_name"]:
    st.write(f"Welcome back, **{st.session_state['user_name']}**! 👋")

prompt = st.text_input("Prompt", placeholder="Enter your prompt here..")

if (
    "chat_answers_history" not in st.session_state
    and "user_prompt_history" not in st.session_state
    and "chat_history" not in st.session_state
):
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []

def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string

if prompt:
    with st.spinner("Generating response.."):
        generated_response = run_llm(query=prompt, chat_history=st.session_state["chat_history"])
        sources = set([doc.metadata["source"] for doc in generated_response["source_documents"]])

        formatted_response = f"{generated_response['result']} \n\n {create_sources_string(sources)}"
        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))

if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(st.session_state["chat_answers_history"], st.session_state["user_prompt_history"]):
        st.chat_message("user").write(user_query)
        st.chat_message("assistant").write(generated_response)
        
