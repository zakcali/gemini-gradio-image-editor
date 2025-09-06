# Gemini Gradio Image Editor & Analyzer

A Gradio web interface that uses the Google Gemini API to perform powerful AI-based image editing and analysis. This tool can transform your photos into different art styles, add or remove objects, or simply provide a detailed text description of an image.


*Example: Make him hold a giant trophy.* OR *Describe this scene*

## Features

*   **AI Image Editing**: Provide an image and a text prompt (e.g., "Make this a watercolor painting," "add a superhero cape to the person") to generate a new version of your image.
*   **AI Image Analysis**: Ask questions about an image (e.g., "describe this scene in detail," "what kind of event is this?") to receive a textual analysis from the AI.
*   **Dual-Mode Interface**: The UI intelligently displays either the generated image (with a download button) or the generated text, depending on the model's response.
*   **Simple & Clean UI**: Built with Gradio for a straightforward and responsive user experience.

## Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/zakcali/gemini-gradio-image-editor.git
    cd gemini-gradio-image-editor
    ```

2.  Install the required packages. It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

    Your `requirements.txt` file should contain:
    ```
    gradio
    google-genai
    pillow
    ```

## Configuration

Before running the application, you must set your Google Gemini API key as an environment variable. You can get a key from [Google AI Studio](https://aistudio.google.com/).

```bash
# On macOS or Linux
export GEMINI_API_KEY="YOUR_API_KEY_HERE"

# On Windows
set GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

## Running the Application

Run the main script from your terminal:
```bash
python gradio-edit.py
```

The application can be launched in several ways:

### To run locally on your machine:
The script defaults to this. Gradio will provide a local URL like `http://127.0.0.1:7860`.
```python
demo.launch()
```

### To serve to other devices on your local network (LAN):
Modify the last line in the script to include your machine's local IP address.
```python
# Replace "192.168.1.XX" with your actual LAN IP address
demo.launch(server_name="192.168.1.XX", server_port=7860)
```

### To share publicly over the internet:
Set the `share` parameter to `True`. Gradio will generate a temporary public URL for you.
```python
demo.launch(share=True)
```
For more details, see the official Gradio guide on [Sharing Your App](https://www.gradio.app/guides/sharing-your-app).

## How It Works

This application sends the user-uploaded image and text prompt to the Gemini API, specifically using the `gemini-2.5-flash-image-preview` model. As of 6 Sep 2025, this is *Nano Banana* model. The Gemini model is multimodal and can understand both the image and the text context.

Based on the prompt, it will either:
1.  Return a new image as `inline_data`, which the script then saves as a PNG file and displays.
2.  Return a `text` response, which the script displays in a separate text box.

The script gracefully handles both response types, making it a versatile tool for both creative editing and analytical tasks.
