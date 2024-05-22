import json
import string
import random
import streamlit as st
import openai
from PIL import Image
import io, base64

# Initialize Snowflake connection
conn = st.connection("snowflake")
session = conn.session()

# OpenAI API key setup
open_ai_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = open_ai_key

# Initialize session state variables
if 'quest_solution' not in st.session_state:
    st.session_state.quest_solution = ""

if 'hint' not in st.session_state:
    st.session_state.hint = ""

if 'is_fetching_quest' not in st.session_state:
    st.session_state.is_fetching_quest = False

if 'input_state' not in st.session_state:
    st.session_state.input_state = []

if 'solution_with_random_letters' not in st.session_state:
    st.session_state.solution_with_random_letters = ""

if 'output_state' not in st.session_state:
    st.session_state.output_state = []

if 'is_game_started' not in st.session_state:
    st.session_state.is_game_started = False

if 'is_solution_found' not in st.session_state:
    st.session_state.is_solution_found = False

if 'is_hint_locked' not in st.session_state:
    st.session_state.is_hint_locked = True
    
if 'coins' not in st.session_state:
    st.session_state.coins = 1000

if 'exclude_list' not in st.session_state:
    st.session_state.exclude_list = ['jump']
    
if 'stage' not in st.session_state:
    st.session_state.stage = 1
    
if 'encouraging_word' not in st.session_state:
    st.session_state.encouraging_words = []

if 'category' not in st.session_state:
    st.session_state.category = ""

def add_random_letters(target_length=12):
    num_random_letters = max(0, target_length - len(st.session_state.quest_solution))
    random_letters = ''.join(random.choice(string.ascii_lowercase) for _ in range(num_random_letters))
    result_string = st.session_state.quest_solution + random_letters
    st.session_state.solution_with_random_letters = result_string.upper()
    s_list = list(result_string)
    random.shuffle(s_list)
    shuffled_string = ''.join(s_list)
    new_input_state = [{'letter': letter, 'index': i} for i, letter in enumerate(shuffled_string.upper())]
    st.session_state.input_state = new_input_state

def count_output_underscores():
    return sum(1 for item in st.session_state.output_state if item["letter"] == "_")


def create_word_and_check(input_array):
    letters = [item["letter"] for item in input_array]
    word = "".join(letters)
    if word.lower() == st.session_state.quest_solution.lower():
        st.session_state.is_solution_found = True
        calculate_coins()

def handle_input_button(letter, indexx):
    for index, item in enumerate(st.session_state.output_state):
        if item["letter"] == "_":
            st.session_state.output_state[index] = {"letter": letter["letter"], "index": letter["index"]}
            create_word_and_check(st.session_state.output_state)
            break
    st.rerun()  # Trigger rerun to immediately reflect state changes

def render_input_buttons():
    num_buttons = len(st.session_state.input_state)
    num_columns = 6
    num_rows = (num_buttons + num_columns - 1) // num_columns
    for row_index in range(num_rows):
        columns = st.columns(num_columns)
        for col_index in range(num_columns):
            index = row_index * num_columns + col_index
            if index < num_buttons:
                item = st.session_state.input_state[index]
                button_id = f"Input_button_{index}"
                if item["letter"] == "_":
                    columns[col_index].button(item["letter"], key=button_id, disabled=True)
                else:
                    output_underscore_count = count_output_underscores()
                    if columns[col_index].button(item["letter"], type="primary", key=button_id) and output_underscore_count != 0:
                        st.session_state.input_state[index] = {"letter": "_", "index": item["index"]}
                        handle_input_button(item, index)
                        
def handle_output_button(index):
    position = st.session_state.output_state[index]["index"]
    #st.session_state.input_state[index] = st.session_state.output_state[index]
    st.session_state.input_state[position] = st.session_state.output_state[index]
    st.session_state.output_state[index] = {"letter":"_", "index":0}
    st.rerun()
    
def render_output_buttons():
    columns = st.columns(len(st.session_state.output_state))
    for index, item in enumerate(st.session_state.output_state):
        button_id = f"button_{index}"
        if item["letter"] == "_":
            columns[index].button(item["letter"], key=button_id, disabled=True)
        else:
            if columns[index].button(item['letter'], key=button_id):
                handle_output_button(index)

