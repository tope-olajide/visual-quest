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
        render_output_button()
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
                    output_underscore_count = count_underscores()
                    if columns[col_index].button(item["letter"], type="primary", key=button_id) and output_underscore_count != 0:
                        print(row_index)
                        print(len(st.session_state.output_state))
                        st.session_state.input_state[index] = {"letter": "_", "index": 0}
                        handle_input_button(item, index)


def render_output_button():
    columns = st.columns(len(st.session_state.output_state))
    for index, item in enumerate(st.session_state.output_state):
        button_id = f"button_{index}"  # Unique ID for each button
        if item["letter"] == "_":
            columns[index].button(item["letter"], type="primary", key=button_id, disabled=True)
        else:
            if columns[index].button(item['letter'], key=button_id):
                handle_output_button(index)

def handle_output_button(index):
    position = st.session_state.output_state[index]["index"]
    print(st.session_state.output_state[index])
    #st.session_state.input_state[index] = st.session_state.output_state[index]
    st.session_state.input_state[position] = st.session_state.output_state[index]
    st.session_state.output_state[index] = {"letter":"_", "index":0}
    st.rerun()

def count_underscores():
    print(sum(1 for item in st.session_state.output_state if item["letter"] == "_"))
    return sum(1 for item in st.session_state.output_state if item["letter"] == "_")  





















if __name__ == "__main__":
    main()
