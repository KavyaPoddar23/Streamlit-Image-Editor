import streamlit as st
from rembg import remove
from PIL import Image, ImageOps, ImageEnhance, ImageStat, ImageFilter, ImageDraw, ImageFont
from io import BytesIO
import base64

st.set_page_config(layout="wide", page_title="Enhanced Image Background Remover")

st.write("## Remove Background & Edit Your Image")
st.write(
    "Try uploading an image to watch the background magically removed. "
    "You can also rotate, crop, resize, adjust brightness, contrast, sharpness, apply blur, add text, and replace the background. "
    "Full quality images can be downloaded from the sidebar.")
st.sidebar.write("## Upload, Edit, and Download :gear:")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# Function to check if contrast adjustment is safe
def safe_contrast_adjustment(image, contrast):
    stat = ImageStat.Stat(image)
    if all(v == 0 for v in stat.sum):  # Check if image is completely black
        return image  # Skip contrast adjustment
    return ImageEnhance.Contrast(image).enhance(contrast)

# Function to remove background and apply customizations
def fix_image(upload, rotate_angle, crop_values, resize_width, resize_height, brightness, contrast, sharpness, blur_radius, text, text_position, background_image):
    image = Image.open(upload).convert("RGBA")  # Ensure RGBA mode
    col1.write("Original Image :camera:")
    col1.image(image)

    # Apply rotation
    if rotate_angle != 0:
        image = image.rotate(rotate_angle, expand=True)
    
    # Apply cropping
    if all(v is not None for v in crop_values):
        left, top, right, bottom = crop_values
        image = image.crop((left, top, right, bottom))
    
    # Apply resizing
    if resize_width > 0 and resize_height > 0:
        image = image.resize((resize_width, resize_height))
    
    # Apply brightness adjustment
    image = ImageEnhance.Brightness(image).enhance(brightness)
    
    # Apply contrast adjustment safely
    image = safe_contrast_adjustment(image, contrast)
    
    # Apply sharpness adjustment
    image = ImageEnhance.Sharpness(image).enhance(sharpness)
    
    # Apply blur effect
    if blur_radius > 0:
        image = image.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Remove background
    fixed = remove(image)
    
    # Apply background replacement
    if background_image is not None:
        bg = Image.open(background_image).convert("RGBA").resize(fixed.size)
        fixed = Image.alpha_composite(bg, fixed)
    
    # Add text to image
    if text:
        draw = ImageDraw.Draw(fixed)
        font = ImageFont.load_default()
        draw.text(text_position, text, fill="white", font=font)
    
    col2.write("Processed Image :wrench:")
    col2.image(fixed)
    
    st.sidebar.markdown("\n")
    st.sidebar.download_button("Download Processed Image", convert_image(fixed), "processed.png", "image/png", key="sidebar_download")
    st.download_button("Download Processed Image", convert_image(fixed), "processed.png", "image/png", key="main_download")

col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
background_upload = st.sidebar.file_uploader("Upload Background Image (Optional)", type=["png", "jpg", "jpeg"])

# Image processing controls
rotate_angle = st.sidebar.slider("Rotate Image (°)", -180, 180, 0)
crop_left = st.sidebar.number_input("Crop Left", min_value=0, value=0)
crop_top = st.sidebar.number_input("Crop Top", min_value=0, value=0)
crop_right = st.sidebar.number_input("Crop Right", min_value=0, value=0)
crop_bottom = st.sidebar.number_input("Crop Bottom", min_value=0, value=0)
crop_values = (crop_left, crop_top, crop_right, crop_bottom)
resize_width = st.sidebar.number_input("Resize Width", min_value=0, value=0)
resize_height = st.sidebar.number_input("Resize Height", min_value=0, value=0)
brightness = st.sidebar.slider("Adjust Brightness", 0.5, 2.0, 1.0)
contrast = st.sidebar.slider("Adjust Contrast", 0.5, 2.0, 1.0)
sharpness = st.sidebar.slider("Adjust Sharpness", 0.5, 2.0, 1.0)
blur_radius = st.sidebar.slider("Apply Blur", 0.0, 10.0, 0.0)
text = st.sidebar.text_input("Enter Text (Optional)")
text_x = st.sidebar.number_input("Text X Position", min_value=0, value=10)
text_y = st.sidebar.number_input("Text Y Position", min_value=0, value=10)
text_position = (text_x, text_y)

if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error("The uploaded file is too large. Please upload an image smaller than 5MB.")
    else:
        fix_image(my_upload, rotate_angle, crop_values, resize_width, resize_height, brightness, contrast, sharpness, blur_radius, text, text_position, background_upload)
else:
    fix_image("./zebra.jpg", rotate_angle, crop_values, resize_width, resize_height, brightness, contrast, sharpness, blur_radius, text, text_position, background_upload)
