import pytest
import subprocess
import os
from src import app;

def test_identical_images():
    # Test with identical images
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    score = app.get_images_similarity(source_image, source_image)
    assert score == 100.0  # SSIM should be 1 for identical images

def test_different_images():
    # Test with different images
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    target_image = os.path.join('tests', 'data', 'basic_test', 'table_modified.jpg')
    score = app.get_images_similarity(source_image, target_image)
    assert score < 100.0  # SSIM should be less than 1 for different images

def test_nonexistent_file():
    with pytest.raises(Exception):
        # This should raise an error since the file doesn't exist
        app.get_images_similarity('tests/data/non-existing-image.jpg', 'tests/data/non-existing-image.jpg')


# Test for the single image comparison
def test_single_image_comparison(tmpdir):
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    modified_image = os.path.join('tests', 'data', 'basic_test', 'table_modified.jpg')

    result = subprocess.run(
        ['python', 'src/app.py', '-s', source_image, '-m', modified_image],
        capture_output=True,
        text=True
    )

    # Check if the command was successful
    assert result.returncode == 0

    # Verify the expected output is in the result
    assert "Image Similarity (SSIM):" in result.stdout
    assert "100.0000%" not in result.stdout  # This ensures the images are not identical

def test_directory_comparison(tmpdir):
    source_image = os.path.join('tests', 'data', 'cyberpunk_4k_ultra_preset_viktor_lab', 'source.png')
    test_directory = os.path.join('tests', 'data', 'cyberpunk_4k_ultra_preset_viktor_lab')

    result = subprocess.run(
        ['python', 'src/app.py', '-s', source_image, '-d', test_directory],
        capture_output=True,
        text=True
    )

    # Check if the command was successful
    assert result.returncode == 0

    assert "Image Similarity (SSIM) with" in result.stdout

    assert "dlss_b.png" in result.stdout
    assert "dlaa.png" in result.stdout

def test_missing_arguments():
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    result = subprocess.run(
        ['python', 'src/app.py', '-s', source_image],
        capture_output=True,
        text=True
    )

    # Command should fail since both -m and -d are missing
    assert result.returncode == 0
    assert "Please provide either a modified image (-m) or a directory (-d)" in result.stdout
