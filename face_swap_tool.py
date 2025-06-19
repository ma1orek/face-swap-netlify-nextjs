import fal_ai
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip
import os
import requests

# Your fal.ai API key
FAL_AI_API_KEY = "5618b6cf-3851-4cc1-9f43-4b1d40c74b20:3b51795bb52f6d48a909fee7017f9313"

# Initialize the fal_ai client
fal = fal_ai.Fal(key=FAL_AI_API_KEY)

def convert_video_to_gif_and_extract_audio(video_path, output_gif_path, output_audio_path):
    """
    Converts a video to a GIF and extracts its audio.
    Requires moviepy.
    """
    try:
        video_clip = VideoFileClip(video_path)
        
        # Extract audio
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_path)
        
        # Convert video to GIF
        video_clip.write_gif(output_gif_path, fps=video_clip.fps) # Preserve original FPS
        
        video_clip.close()
        audio_clip.close()
        print(f"Successfully converted '{video_path}' to '{output_gif_path}' and extracted audio to '{output_audio_path}'")
        return True
    except Exception as e:
        print(f"Error converting video to GIF or extracting audio: {e}")
        return False

def perform_face_swap_on_gif(input_gif_path, input_image_path, output_gif_path):
    """
    Performs face swap on a GIF using fal.ai easel-gifswap.
    """
    try:
        with open(input_gif_path, "rb") as gif_file, open(input_image_path, "rb") as image_file:
            inputs = {
                "input_gif": gif_file,
                "input_image": image_file
            }
            # The model is easel-ai/easel-gifswap
            result = fal.run(
                "easel-ai/easel-gifswap",
                inputs=inputs
            )
            
            # The result is a URL to the new GIF
            swapped_gif_url = result["gif"]
            
            # Download the swapped GIF
            response = requests.get(swapped_gif_url)
            if response.status_code == 200:
                with open(output_gif_path, "wb") as f:
                    f.write(response.content)
                print(f"Successfully performed face swap. Swapped GIF saved to: {output_gif_path}")
                return True
            else:
                print(f"Failed to download swapped GIF. Status code: {response.status_code}")
                return False
    except fal_ai.FalError as e:
        print(f"Fal.ai API error during face swap: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during face swap: {e}")
        return False

def combine_gif_with_audio_to_mp4(input_gif_path, input_audio_path, output_mp4_path):
    """
    Combines a GIF with an audio track into an MP4 video.
    Requires moviepy.
    """
    try:
        gif_clip = ImageSequenceClip(input_gif_path, fps=None) # moviepy will infer FPS
        audio_clip = AudioFileClip(input_audio_path)
        
        # Set the audio of the GIF clip
        final_clip = gif_clip.set_audio(audio_clip)
        
        # Ensure the duration matches (important for looping GIFs or truncated audio)
        final_clip = final_clip.set_duration(audio_clip.duration)
        
        final_clip.write_videofile(output_mp4_path, codec="libx264", audio_codec="aac")
        
        gif_clip.close()
        audio_clip.close()
        final_clip.close()
        print(f"Successfully combined '{input_gif_path}' and '{input_audio_path}' into '{output_mp4_path}'")
        return True
    except Exception as e:
        print(f"Error combining GIF with audio: {e}")
        return False

# --- Example Usage (How you would string these together in a script) ---
if __name__ == "__main__":
    # --- Step 1: Prepare your input files ---
    # In a real application, these would come from user uploads.
    # For this example, let's assume you have them locally.
    
    # Create dummy files for demonstration if they don't exist
    if not os.path.exists("input_video.mp4"):
        print("Please create a dummy 'input_video.mp4' for demonstration.")
        print("You can use a short video clip.")
        exit()

    if not os.path.exists("face_swap_image.jpg"):
        print("Please create a dummy 'face_swap_image.jpg' (or .png) for demonstration.")
        print("This should be an image containing the face you want to swap in.")
        exit()

    input_video = "input_video.mp4"
    face_image = "face_swap_image.jpg" # Or .png
    
    # --- Define intermediate and final output paths ---
    temp_gif = "temp_output_video.gif"
    temp_audio = "temp_output_audio.mp3"
    swapped_gif = "swapped_face_gif.gif"
    final_output_mp4 = "final_video_with_swapped_face.mp4"

    # --- Step 2: Convert video to GIF and extract audio ---
    print("\n--- Step 2: Converting video to GIF and extracting audio ---")
    if convert_video_to_gif_and_extract_audio(input_video, temp_gif, temp_audio):
        # --- Step 3: Perform Face Swap on the GIF ---
        print("\n--- Step 3: Performing Face Swap on the GIF ---")
        if perform_face_swap_on_gif(temp_gif, face_image, swapped_gif):
            # --- Step 4: Combine the swapped GIF with the extracted audio ---
            print("\n--- Step 4: Combining swapped GIF with audio to MP4 ---")
            if combine_gif_with_audio_to_mp4(swapped_gif, temp_audio, final_output_mp4):
                print(f"\nProcess completed successfully! Final video: {final_output_mp4}")
            else:
                print("\nFailed to combine GIF with audio.")
        else:
            print("\nFailed to perform face swap.")
    else:
        print("\nFailed to convert video or extract audio.")

    # --- Clean up temporary files (optional) ---
    # Uncomment these lines if you want to remove the intermediate files
    # if os.path.exists(temp_gif):
    #     os.remove(temp_gif)
    # if os.path.exists(temp_audio):
    #     os.remove(temp_audio)
    # if os.path.exists(swapped_gif):
    #     os.remove(swapped_gif)