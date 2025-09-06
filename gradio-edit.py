# Save this code as a Python file, for example: app.py

import os
import gradio as gr
from google import genai
from PIL import Image
from io import BytesIO
import time

# --- Configuration ---
# Set your GEMINI_API_KEY as an environment variable before running.
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL: GEMINI_API_KEY environment variable not found. The application will not work.")

# --- Core Logic (Modified to handle text responses) ---
def generate_image_with_gemini(prompt, source_image):
    """
    Generates content based on a prompt and image.
    Returns an image and download button if the model generates an image.
    Returns a text description if the model generates text.
    """
    if not api_key:
        raise gr.Error("GEMINI_API_KEY environment variable has not been set. Please set it and restart the application.")
    if source_image is None:
        raise gr.Error("Please upload a source image.")
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    client = genai.Client(api_key=api_key)

    try:
        model_name = "gemini-2.5-flash-image-preview"
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, source_image],
        )

        # Check for image data first
        generated_image_data = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                generated_image_data = part.inline_data.data
                break
        
        # --- NEW LOGIC: Handle either image or text ---
        if generated_image_data is not None:
            # --- Case 1: An image was returned ---
            result_image = Image.open(BytesIO(generated_image_data))
            timestamp = int(time.time())
            output_filename = f"generated_image_{timestamp}.png"
            result_image.save(output_filename)

            # Return the image, a visible download button, and hide the text box
            return (
                result_image, 
                gr.update(visible=True, value=output_filename), 
                gr.update(visible=False, value="")
            )
        else:
            # --- Case 2: No image, so we look for text ---
            text_response = "The model did not return an image or text." # Default message
            if response.candidates and response.candidates[0].content.parts:
                text_part = next((p.text for p in response.candidates[0].content.parts if p.text is not None), None)
                if text_part:
                    text_response = text_part
            
            # Return no image, hide the download button, and show the text response
            return (
                None, 
                gr.update(visible=False), 
                gr.update(visible=True, value=text_response)
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        raise gr.Error(f"An API error occurred. Details: {str(e)}")


# --- Gradio User Interface (Updated) ---
with gr.Blocks(theme=gr.themes.Soft(), title="🎨 Gemini Image & Text Analyzer") as demo:
    gr.Markdown("# 🎨 Gemini Image Editor & Analyzer")
    gr.Markdown("Upload an image, then ask to edit it OR ask a question about it (e.g., 'describe this picture').")

    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="Upload Your Image", height=400)
            prompt_box = gr.Textbox(
                label="Your Prompt",
                placeholder="Example: Make him hold a giant trophy.\nOR\nExample: Describe this scene.",
                lines=4
            )
            generate_btn = gr.Button("Generate", variant="primary")

        with gr.Column(scale=1):
            output_image = gr.Image(label="Generated Image", height=400, show_download_button=False)
            # New text box for text responses
            text_output_box = gr.Textbox(label="Model's Text Response", visible=False, lines=15, interactive=False)
            download_btn = gr.DownloadButton(label="Download Image", visible=False)

    # The outputs list now includes the new text box
    generate_btn.click(
        fn=generate_image_with_gemini,
        inputs=[prompt_box, input_image],
        outputs=[output_image, download_btn, text_output_box]
    )

if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch()