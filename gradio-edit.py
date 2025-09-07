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

# --- Core Logic (Unchanged from previous version) ---
def generate_image_with_gemini(prompt, source_image):
    """
    Generates content based on a prompt.
    - If only a prompt is given, performs text-to-image generation.
    - If a prompt and image are given, performs image editing or analysis.
    Returns an image and download button if the model generates an image.
    Returns a text description if the model generates text.
    """
    if not api_key:
        raise gr.Error("GEMINI_API_KEY environment variable has not been set. Please set it and restart the application.")
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    client = genai.Client(api_key=api_key)

    if source_image is None:
        api_contents = [prompt]
    else:
        api_contents = [prompt, source_image]

    try:
        model_name = "gemini-2.5-flash-image-preview"
        response = client.models.generate_content(
            model=model_name,
            contents=api_contents,
        )

        generated_image_data = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                generated_image_data = part.inline_data.data
                break
        
        if generated_image_data is not None:
            result_image = Image.open(BytesIO(generated_image_data))
            timestamp = int(time.time())
            output_filename = f"generated_image_{timestamp}.png"
            result_image.save(output_filename)
            return (
                result_image, 
                gr.update(visible=True, value=output_filename), 
                gr.update(visible=False, value="")
            )
        else:
            text_response = "The model did not return an image or text."
            if response.candidates and response.candidates[0].content.parts:
                text_part = next((p.text for p in response.candidates[0].content.parts if p.text is not None), None)
                if text_part:
                    text_response = text_part
            return (
                None, 
                gr.update(visible=False), 
                gr.update(visible=True, value=text_response)
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        raise gr.Error(f"An API error occurred. Details: {str(e)}")


# --- Gradio User Interface (Updated with a clear button) ---
with gr.Blocks(theme=gr.themes.Soft(), title="🎨 Gemini Image & Text Generator") as demo:
    gr.Markdown("# 🎨 Gemini Image Generator & Analyzer")
    gr.Markdown("Provide a prompt to generate a new image (text-to-image), OR upload an image to edit/analyze it.")

    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="Upload an Image (Optional)", height=400)
            prompt_box = gr.Textbox(
                label="Your Prompt",
                placeholder="Text-to-Image: A photo of a cat programming on a laptop.\n\nImage Editing: Remove the background.\n\nImage Analysis: Describe this scene.",
                lines=5
            )
            # --- MODIFICATION START: Add a Row for the buttons ---
            with gr.Row():
                clear_btn = gr.Button(value="🗑️ Clear Prompt", scale=1)
                generate_btn = gr.Button("Generate", variant="primary", scale=3)
            # --- MODIFICATION END ---

        with gr.Column(scale=1):
            output_image = gr.Image(label="Generated Image", height=400, show_download_button=False)
            text_output_box = gr.Textbox(label="Model's Text Response", visible=False, lines=15, interactive=False)
            download_btn = gr.DownloadButton(label="Download Image", visible=False)

    # Event handler for the main generate button
    generate_btn.click(
        fn=generate_image_with_gemini,
        inputs=[prompt_box, input_image],
        outputs=[output_image, download_btn, text_output_box]
    )

    # --- MODIFICATION START: Add event handler for the new clear button ---
    clear_btn.click(
        fn=lambda: "",           # The function to run is a simple lambda that returns an empty string
        inputs=None,             # No inputs are needed for this function
        outputs=[prompt_box],    # The component to update is the prompt_box
        queue=False              # Run instantly in the browser without queuing
    )
    # --- MODIFICATION END ---

if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch()