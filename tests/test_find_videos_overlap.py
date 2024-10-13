import numpy as np
import imagehash
from PIL import Image
from src import app  # Import the function from your app (replace 'app' with your file name)

# Helper function to create a mock frame
def create_mock_frame(color):
    """Create a mock frame of a solid color."""
    return np.full((100, 100, 3), color, dtype=np.uint8)

def test_overlap_found():
    """Test if the overlap is found between two sets of frames."""

    # Create mock frames (5 frames for video1, 3 frames for video2)
    frames_video1 = [
        create_mock_frame((255, 0, 0)),  # Red frame
        create_mock_frame((0, 255, 0)),  # Green frame
        create_mock_frame((0, 0, 255)),  # Blue frame (overlapping frame)
        create_mock_frame((255, 255, 0)),  # Yellow frame (overlapping frame)
        create_mock_frame((0, 255, 255)),  # Cyan frame (overlapping frame)
    ]

    frames_video2 = [
        create_mock_frame((0, 0, 255)),  # Blue frame (matches frame 2 in video1)
        create_mock_frame((255, 255, 0)),  # Yellow frame (matches frame 3 in video1)
        create_mock_frame((0, 255, 255)),  # Cyan frame (matches frame 4 in video1)
    ]

    # Call the find_video_overlap function
    start1, start2, match_length = app.find_video_overlap(frames_video1, frames_video2)

    # Assert that the overlap starts at frame 2 in video1 and frame 0 in video2
    assert start1 == 2
    assert start2 == 0
    assert match_length == 3  # Overlap should be 3 frames long

def test_no_overlap():
    """Test if no overlap is found between two sets of frames."""
    
    # Create non-overlapping frames
    frames_video1 = [
        create_mock_frame((255, 0, 0)),  # Red frame
        create_mock_frame((0, 255, 0)),  # Green frame
        create_mock_frame((0, 0, 255)),  # Blue frame
    ]
    
    frames_video2 = [
        create_mock_frame((255, 255, 255)),  # White frame
        create_mock_frame((0, 0, 0)),  # Black frame
        create_mock_frame((128, 128, 128)),  # Gray frame
    ]
    
    # Call the find_video_overlap function
    start1, start2, match_length = app.find_video_overlap(frames_video1, frames_video2)
    
    # Assert that no overlap was found
    assert start1 is None
    assert start2 is None
    assert match_length == 0