def render_solution_buttons():
    columns = st.columns(len(st.session_state.quest_solution))
    for index, item in enumerate(st.session_state.quest_solution.upper()):
        button_id = f"solution_button_{index}"
        if columns[index].button(item, key=button_id):
            pass

def prompt_quest():
    array_string = json.dumps(st.session_state.exclude_list)
    prompt = f"Generate a random action verb or noun (4-7 letters) related to {st.session_state.catgegory}.  Avoid technical terms. Aim for tangible actions. The word must not be in this list: {array_string}. Provide a hint. Must be in JSON format with word and hint as keys."
    cortex_prompt = "'[INST] " + prompt + " [/INST]'"
    print(prompt)
    cortex_response = session.sql(f"select snowflake.cortex.complete('snowflake-arctic', {cortex_prompt}) as response").to_pandas().iloc[0]['RESPONSE']
    data = json.loads(cortex_response)
    word = data['word']
    hint = data['hint']
    st.session_state.quest_solution = word
    st.session_state.exclude_list.append(word)
    st.session_state.hint = hint
    new_output_state = [{'letter': '_', 'index': i} for i in range(len(st.session_state.quest_solution))]
    st.session_state.output_state = new_output_state
    print(f"#####{st.session_state.exclude_list}")
    generate_image(word)

def generate_image(word):
    prompt = f"Generate an image with four different collages, each representing the word '{word}'"
    response = openai.Image.create(
        prompt=prompt,
        model="dall-e-3",
        n=1,
        size="1024x1024",
        response_format="b64_json",
    )
    image_data = response['data'][0]['b64_json']
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))
    img.save('quest-image.jpeg')
    st.session_state.is_fetching_quest = False

def start_game():
    with st.spinner('Loading...'):
        prompt_quest()
        add_random_letters()
        st.session_state.is_game_started = True
        st.session_state.encouraging_word = get_encouraging_word()
        st.rerun()
        

def shuffle_input():
    s_list = list(st.session_state.solution_with_random_letters)
    random.shuffle(s_list)
    shuffled_string = ''.join(s_list) 
    new_output_state = [{'letter': '_', 'index': i} for i in range(len(st.session_state.quest_solution))]
    new_input_state = [{'letter': letter, 'index': i} for i, letter in enumerate(shuffled_string)]
    st.session_state.input_state = new_input_state
    st.session_state.output_state = new_output_state
    st.rerun()

def unlock_hint ():
    if st.session_state.coins < len(st.session_state.quest_solution)*50:
        insufficient_fund()
    else: sufficient_fund()
        
@st.experimental_dialog("Unlock hint")
def insufficient_fund():
    st.write(f"You do not have enough coins to unlock hint")

@st.experimental_dialog("Unlock hint")
def sufficient_fund():
    coins = len(st.session_state.quest_solution) * 50
    st.write(f"-{coins}🪙 will be deducted from your balance. Do you want to continue?")
    if st.button("Yes"):
        st.session_state.coins = st.session_state.coins - coins
        st.session_state.is_hint_locked = False
        st.rerun()

def calculate_coins():
    coins = len(st.session_state.quest_solution) * 100
    st.session_state.coins = st.session_state.coins + coins

def get_encouraging_word():
    words = [
        "Excellent",
        "Very good",
        "Awesome",
        "Great job",
        "Fantastic",
        "Well done",
        "Superb",
        "Amazing",
        "Brilliant",
        "Outstanding"
    ]
    return random.choice(words)

@st.experimental_dialog("Settings")
def display_settings():
    with st.container(border=True):
        option = st.selectbox(
    "Choose a Category",
    ("Travel and Adventure", "Sports and Fitness", "Arts and Entertainment", "Health and Wellness", "School and Learning" ))
    st.session_state.catgegory = option
    
    
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([2, 1.2, 2])
    with col2:
            if st.button('Save 💾'):
                st.rerun()

