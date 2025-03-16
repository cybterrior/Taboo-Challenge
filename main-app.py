import streamlit as st
import requests
import json
import random
import time

# Page configuration
st.set_page_config(
    page_title="AI Taboo Challenge",
    page_icon="🤖",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .game-title {
        color: #FF5F1F;
        text-align: center;
        font-size: 3rem !important;
        margin-bottom: 0 !important;
        text-shadow: 2px 2px 4px #cccccc;
    }
    .subtitle {
        color: #39be17;
        text-align: center;
        font-size: 1.9rem !important;
        margin-bottom: 0.5rem !important;
        
    }
    .header-container {
        background-color: #432411;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .score-display {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
    }
    .target-word {
        background-color: #e6f7ff;
        padding: 15px;
        border-radius: 10px;
        font-size: 1.8rem;
        font-weight: bold;
        color: #003366;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .taboo-words {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
    }
    .taboo-word {
        background-color: #ff6b6b;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
    }
    .emoji-celebration {
        font-size: 3rem;
        text-align: center;
    }
    .funny-message {
        text-align: center;
        font-size: 1.2rem;
        color: #ff4500;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# API setup Using Mistral AI
MISTRAL_API_KEY = "3SEmEMRvlZouWdr85cQxJAgdwSmMSxzw"  # Replace with your actual API key
# MISTRAL_API_KEY = st.secrets["mistral_api_key"]
mistral_api_url = "https://api.mistral.ai/v1/chat/completions"


# Fun emojis for the game
emojis = ["🤖", "💻", "🧠", "🚀", "🎮", "🧩", "🎲", "🎰", "🎡", "🎢"]
success_emojis = ["🎉", "🎊", "🥳", "🎈", "🎁", "👏", "✨", "🌟", "⭐", "🔥"]
fail_emojis = ["😮", "🤔", "🧐", "🤨", "😵", "🙄", "😬", "🤦", "😅", "😯"]

# Silly motivational messages
motivational_messages = [
    "You're doing great! (At least better than my ex's coding)",
    "Your clue was... interesting? Keep trying!",
    "Are you a professional at this useless game? Wow!",
    "Not bad for a human! The robots are still watching though...",
    "Your creativity is... something. Not sure what, but something!",
    "If this was a real job, you'd be promoted to 'Senior Clue Giver'",
    "The AI is confused, but so am I!",
    "Keep going! Your persistence is almost as strong as my coffee",
    "That clue was so good, even the computer is jealous!",
    "You're putting the 'fun' in 'dysfunctional game'!",
]

# Game data
words = [
    {"target": "Firewall", "taboo": ["Security", "Network", "Protection", "Block", "Traffic", "Filter"]},
    {"target": "Algorithm", "taboo": ["Logic", "Steps", "Sort", "Function", "Process", "Data"]},
    {"target": "Encryption", "taboo": ["Secure", "Cipher", "Key", "Decrypt", "Data", "Encode"]},
    {"target": "Cloud", "taboo": ["Storage", "Internet", "Server", "AWS", "Google", "Backup"]},
    {"target": "Phishing", "taboo": ["Scam", "Email", "Fraud", "Cybercrime", "Fake", "Identity"]},
    {"target": "Malware", "taboo": ["Virus", "Trojan", "Worm", "Spyware", "Infect", "Hacker"]},
    {"target": "Blockchain", "taboo": ["Bitcoin", "Crypto", "Ledger", "Decentralized", "Mining", "Hash"]},
    {"target": "Router", "taboo": ["Wi-Fi", "Internet", "Network", "LAN", "Wireless", "Signal"]},
    {"target": "Hacker", "taboo": ["Cyber", "Penetrate", "Exploit", "Security", "Anonymous", "Ethical"]},
    {"target": "Quantum", "taboo": ["Computing", "Bits", "Qubit", "Physics", "Speed", "Future"]},
    {"target": "API", "taboo": ["Interface", "Request", "Server", "Connect", "Data", "Endpoint"]},
    {"target": "Database", "taboo": ["SQL", "Records", "Store", "Query", "Table", "Retrieve"]},
]

# Difficulty settings
difficulty_settings = {
    "Easy": {"total_time": 180, "description": "3 minutes total"},
    "Medium": {"total_time": 120, "description": "2 minutes total"},
    "Hard": {"total_time": 90, "description": "1.5 minutes total"}
}

# Function to get AI's guess using Mistral
def get_ai_guess(clue):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }

    payload = {
        "model": "mistral-small",  # preferred Mistral model
        "messages": [
            {
                "role": "user",
                "content": f"Guess the word based on this clue: {clue}. Reply with just the word you're guessing, nothing else."
            }
        ],
        "max_tokens": 10,
        "temperature": 0.7
    }

    try:
        response = requests.post(mistral_api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        # first_word = result["choices"][0]["message"]["content"].strip().split()[0] 
        return result["choices"][0]["message"]["content"].strip().split()[0].replace(".", "")
    except Exception as e:
        st.error(f"Error calling Mistral AI: {str(e)}")
        return "API Error"

# Session state initialization
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_word_index" not in st.session_state:
    st.session_state.current_word_index = 0
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 6
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"
if "round_results" not in st.session_state:
    st.session_state.round_results = []
if "emoji" not in st.session_state:
    st.session_state.emoji = random.choice(emojis)
if "word_order" not in st.session_state:
    st.session_state.word_order = list(range(len(words)))
    random.shuffle(st.session_state.word_order)
if "game_completed" not in st.session_state:
    st.session_state.game_completed = False

# Function to get the current word data
def get_current_word():
    index = st.session_state.word_order[st.session_state.current_word_index % len(words)]
    return words[index]

# Function to increase number of questions
def increase_questions():
    st.session_state.num_questions += 1

# Function to decrease number of questions
def decrease_questions():
    if st.session_state.num_questions > 1:
        st.session_state.num_questions -= 1

# Function to move to next word
def next_word():
    st.session_state.current_word_index += 1

    # Check if game is completed
    if st.session_state.current_word_index >= st.session_state.num_questions:
        st.session_state.game_completed = True

    st.session_state.emoji = random.choice(emojis)

# Welcome window
if not st.session_state.game_started:
    st.markdown(f"<h1 class='game-title'>Welcome to AI Taboo Challenge! {random.choice(emojis)}</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class='header-container'>
            <p class='subtitle'>Can you outsmart the AI in this word game?</p>
            <p class='subtitle'>Using Your Silly Prompts!!!</p>
            <p style='text-align: center;'>Give clues to help the AI guess words, but avoid using the taboo words!</p>
            <p style='text-align: center;'>The more words the AI guesses correctly, the higher your score!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("What should we call you, word master?", placeholder="Enter your name")

        # Difficulty settings
        difficulty = st.select_slider(
            "Choose difficulty:",
            options=["Easy", "Medium", "Hard"],
            value="Medium"
        )

        # Display difficulty info
        st.markdown(f"<div class='difficulty-info'>{difficulty_settings[difficulty]['description']}</div>", unsafe_allow_html=True)

        # Number of questions control
        st.markdown("<div style='margin: 15px 0 5px 0;'>Number of questions:</div>", unsafe_allow_html=True)

        col_minus, col_num, col_plus = st.columns([1, 1, 1])
        with col_minus:
            st.button("➖", key="decrease", on_click=decrease_questions, use_container_width=True)
        with col_num:
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{st.session_state.num_questions}</div>", unsafe_allow_html=True)
        with col_plus:
            st.button("➕", key="increase", on_click=increase_questions, use_container_width=True)

        if st.button("Let's Play! 🎮", type="primary", use_container_width=True):
            if username:
                st.session_state.username = username
                st.session_state.difficulty = difficulty
                st.session_state.game_started = True

                # Make sure we have a fresh shuffle
                st.session_state.word_order = list(range(len(words)))
                random.shuffle(st.session_state.word_order)
                st.rerun()
            else:
                st.error("Please enter your name to start!")

# Game completed screen
elif st.session_state.game_completed:
    st.markdown(f"<h1 class='game-title'>Game Completed! {random.choice(success_emojis)}</h1>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='header-container'>
            <p class='subtitle'>Well done, {st.session_state.username}!</p>
            <p style='text-align: center; font-size: 2rem; font-weight: bold; margin: 20px 0;'>
                Final Score: {st.session_state.score}/{st.session_state.num_questions}
            </p>
            <p style='text-align: center;'>
                You completed the game on {st.session_state.difficulty} difficulty.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display game history
    if st.session_state.round_results:
        st.markdown("### 📝 Game History")
        history_df = st.dataframe(
            {
                "Word": [r["word"] for r in st.session_state.round_results],
                "Your Clue": [r["clue"] for r in st.session_state.round_results],
                "AI's Guess": [r["guess"] for r in st.session_state.round_results],
                "Result": ["✅ Correct!" if r["correct"] else "❌ Wrong" for r in st.session_state.round_results]
            },
            hide_index=True
        )

    # Play again button
    if st.button("Play Again", type="primary"):
        st.session_state.score = 0
        st.session_state.current_word_index = 0
        st.session_state.round_results = []
        st.session_state.game_completed = False
        st.session_state.word_order = list(range(len(words)))
        random.shuffle(st.session_state.word_order)
        st.rerun()

    # Return to main menu
    if st.button("Return to Main Menu", type="secondary"):
        st.session_state.game_started = False
        st.session_state.game_completed = False
        st.session_state.score = 0
        st.session_state.current_word_index = 0
        st.session_state.round_results = []
        st.rerun()

# Main game screen
else:
    # Header with score
    st.markdown(f"<h1 class='game-title'>AI Taboo Challenge {st.session_state.emoji}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>Player: {st.session_state.username} | Difficulty: {st.session_state.difficulty}</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<div class='score-display'>Score: {st.session_state.score}/{st.session_state.num_questions}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'>Question {st.session_state.current_word_index + 1} of {st.session_state.num_questions}</div>", unsafe_allow_html=True)

    # Show current word and taboo words
    current_data = get_current_word()

    st.markdown(f"<div class='target-word'>🎯 Target Word: {current_data['target']}</div>", unsafe_allow_html=True)

    # Display taboo words
    taboo_html = "<div class='taboo-words'>"
    for word in current_data['taboo']:
        taboo_html += f"<span class='taboo-word'>❌ {word}</span>"
    taboo_html += "</div>"
    st.markdown(taboo_html, unsafe_allow_html=True)

    # Input for player's clue
    st.markdown(
    "<h4 style='font-size:18px;'>Hint: I guard the digital gates. What am I?- Firewall</h4>", 
    unsafe_allow_html=True
    )

    clue = st.text_input("Enter your clue (avoid taboo words):", key="clue_input",
                         placeholder="Give a clever hint without using taboo words...")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Submit Clue", type="primary", use_container_width=True):
            if not clue:
                st.error("Please enter a clue first!")
            # Check if clue contains taboo words
            elif any(taboo.lower() in clue.lower() for taboo in current_data["taboo"]):
                st.error(f"{random.choice(fail_emojis)} Oops! You used a taboo word! Try again.")
            else:
                # Get AI's guess
                with st.spinner("AI is thinking..."):
                    ai_guess = get_ai_guess(clue)

                # Record results
                result = {
                    "word": current_data["target"],
                    "clue": clue,
                    "guess": ai_guess,
                    "correct": ai_guess.lower() == current_data["target"].lower()
                }
                st.session_state.round_results.append(result)

                # Check if AI guessed correctly
                if ai_guess.lower() == current_data["target"].lower():
                    st.session_state.score += 1
                    st.markdown(f"<div class='emoji-celebration'>{random.choice(success_emojis)}</div>", unsafe_allow_html=True)
                    st.success(f"Amazing! AI guessed '{ai_guess}' correctly!")
                else:
                    st.markdown(f"<div class='emoji-celebration'>{random.choice(fail_emojis)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='funny-message'>{random.choice(motivational_messages)}</div>", unsafe_allow_html=True)
                    st.error(f"AI guessed '{ai_guess}' instead of '{current_data['target']}'.")

                time.sleep(3)
                next_word()
                time.sleep(1.5)
                st.rerun()

    with col2:
        if st.button("Skip This Word", type="secondary", use_container_width=True):
            next_word()
            st.rerun()

    # Restart game button
    if st.button("Restart Game", type="secondary"):
        st.session_state.score = 0
        st.session_state.current_word_index = 0
        st.session_state.round_results = []
        st.session_state.game_completed = False

        # Shuffle words again
        st.session_state.word_order = list(range(len(words)))
        random.shuffle(st.session_state.word_order)
        st.rerun()
