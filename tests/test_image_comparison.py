import os
from src import image_comparison;
import pytest

def test_identical_images():
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    score = image_comparison.get_images_similarity(source_image, source_image)
    assert score == 100.0  # SSIM should be 1 for identical images

def test_different_images():
    source_image = os.path.join('tests', 'data', 'basic_test', 'table_source.jpg')
    target_image = os.path.join('tests', 'data', 'basic_test', 'table_modified.jpg')
    score = image_comparison.get_images_similarity(source_image, target_image)
    assert score < 100.0  # SSIM should be less than 1 for different images

def test_nonexistent_file():
    with pytest.raises(Exception):
        image_comparison.get_images_similarity('tests/data/non-existing-image.jpg', 'tests/data/non-existing-image.jpg')