@st.experimental_dialog("How to play")
def how_to_play():
    st.markdown("""
    **How to Play: **

    🎮 **Step 1: Observe**
    - **🔍 Look Closely:** Each level presents four stunning images.
    - **🌟 Spot the Connection:** Find the common theme!

    🎮 **Step 2: Guess**
    - **🧠 Form the Word:** Use the letters to guess the hidden word.
    - **🔠 Tap Away:** Tap letters to form your word. Mistakes? Letters reset for another try.

    🎮 **Step 3: Use Hints**
    - **💡 Stuck? No Problem!** Tap hints to reveal letters or remove unnecessary ones.
    - **🎯 Strategize:** Use hints wisely to conquer tough puzzles.

    🎮 **Step 4: Shuffle Letters**
    - **🔄 Fresh Perspective:** Shuffle letters to see them in a new way. A fresh arrangement can reveal the answer!
    """)


@st.experimental_dialog("About VQ")
def about_vq():
    st.markdown("""
    **About Visual Quest**

    🌟 **Welcome to Visual Quest!**

    Dive into an addictive word-guessing game that challenges your puzzle-solving skills and sharpens your mind. Explore hundreds of levels filled with beautiful image collages, each hiding a word that connects all four pictures.

    **Game Features:**
    - **🧩 Hundreds of Levels:** Keep your brain buzzing with endless puzzles.
    - **🖼️ Beautiful Collages:** Enjoy high-quality images with each level.
    - **💡 Hints and Shuffles:** Use hints to reveal letters and shuffle for a fresh perspective.

    **Why You'll Love It:**
    - **📚 Educational Fun:** Enhance your vocabulary and cognitive skills.
    - **🎉 Engaging Gameplay:** Perfect for quick breaks or long sessions.
    - **👨‍👩‍👧‍👦 Family-Friendly:** Fun for all ages.

    """)

def main():
    if not st.session_state.is_game_started:
        col1, col2, col3 = st.columns([1, 1.1, 1])
        with col2:
            st.title('_Visual_ :blue[Quest]')
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 5, 1])
                with col2:
                    with st.container(border=True):
                        if st.button('Play Game', type="primary"):
                            start_game()     
                    with st.container(border=True):
                        if st.button("About 💁"):
                            about_vq()
                    with st.container(border=True):
                        if st.button("Settings ⚙"):
                            display_settings()
                    with st.container(border=True):
                        if st.button("How To Play", type="primary"):
                            how_to_play()
    else:
        if not st.session_state.is_solution_found:
            col1, col2, col3 = st.columns([1, 1.5, 1])
            with col2:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        st.write(f"🪙{st.session_state.coins}")
                    with col3:
                        st.write(f"stage: {st.session_state.stage}")
                    
                    with st.container(border=True):
                        render_output_buttons()
                
                        st.image("quest-image.jpeg")
                    
                        col1, col3 = st.columns([5.5, 3.1])
                        with col3:
                            if st.button("Shuffle"):
                                shuffle_input()
                        with col1:
                            if st.session_state.is_hint_locked == False:
                                st.write(f"💡: {st.session_state.hint}")
                            else:
                                if st.button("HINT?💡"):
                                    unlock_hint()
                                
                    with st.container(border=True):
                        render_input_buttons()
                    
                       
        if st.session_state.is_solution_found == True:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                       
                        st.subheader(F":rainbow[{st.session_state.encouraging_word}]!!")
                    st.image("giphy.gif")
                    
                    with st.container(border=True):
                        render_solution_buttons()
                    st.write("")     
                    col1, col2, col3 = st.columns([1, 0.7, 1])
                    with col1:
                        st.subheader(f"+ {len(st.session_state.quest_solution)*100}🪙")
                    with col3:
                            
                        if st.button('Next Quest', key="Load_Next_Quest_Button", type="primary"):
                            st.session_state.is_solution_found = False
                            st.session_state.is_hint_locked = True
                            st.session_state.stage = st.session_state.stage + 1
                            start_game()
                            st.rerun()
                        st.write("")    
                        st.write("")    
                        
                    
if __name__ == "__main__":
    main()
