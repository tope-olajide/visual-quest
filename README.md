# Visual Quest

**Visual Quest** is an engaging word-guessing game that challenges players to identify the hidden word that connects four different images. With hundreds of levels and various areas of interest, Visual Quest is designed to entertain and educate players of all ages.


## About

Visual Quest presents players with four images that share a common theme. Players must guess the hidden word that connects these images. The game features:
- Hundreds of unique levels
- Hints and the ability to shuffle letters
- Areas of interest such as "Travel and Adventure," "Sports and Fitness," "Arts and Entertainment," "Health and Wellness," and "School and Learning"

## Setup Instructions

To run Visual Quest, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/tope-olajide/visual-quest.git
    cd visual-quest
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.streamlit/secrets.toml` file and add your API keys and connection details:
    ```toml
    OPENAI_API_KEY = ""

    [connections.snowflake]
    account = ""
    user  = ""
    password  = ""
    role  = ""
    warehouse = ""
    database  = ""
    schema= ""
    ```

4. Run the Streamlit app:
    ```sh
    streamlit run app.py
    ```

Enjoy playing Visual Quest!

## Contributing

We welcome contributions to enhance Visual Quest. Please feel free to submit pull requests and report issues.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
