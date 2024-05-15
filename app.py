import streamlit as st
import string
import random
st.set_page_config(page_title="Visual Quest")


word = "Travel"
output_state = st.session_state.get("output_state", [])

def add_random_letters(input_string, target_length=12):
    # Calculate how many random letters are needed
    num_random_letters = max(0, target_length - len(input_string))
    
    # Generate random letters
    random_letters = ''.join(random.choice(string.ascii_lowercase) for _ in range(num_random_letters))
    
    # Combine with the input string
    result_string = input_string + random_letters
    print(result_string)
    return result_string.upper()

word2 =  add_random_letters("Travel")
def main():
    set_default_output_state(word)
    set_default_input_state(word)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_image()
        render_input_button()

def render_image ():
    
        st.image("sample.jpg")

def set_default_output_state(word):
    # Set default state with underscores and index values
    default_state = [{'letter': '_', 'index': i} for i in range(len(word))]
    st.session_state.setdefault("output_state", default_state)

def set_default_input_state(word):
    # Set default state with underscores and index values
    default_state = [{'letter': letter, 'index': i} for i, letter in enumerate(word2)]
    st.session_state.setdefault("input_state", default_state)

def handle_input_button(letter,indexx):
    # Find the first occurrence of "_" in the output_state state
    for index, item in enumerate(st.session_state.output_state):
        if item["letter"] == "_":
            # Replace the letter and update the button label
            st.session_state.output_state[index] = letter
            print(st.session_state.input_state[indexx]['letter'])
            st.rerun()



def render_input_button():
    num_buttons = len(st.session_state.input_state)
    num_columns = 6
    num_rows = (num_buttons + num_columns - 1) // num_columns  # Calculate number of rows

    for row_index in range(num_rows):
        columns = st.columns(num_columns)  # Create a row of columns
        for col_index in range(num_columns):
            index = row_index * num_columns + col_index  # Calculate the index of the button
            if index < num_buttons:
                item = st.session_state.input_state[index]
                button_id = f"Input_button_{index}"  # Unique ID for each button
                if item["letter"] == "_":
                    columns[col_index].button(item["letter"], type="primary", key=button_id, disabled=True)
                else:
                    if columns[col_index].button(item["letter"], type="primary", key=button_id):
                        st.session_state.input_state[index] = {"letter": "_", "index": 0}
                        handle_input_button(item, index)
























if __name__ == "__main__":
    main()
