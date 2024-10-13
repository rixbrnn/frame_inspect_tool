import cv2
import os
import re

# Function to sort filenames based on the numeric part in the filename (e.g., "image_0.png", "image_1.png", etc.)
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# Convert images to video
def images_to_video(image_folder, output_video, fps=30, width=None, height=None):
    # Get the list of images in the directory
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    
    # Sort images based on the numeric order in filenames (e.g., image_0.png, image_1.png)
    images.sort(key=natural_sort_key)

    if len(images) == 0:
        print("No images found in the specified folder.")
        return

    # Read the first image to get the width and height, if not provided
    first_image = cv2.imread(os.path.join(image_folder, images[0]))
    if width is None or height is None:
        height, width, _ = first_image.shape  # Use first image's size

    # Define the video codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Error reading image: {img_path}")
            continue
        
        # Resize frame if the size is different from the first image
        if frame.shape[1] != width or frame.shape[0] != height:
            frame = cv2.resize(frame, (width, height))

        video.write(frame)

    video.release()
    print(f'Video saved as "{output_video}"')

def main():
    image_folder = input("Enter the path to the folder containing your images: ")
    output_video = input("Enter the name of the output video file (e.g., 'output.mp4'): ")

    # Convert images to video
    images_to_video(image_folder, output_video, fps=30)

if __name__ == "__main__":
    main()
