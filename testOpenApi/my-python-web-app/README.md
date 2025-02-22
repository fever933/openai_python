# My Python Web App

This project is a simple web application built using Flask that integrates with the OpenAI API to provide a streaming interface for user queries.

## Project Structure

```
my-python-web-app
├── src
│   ├── app.py            # Main application file
│   ├── templates
│   │   └── index.html    # HTML template for the web interface
│   └── static
│       └── styles.css     # CSS styles for the web interface
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd my-python-web-app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key:**
   Make sure to set your OpenAI API key in your environment variables or directly in the `app.py` file.

## Usage

1. **Run the application:**
   ```bash
   python src/app.py
   ```

2. **Access the web interface:**
   Open your web browser and navigate to `http://127.0.0.1:5000`.

3. **Interact with the application:**
   Use the input form to submit your queries and receive streamed responses from the OpenAI API.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.