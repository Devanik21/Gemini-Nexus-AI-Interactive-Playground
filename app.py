import streamlit as st
import google.generativeai as genai
import random
import time
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import re

# Configure page
st.set_page_config(
    page_title="🎮 Gemini Nexus",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark gradient theme
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #1a1a2e 75%, #0f0f23 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
    }
    
    /* Custom container styling */
    .game-container {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.8), rgba(22, 33, 62, 0.6));
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Chat message styling */
    .chat-message {
        background: linear-gradient(145deg, rgba(22, 33, 62, 0.7), rgba(26, 26, 46, 0.5));
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    
    .ai-message {
        border-left-color: #2196F3;
    }
    
    .user-message {
        border-left-color: #FF9800;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #45a049, #4CAF50);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(26, 26, 46, 0.8);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.8);
        color: white;
        border-radius: 8px;
    }
    
    /* Metrics styling */
    .metric-container {
        background: linear-gradient(145deg, rgba(22, 33, 62, 0.8), rgba(26, 26, 46, 0.6));
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Game title styling */
    .game-title {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #4CAF50, #2196F3, #FF9800);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #4CAF50; }
    .status-thinking { background-color: #FF9800; }
    .status-offline { background-color: #f44336; }
    
    /* Animated elements */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .thinking {
        animation: pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini API
@st.cache_resource
def initialize_gemini():
    """Initialize Gemini AI with API key from secrets"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemma-2-27b-it')
        return model
    except Exception as e:
        st.error(f"Failed to initialize Gemini AI: {str(e)}")
        return None

# Game Classes
class GameSession:
    def __init__(self, game_type: str):
        self.game_type = game_type
        self.start_time = datetime.now()
        self.messages = []
        self.score = 0
        self.level = 1
        self.game_state = {}
        
    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

class StoryAdventure:
    def __init__(self, model):
        self.model = model
        self.story_context = ""
        self.player_choices = []
        self.current_scene = 1
        
    def generate_scene(self, user_input: str = None):
        """Generate next story scene based on user input"""
        if not user_input:
            prompt = f"""You are a master storyteller creating an interactive adventure game. 
            Start a thrilling adventure story and present the player with 3 meaningful choices.
            Make it engaging, immersive, and set in a fantasy world.
            
            Format your response as:
            SCENE: [Vivid scene description]
            CHOICES:
            A) [Choice 1]
            B) [Choice 2] 
            C) [Choice 3]"""
        else:
            prompt = f"""Continue this interactive story based on the player's choice: "{user_input}"
            
            Previous context: {self.story_context}
            
            Create the next scene and provide 3 new choices. Make consequences meaningful.
            
            Format your response as:
            SCENE: [What happens next based on their choice]
            CHOICES:
            A) [Choice 1]
            B) [Choice 2]
            C) [Choice 3]"""
            
        try:
            response = self.model.generate_content(prompt)
            self.story_context += f"\n{response.text}"
            self.current_scene += 1
            return response.text
        except Exception as e:
            return f"Error generating story: {str(e)}"

class RiddleMaster:
    def __init__(self, model):
        self.model = model
        self.current_riddle = ""
        self.riddle_answer = ""
        self.hints_used = 0
        self.difficulty = "medium"
        
    def generate_riddle(self, difficulty: str = "medium"):
        """Generate a new riddle based on difficulty"""
        self.difficulty = difficulty
        self.hints_used = 0
        
        prompt = f"""Create a {difficulty} difficulty riddle. 
        Make it creative, engaging, and solvable.
        
        Format your response as:
        RIDDLE: [The riddle question]
        ANSWER: [The answer]
        HINT1: [First hint]
        HINT2: [Second hint]
        HINT3: [Final hint]"""
        
        try:
            response = self.model.generate_content(prompt)
            lines = response.text.split('\n')
            
            for line in lines:
                if line.startswith('RIDDLE:'):
                    self.current_riddle = line.replace('RIDDLE:', '').strip()
                elif line.startswith('ANSWER:'):
                    self.riddle_answer = line.replace('ANSWER:', '').strip().lower()
                    
            return self.current_riddle
        except Exception as e:
            return f"Error generating riddle: {str(e)}"
            
    def check_answer(self, user_answer: str):
        """Check if user's answer is correct"""
        return user_answer.lower().strip() in self.riddle_answer
        
    def get_hint(self):
        """Get a hint for the current riddle"""
        self.hints_used += 1
        hints = ["Think about wordplay", "Consider multiple meanings", "What sounds similar?"]
        if self.hints_used <= len(hints):
            return hints[self.hints_used - 1]
        return "No more hints available!"

