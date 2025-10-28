import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary with credentials from environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def upload_to_cloudinary(file_path: str) -> str:
    """
    Uploads a video file to Cloudinary and returns its public URL.

    Args:
        file_path (str): The local path to the video file.

    Returns:
        str: The public URL of the uploaded video.

    Raises:
        Exception: If the upload fails.
    """
    try:
        # Upload the video to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            # Transformations can be added here if needed in the future
            # For example: eager=[
            #     {"width": 300, "height": 300, "crop": "pad", "audio_codec": "none"},
            #     {"width": 160, "height": 100, "crop": "crop", "gravity": "south", "audio_codec": "none"}
            # ]
        )
        return upload_result.get("secure_url")
    except Exception as e:
        # Handle potential errors during the upload
        print(f"Error uploading to Cloudinary: {e}")
        raise
