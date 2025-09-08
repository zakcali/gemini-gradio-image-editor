# Save this code as a Python file, for example: app.py

import os
import gradio as gr
from google import genai
from google.genai import errors
from PIL import Image
from io import BytesIO
import tempfile
import atexit # Import atexit for robust cleanup

# --- Global list to track temporary files ---
# This list will hold the paths of all generated files for this session.
temp_files_to_clean = []

# --- Function to perform cleanup ---
def cleanup_temp_files():
    """Iterates through the global list and deletes the tracked files."""
    print(f"Cleaning up {len(temp_files_to_clean)} temporary files...")
    for file_path in temp_files_to_clean:
        try:
            os.remove(file_path)
            print(f"  - Removed: {file_path}")
        except FileNotFoundError:
            # The file might have been moved or deleted by other means
            print(f"  - Not found (already gone): {file_path}")
        except Exception as e:
            # Catch other potential errors (e.g., permissions)
            print(f"  - Error removing {file_path}: {e}")

# --- Register the cleanup function to run on script exit ---
# This will be called on normal exit and for most unhandled exceptions,
# including KeyboardInterrupt from Ctrl+C.
atexit.register(cleanup_temp_files)


# --- Configuration ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL: GEMINI_API_KEY environment variable not found.")


# --- Core Logic (Updated to track files) ---
def generate_image_with_gemini(prompt, source_image):
    if not api_key:
        raise gr.Error("GEMINI_API_KEY not set.")
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    client = genai.Client(api_key=api_key)
    api_contents = [prompt, source_image] if source_image else [prompt]

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
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                output_filepath = temp_file.name
                result_image.save(output_filepath)
            
            # --- MODIFICATION: Track the file for cleanup ---
            temp_files_to_clean.append(output_filepath)
            print(f"Created and tracking temp file: {output_filepath}")
            
            return (
                result_image, 
                gr.update(visible=True, value=output_filepath), 
                gr.update(visible=False, value=""),
                "✅ Image generated successfully!"
            )
        else:
            # (Text response logic remains the same)
            text_response = "The model did not return an image or text."
            if response.candidates and response.candidates[0].content.parts:
                text_part = next((p.text for p in response.candidates[0].content.parts if p.text is not None), None)
                if text_part:
                    text_response = text_part
            return (None, gr.update(visible=False), gr.update(visible=True, value=text_response), "✅ Text analysis complete.")
    
    except errors.APIError as e:
        print(f"Caught an API Error: {e}")
        error_message_for_ui = f"❌ API Error ({e.code}): {e.message}"
        return (
            None,                           # For output_image
            gr.update(visible=False),       # For download_btn
            gr.update(visible=False),       # For text_output_box
            error_message_for_ui            # For status_box
        )
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return (None, gr.update(visible=False), gr.update(visible=False), f"❌ An unexpected error occurred: {e}")
    
# --- Gradio User Interface ---
with gr.Blocks(theme=gr.themes.Soft(), title="🎨 Gemini Image & Text Generator") as demo:
    # (UI definition is the same as before)
    gr.Markdown("# 🎨 Gemini Image Generator & Analyzer")
    gr.Markdown("Provide a prompt to generate a new image (text-to-image), OR upload an image to edit/analyze it.")
    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="Upload an Image (Optional)", height=400)
            prompt_box = gr.Textbox(label="Your Prompt", placeholder="Text-to-Image: A photo of a cat programming on a laptop...", lines=5)
            with gr.Row():
                clear_btn = gr.Button(value="🗑️ Clear Prompt", scale=1)
                generate_btn = gr.Button("Generate", variant="primary", scale=2)
            status_box = gr.Markdown("")
        with gr.Column(scale=1):
            output_image = gr.Image(label="Generated Image", height=400, show_download_button=False)
            text_output_box = gr.Textbox(label="Model's Text Response", visible=False, lines=15, interactive=False)
            download_btn = gr.DownloadButton(label="Download Image", visible=False)

    generate_btn.click(fn=generate_image_with_gemini, inputs=[prompt_box, input_image], outputs=[output_image, download_btn, text_output_box, status_box])
    clear_btn.click(fn=lambda: ("", "Prompt cleared."), inputs=None, outputs=[prompt_box, status_box], queue=False)
    
    # --- MODIFICATION: Alternative cleanup using Gradio's own lifecycle event ---
    # This is often even better than atexit for web apps.
    # demo.unload(cleanup_temp_files, None, None)


if __name__ == "__main__":
    print("Launching Gradio interface... Press Ctrl+C to exit.")
    print("Temporary files for this session will be cleaned up automatically on exit.")
    demo.launch()