class RolePlayChat:
    def __init__(self, model):
        self.model = model
        self.character = ""
        self.scenario = ""
        self.conversation_history = []
        
    def set_character(self, character: str, scenario: str):
        """Set the AI character and scenario"""
        self.character = character
        self.scenario = scenario
        self.conversation_history = []
        
    def chat(self, user_message: str):
        """Continue roleplay conversation"""
        prompt = f"""You are roleplaying as {self.character} in this scenario: {self.scenario}
        
        Previous conversation: {' '.join([msg['content'] for msg in self.conversation_history[-5:]])}
        
        User says: "{user_message}"
        
        Respond in character, staying true to the personality and scenario. Be engaging and interactive."""
        
        try:
            response = self.model.generate_content(prompt)
            self.conversation_history.append({
                "user": user_message,
                "ai": response.text,
                "timestamp": datetime.now()
            })
            return response.text
        except Exception as e:
            return f"Error in roleplay: {str(e)}"

class WordGame:
    def __init__(self, model):
        self.model = model
        self.game_mode = ""
        self.current_word = ""
        self.score = 0
        self.attempts = 0
        
    def start_word_association(self):
        """Start a word association game"""
        prompt = "Give me a random word to start a word association game. Just respond with one word."
        try:
            response = self.model.generate_content(prompt)
            self.current_word = response.text.strip().lower()
            return self.current_word
        except Exception as e:
            return "error"
            
    def check_association(self, user_word: str):
        """Check if user's word is associated with current word"""
        prompt = f"""Are the words "{self.current_word}" and "{user_word}" reasonably associated? 
        Consider synonyms, categories, rhymes, or logical connections.
        Respond with just YES or NO, then explain briefly."""
        
        try:
            response = self.model.generate_content(prompt)
            is_valid = "YES" in response.text.upper()
            self.current_word = user_word.lower()
            if is_valid:
                self.score += 1
            self.attempts += 1
            return is_valid, response.text
        except Exception as e:
            return False, f"Error checking association: {str(e)}"

# Main App
def main():
    st.markdown('<h1 class="game-title">🎮 Gemini Nexus: AI Interactive Playground</h1>', 
                unsafe_allow_html=True)
    
    # Initialize Gemini
    model = initialize_gemini()
    if not model:
        st.error("Cannot start app without Gemini AI connection.")
        st.stop()
    
    # Initialize session state
    if 'game_session' not in st.session_state:
        st.session_state.game_session = None
    if 'story_game' not in st.session_state:
        st.session_state.story_game = StoryAdventure(model)
    if 'riddle_game' not in st.session_state:
        st.session_state.riddle_game = RiddleMaster(model)
    if 'roleplay_game' not in st.session_state:
        st.session_state.roleplay_game = RolePlayChat(model)
    if 'word_game' not in st.session_state:
        st.session_state.word_game = WordGame(model)
    if 'ai_status' not in st.session_state:
        st.session_state.ai_status = "online"
    
    # Sidebar Controls
    with st.sidebar:
        st.markdown("### 🎮 Game Controls")
        
        # AI Status
        status_color = {
            "online": "status-online",
            "thinking": "status-thinking", 
            "offline": "status-offline"
        }
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <span class="status-indicator {status_color[st.session_state.ai_status]}"></span>
            AI Status: {st.session_state.ai_status.title()}
        </div>
        """, unsafe_allow_html=True)
        
        # Game Selection
        game_type = st.selectbox(
            "🎯 Choose Your Adventure",
            ["Story Adventure", "Riddle Master", "Role Play Chat", "Word Association", "About"]
        )
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        if game_type == "Story Adventure":
            st.session_state.story_theme = st.selectbox(
                "Story Theme", 
                ["Fantasy", "Sci-Fi", "Mystery", "Horror", "Adventure"]
            )
            
        elif game_type == "Riddle Master":
            st.session_state.riddle_difficulty = st.selectbox(
                "Difficulty",
                ["easy", "medium", "hard", "expert"]
            )
            
        elif game_type == "Role Play Chat":
            st.session_state.rp_character = st.selectbox(
                "Character Type",
                ["Wise Wizard", "Space Captain", "Detective", "Time Traveler", "Dragon", "Custom"]
            )
            
            if st.session_state.rp_character == "Custom":
                st.session_state.custom_character = st.text_input("Describe your character:")
        
        # Game Stats
        if st.session_state.game_session:
            st.markdown("### 📊 Session Stats")
            session = st.session_state.game_session
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>Score</h4>
                    <h2>{session.score}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>Level</h4>
                    <h2>{session.level}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Session time
            elapsed = datetime.now() - session.start_time
            st.metric("Session Time", f"{elapsed.seconds // 60}m {elapsed.seconds % 60}s")
        
        # Reset button
        if st.button("🔄 New Game Session"):
            st.session_state.game_session = GameSession(game_type)
            st.rerun()
    
    # Main Game Area
    if game_type == "About":
        show_about_page()
    elif game_type == "Story Adventure":
        show_story_adventure()
    elif game_type == "Riddle Master":
        show_riddle_master()
    elif game_type == "Role Play Chat":
        show_roleplay_chat()
    elif game_type == "Word Association":
        show_word_association()

def show_about_page():
    """Display about page with app information"""
    st.markdown("""
    <div class="game-container">
        <h2>🌟 Welcome to Gemini Nexus!</h2>
        <p>Experience the future of interactive AI gaming where artificial intelligence doesn't just follow rules—it creates, adapts, and engages with you in real-time.</p>
        
        <h3>🎮 Available Games:</h3>
        <ul>
            <li><strong>Story Adventure:</strong> Embark on dynamic narratives where your choices shape the story</li>
            <li><strong>Riddle Master:</strong> Test your wit against AI-generated puzzles and brain teasers</li>
            <li><strong>Role Play Chat:</strong> Interact with AI characters in immersive scenarios</li>
            <li><strong>Word Association:</strong> Challenge your creativity in word connection games</li>
        </ul>
        
        <h3>✨ Features:</h3>
        <ul>
            <li>🧠 Adaptive AI that learns from your playstyle</li>
            <li>🎨 Beautiful dark gradient interface for comfortable gaming</li>
            <li>📊 Real-time statistics and progress tracking</li>
            <li>🎯 Multiple difficulty levels and customization options</li>
            <li>💬 Natural language interaction with advanced AI</li>
        </ul>
        
        <h3>🚀 Getting Started:</h3>
        <p>Select a game from the sidebar and dive into your AI-powered adventure. Each game offers unique challenges and experiences powered by Google's Gemini AI technology.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show demo visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4, 5],
        y=[10, 25, 40, 60, 85],
        mode='lines+markers',
        name='Engagement Level',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="AI Engagement Over Time",
        xaxis_title="Game Sessions",
        yaxis_title="Engagement Score",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_story_adventure():
    """Display story adventure game"""
    st.markdown('<div class="game-container">', unsafe_allow_html=True)
    st.markdown("## 📚 Interactive Story Adventure")
    
    if not st.session_state.game_session:
        st.session_state.game_session = GameSession("Story Adventure")
    
    story_game = st.session_state.story_game
    
    # Start new story button
    if st.button("🌟 Begin New Adventure"):
        st.session_state.ai_status = "thinking"
        with st.spinner("AI is crafting your adventure..."):
            scene = story_game.generate_scene()
            st.session_state.game_session.add_message("ai", scene)
            st.session_state.ai_status = "online"
        st.rerun()
    
    # Display conversation
    if st.session_state.game_session.messages:
        for msg in st.session_state.game_session.messages:
            role_class = "ai-message" if msg["role"] == "ai" else "user-message"
            role_icon = "🤖" if msg["role"] == "ai" else "👤"
            
            st.markdown(f"""
            <div class="chat-message {role_class}">
                <strong>{role_icon} {msg["role"].title()}:</strong><br>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # User input
    user_choice = st.text_input("Your choice or action:", key="story_input")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Choose A"):
            if user_choice:
                handle_story_input("A", story_game)
    with col2:
        if st.button("Choose B"):
            if user_choice:
                handle_story_input("B", story_game)
    with col3:
        if st.button("Choose C"):
            if user_choice:
                handle_story_input("C", story_game)
    
    if st.button("🎭 Custom Action") and user_choice:
        handle_story_input(user_choice, story_game)
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_story_input(choice, story_game):
    """Handle user input in story adventure"""
    st.session_state.game_session.add_message("user", choice)
    st.session_state.ai_status = "thinking"
    
    with st.spinner("AI is processing your choice..."):
        response = story_game.generate_scene(choice)
        st.session_state.game_session.add_message("ai", response)
        st.session_state.game_session.score += 10
        st.session_state.ai_status = "online"
    
    st.rerun()

def show_riddle_master():
    """Display riddle master game"""
    st.markdown('<div class="game-container">', unsafe_allow_html=True)
    st.markdown("## 🧩 Riddle Master Challenge")
    
    if not st.session_state.game_session:
        st.session_state.game_session = GameSession("Riddle Master")
    
    riddle_game = st.session_state.riddle_game
    
    # Generate new riddle
    if st.button("🎲 New Riddle"):
        difficulty = getattr(st.session_state, 'riddle_difficulty', 'medium')
        st.session_state.ai_status = "thinking"
        with st.spinner("AI is crafting a riddle..."):
            riddle = riddle_game.generate_riddle(difficulty)
            st.session_state.ai_status = "online"
        st.rerun()
    
    # Display current riddle
    if riddle_game.current_riddle:
        st.markdown(f"""
        <div class="chat-message ai-message">
            <strong>🧩 Riddle:</strong><br>
            {riddle_game.current_riddle}
        </div>
        """, unsafe_allow_html=True)
        
        # Answer input
        user_answer = st.text_input("Your answer:", key="riddle_answer")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit Answer") and user_answer:
                if riddle_game.check_answer(user_answer):
                    st.success("🎉 Correct! Well done!")
                    st.session_state.game_session.score += 50
                    st.session_state.game_session.level += 1
                    st.balloons()
                else:
                    st.error("❌ Not quite right. Try again!")
        
        with col2:
            if st.button("💡 Get Hint"):
                hint = riddle_game.get_hint()
                st.info(f"Hint: {hint}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_roleplay_chat():
    """Display roleplay chat game"""
    st.markdown('<div class="game-container">', unsafe_allow_html=True)
    st.markdown("## 🎭 Role Play Adventure")
    
    if not st.session_state.game_session:
        st.session_state.game_session = GameSession("Role Play Chat")
    
    roleplay_game = st.session_state.roleplay_game
    
    # Character selection
    character_type = getattr(st.session_state, 'rp_character', 'Wise Wizard')
    
    if character_type == "Custom":
        character_desc = getattr(st.session_state, 'custom_character', '')
        character = character_desc if character_desc else "Mysterious Character"
    else:
        character = character_type
    
    # Set scenario
    scenarios = {
        "Wise Wizard": "You are in a magical tower seeking ancient knowledge",
        "Space Captain": "Aboard a starship exploring unknown galaxies",
        "Detective": "Investigating a mysterious case in 1920s noir city",
        "Time Traveler": "Jumping between different historical periods",
        "Dragon": "In a medieval fantasy realm as an ancient dragon"
    }
    
    scenario = scenarios.get(character_type, "In an adventure scenario")
    
    # Initialize character
    if st.button("🎬 Start Roleplay"):
        roleplay_game.set_character(character, scenario)
        st.session_state.game_session.add_message("system", f"Roleplay started with {character}")
        st.rerun()
    
    # Display conversation
    for msg in roleplay_game.conversation_history:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {msg['user']}
        </div>
        <div class="chat-message ai-message">
            <strong>🎭 {character}:</strong><br>
            {msg['ai']}
        </div>
        """, unsafe_allow_html=True)
    
    # User input
    user_message = st.text_input("What do you say or do?", key="roleplay_input")
    
    if st.button("💬 Send Message") and user_message:
        st.session_state.ai_status = "thinking"
        with st.spinner(f"{character} is responding..."):
            response = roleplay_game.chat(user_message)
            st.session_state.game_session.score += 5
            st.session_state.ai_status = "online"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_word_association():
    """Display word association game"""
    st.markdown('<div class="game-container">', unsafe_allow_html=True)
    st.markdown("## 🔤 Word Association Challenge")
    
    if not st.session_state.game_session:
        st.session_state.game_session = GameSession("Word Association")
    
    word_game = st.session_state.word_game
    
    # Start game
    if st.button("🚀 Start Word Game"):
        st.session_state.ai_status = "thinking"
        with st.spinner("AI is picking a starting word..."):
            start_word = word_game.start_word_association()
            st.session_state.ai_status = "online"
            st.info(f"Starting word: **{start_word.upper()}**")
        st.rerun()
    
    # Display current word and stats
    if word_game.current_word:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Word", word_game.current_word.upper())
        with col2:
            st.metric("Score", word_game.score)
        with col3:
            st.metric("Attempts", word_game.attempts)
        
        # User input
        user_word = st.text_input("Enter an associated word:", key="word_input")
        
        if st.button("🔗 Check Association") and user_word:
            st.session_state.ai_status = "thinking"
            with st.spinner("AI is checking association..."):
                is_valid, explanation = word_game.check_association(user_word)
                st.session_state.ai_status = "online"
                
                if is_valid:
                    st.success(f"✅ Great association! {explanation}")
                    st.session_state.game_session.score += 10
                else:
                    st.error(f"❌ {explanation}")
            
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
