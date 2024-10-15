import pytest
from unittest.mock import patch
from src import video_comparison


def mock_get_frame_hash(frame):
    return frame

def mock_compare_hashes(hash1, hash2):
    return hash1 == hash2

@patch('src.video_comparison.get_frame_hash', side_effect=mock_get_frame_hash)
def test_find_video_overlap(mock_get_hash, mock_compare_hash):

    
    video1_frames = ["frame1", "frame2", "frame3", "frame4", "frame5"]
    video2_frames = ["frameA", "frameB", "frame2", "frame3", "frame4", "frameC"]

    start1, end1, start2, end2 = video_comparison.find_video_overlap(video1_frames, video2_frames, min_match_length=2)

    assert start1 == 1  # Expected start index in video 1
    assert end1 == 3    # Expected end index in video 1
    assert start2 == 2  # Expected start index in video 2
    assert end2 == 4    # Expected end index in video 2

    video1_frames_no_overlap = ["frameX", "frameY", "frameZ"]
    video2_frames_no_overlap = ["frameA", "frameB", "frameC"]
    
    start1, end1, start2, end2 = video_comparison.find_video_overlap(video1_frames_no_overlap, video2_frames_no_overlap, min_match_length=2)
    
    assert start1 is None
    assert end1 is None
    assert start2 is None
    assert end2 is None

if __name__ == "__main__":
    pytest.main()
