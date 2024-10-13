import cv2
import os
from skimage.metrics import structural_similarity as ssim
import argparse
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

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
    # List to hold the results for generating the report later
    results = []

    # Get the list of files in the directory (filter image files only)
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Use tqdm for a loading bar
    for filename in tqdm(files, desc="Comparing images", unit="image"):
        file_path = os.path.join(directory, filename)

        # Skip the source file itself if it's in the same directory
        if file_path == source_image_path:
            continue

        # Compare images and get the similarity score
        score = get_images_similarity(source_image_path, file_path)

        # Store the result
        results.append({
            'filename': filename,
            'score': score
        })

    # Generate final report after all images are processed
    generate_report(results)

def generate_report(results):
    # Sort the results by SSIM score in descending order (most similar first)
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

    print("\n" + Fore.CYAN + "Final Report (Sorted by Similarity)" + Style.RESET_ALL)
    print(f"{'Image Name':<40}{'SSIM Score (%)':>15}")
    print("="*55)
    
    for result in sorted_results:
        score = result['score']
        filename = result['filename']
        color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
        print(f"{filename:<40}{color}{score:.2f}{Style.RESET_ALL}")

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
        
        # Color code the similarity score based on the value
        if score >= 99:
            color = Fore.GREEN
        elif score >= 97:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        
        print(f"{Fore.CYAN}Image Similarity (SSIM): {color}{score:.2f}%{Style.RESET_ALL}")

    # If source and directory are provided, do directory-based comparison
    elif args.source and args.directory:
        compare_with_directory(args.source, args.directory)

    else:
        print(f"{Fore.RED}Please provide either a modified image (-m) or a directory (-d) for comparison.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
