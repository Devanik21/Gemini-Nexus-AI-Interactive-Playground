import streamlit as st
import google.generativeai as genai
import random

# --- Page Configuration ---
st.set_page_config(
    page_title="Gemini Nexus",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- App Title and Description ---
st.title("🎮 Gemini Nexus: AI Interactive Playground")
st.markdown("""
Welcome to the Gemini Nexus! This is a place to play interactive games with a powerful AI model.
Choose a game from the sidebar, and let the fun begin. Your AI companion is ready to play!
""")

# --- Sidebar for API Key and Game Selection ---
with st.sidebar:
    st.header("Configuration")
    gemini_api_key = st.text_input("Enter your Gemini API Key", type="password")
    
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            st.success("API Key is valid!")
        except Exception as e:
            st.error(f"Invalid API Key: {e}")

    st.markdown("---")
    game_choice = st.selectbox(
        "Choose your game:",
        ("Select a game", "Story Adventure", "Guess the Object", "20 Questions")
    )
    st.markdown("---")
    st.info("This app uses the Gemini API. Your conversations are not stored.")


# --- Game Logic ---

def story_adventure():
    """
    A game where the user and AI collaboratively create a story.
    """
    st.header("Story Adventure")
    st.markdown("Let's create a story together! You start, and I'll continue. Or I can start if you prefer.")

    # Initialize chat history in session state
    if "story_messages" not in st.session_state:
        st.session_state.story_messages = [
            {"role": "assistant", "content": "You are an expert storyteller. We will write a story together. The user will start with a premise, and you will continue the story, adding twists and turns. Make it engaging and interactive, often asking the user 'What do you do next?'"}
        ]

    # Display chat messages
    for message in st.session_state.story_messages:
        if message["role"] != "assistant" or len(st.session_state.story_messages) > 1:
             with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What happens next?"):
        st.session_state.story_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                model = genai.GenerativeModel('gemini-pro')
                # We send the whole chat history to the model
                chat_session = model.start_chat(
                    history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.story_messages]
                )
                response = chat_session.send_message(prompt, stream=True)
                for chunk in response:
                    full_response += (chunk.text or "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"An error occurred: {e}"
                message_placeholder.error(full_response)

        st.session_state.story_messages.append({"role": "assistant", "content": full_response})


def guess_the_object():
    """
    A game where the AI thinks of an object and the user guesses it.
    """
    st.header("Guess the Object")
    st.markdown("I'm thinking of an object. You have to guess what it is by asking me yes/no questions.")

    # Initialize game state
    if "guess_object_state" not in st.session_state:
        st.session_state.guess_object_state = {
            "object": None,
            "chat": [],
            "game_over": False
        }

    game_state = st.session_state.guess_object_state

    if game_state["object"] is None:
        with st.spinner("I'm thinking of an object..."):
            try:
                model = genai.GenerativeModel('gemma-3-27b-it')
                # Ask Gemini to pick an object
                prompt = "Think of a common household object and tell me what it is. Just give me the name of the object and nothing else."
                response = model.generate_content(prompt)
                game_state["object"] = response.text.strip().lower()
                game_state["chat"].append({"role": "assistant", "content": "I have an object in mind. Start asking questions!"})
            except Exception as e:
                st.error(f"Error starting the game: {e}")
                return
    
    # Display chat
    for message in game_state["chat"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if game_state["game_over"]:
        st.success(f"You got it! The object was **{game_state['object']}**.")
        if st.button("Play Again"):
            del st.session_state.guess_object_state
            st.rerun()
        return

    # User input
    if prompt := st.chat_input("Ask a yes/no question or guess the object."):
        game_state["chat"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Check if the user is guessing
            if prompt.lower() == game_state["object"]:
                full_response = f"Yes, that's it! The object was **{game_state['object']}**."
                game_state["game_over"] = True
                message_placeholder.markdown(full_response)
                st.balloons()
            else:
                # Ask Gemini to answer the yes/no question
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    system_prompt = f"You are playing a guessing game. The secret object is '{game_state['object']}'. The user is asking questions to guess it. Answer the following question with only 'Yes', 'No', or 'I cannot answer that'. The question is: '{prompt}'"
                    response = model.generate_content(system_prompt)
                    full_response = response.text.strip()
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"An error occurred: {e}"
                    message_placeholder.error(full_response)

        game_state["chat"].append({"role": "assistant", "content": full_response})
        if game_state["game_over"]:
            st.rerun()


def twenty_questions():
    """
    A game where the user thinks of an object and the AI guesses it.
    """
    st.header("20 Questions")
    st.markdown("You think of an object, and I will try to guess it in 20 questions or less.")

    # Initialize chat history
    if "twentyq_messages" not in st.session_state:
        st.session_state.twentyq_messages = [
            {"role": "assistant", "content": "I am an expert at the game 20 questions. I will ask yes/no questions to guess the object you are thinking of. I will start. Is it an animal?"}
        ]

    # Display chat messages
    for message in st.session_state.twentyq_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Your answer (Yes/No/Maybe)"):
        st.session_state.twentyq_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                model = genai.GenerativeModel('gemini-pro')
                chat_session = model.start_chat(
                    history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.twentyq_messages]
                )
                response = chat_session.send_message(prompt, stream=True)
                for chunk in response:
                    full_response += (chunk.text or "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"An error occurred: {e}"
                message_placeholder.error(full_response)

        st.session_state.twentyq_messages.append({"role": "assistant", "content": full_response})

# --- Main App Logic ---
if not gemini_api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to start playing.")
else:
    if game_choice == "Story Adventure":
        story_adventure()
    elif game_choice == "Guess the Object":
        guess_the_object()
    elif game_choice == "20 Questions":
        twenty_questions()
    elif game_choice == "Select a game":
        st.info("Select a game from the sidebar to get started!")
