import pytest
import subprocess
import os
from src import app;

def test_identical_images():
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    score = app.get_images_similarity(source_image, source_image)
    assert score == 100.0  # SSIM should be 1 for identical images

def test_different_images():
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    target_image = os.path.join('tests', 'data', 'basic_test', 'table_modified.jpg')
    score = app.get_images_similarity(source_image, target_image)
    assert score < 100.0  # SSIM should be less than 1 for different images

def test_nonexistent_file():
    with pytest.raises(Exception):
        app.get_images_similarity('tests/data/non-existing-image.jpg', 'tests/data/non-existing-image.jpg')


def test_single_image_comparison(tmpdir):
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    modified_image = os.path.join('tests', 'data', 'basic_test', 'table_modified.jpg')

    result = subprocess.run(
        ['python', 'src/app.py', '-s', source_image, '-m', modified_image],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert result.returncode == 0

    assert 'Image Similarity (SSIM):' in result.stdout
def test_directory_comparison(tmpdir):
    source_image = os.path.join('tests', 'data', 'cyberpunk_4k_ultra_preset_viktor_lab', 'source.png')
    test_directory = os.path.join('tests', 'data', 'cyberpunk_4k_ultra_preset_viktor_lab')

    result = subprocess.run(
        ['python', 'src/app.py', '-s', source_image, '-d', test_directory],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    assert "Image Comparison Report (Sorted by Similarity)" in result.stdout

    assert "dlss_b.png" in result.stdout
    assert "dlaa.png" in result.stdout

def test_missing_arguments():
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    result = subprocess.run(
        ['python', 'src/app.py', '-s', source_image],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Please provide valid arguments for either image or video comparison" in result.stdout
    