import pytest

from src import app;

def test_identical_images():
    # Test with identical images
    score = app.get_images_similarity('tests/data/left.jpg', 'tests/data/left.jpg')
    assert score == 100.0  # SSIM should be 1 for identical images

def test_different_images():
    # Test with different images
    score = app.get_images_similarity('tests/data/left.jpg', 'tests/data/right.jpg')
    assert score < 100.0  # SSIM should be less than 1 for different images

def test_nonexistent_file():
    with pytest.raises(Exception):
        # This should raise an error since the file doesn't exist
        get_images_similarity('tests/data/non-existing-image.jpg', 'tests/data/non-existing-image.jpg')