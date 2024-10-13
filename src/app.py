from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np
import argparse


# The diff image contains the actual image differences between the two images
# and is represented as a floating point data type in the range [0,1] 
# so we must convert the array to 8-bit unsigned integers in the range
# [0,255] before we can use it with OpenCV
#diff = (diff * 255).astype("uint8")
#diff_box = cv2.merge([diff, diff, diff])

# Threshold the difference image, followed by finding contours to
# obtain the regions of the two input images that differ
#thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
#contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#contours = contours[0] if len(contours) == 2 else contours[1]

#mask = np.zeros(before.shape, dtype='uint8')
#filled_after = after.copy()

#for c in contours:
#    area = cv2.contourArea(c)
#    if area > 40:
#        x,y,w,h = cv2.boundingRect(c)
#        cv2.rectangle(before, (x, y), (x + w, y + h), (36,255,12), 2)
#        cv2.rectangle(after, (x, y), (x + w, y + h), (36,255,12), 2)
#        cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36,255,12), 2)
#        cv2.drawContours(mask, [c], 0, (255,255,255), -1)
#        cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)
#
#cv2.imshow('before', before)
#cv2.imshow('after', after)
#cv2.imshow('diff', diff)
#cv2.imshow('diff_box', diff_box)
#cv2.imshow('mask', mask)
#cv2.imshow('filled after', filled_after)
#cv2.waitKey()

import cv2
import os
from skimage.metrics import structural_similarity as ssim
import argparse

def get_images_similarity(source_image_path, modified_image_path):
    # Load images
    source_image = cv2.imread(source_image_path)
    modified_image = cv2.imread(modified_image_path)

    # Convert images to grayscale
    before_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)

    # Compute SSIM between the two images
    (score, diff) = ssim(before_gray, after_gray, full=True)
    return score * 100

def compare_with_directory(source_image_path, directory):
    # Loop through the files in the provided directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Skip the source file itself if it's in the same directory
        if file_path == source_image_path:
            continue
        
        # Check if the file is an image (can be extended for other formats)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Comparing source image with {file_path}...")
            score = get_images_similarity(source_image_path, file_path)
            print(f"Image Similarity (SSIM) with {filename}: {score:.4f}%")

def main():
    parser = argparse.ArgumentParser(description="Compare images using SSIM.")
    
    # Add arguments for source image, modified image, and directory
    parser.add_argument(
        '-s', '--source', required=True, help="Path to the source image."
    )
    parser.add_argument(
        '-m', '--modified', required=False, help="Path to the modified image."
    )
    parser.add_argument(
        '-d', '--directory', required=False, help="Path to the directory containing images to compare."
    )

    # Parse the arguments
    args = parser.parse_args()

    # If both source and modified are provided, do single image comparison
    if args.source and args.modified:
        score = get_images_similarity(args.source, args.modified)
        print(f"Image Similarity (SSIM): {score:.4f}%")

    # If source and directory are provided, do directory-based comparison
    elif args.source and args.directory:
        compare_with_directory(args.source, args.directory)

    else:
        print("Please provide either a modified image (-m) or a directory (-d) for comparison.")

if __name__ == "__main__":
    main()