from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="rixbrnn/frame_inspect_tool_data",
    repo_type="dataset",
    local_dir="./recordings",
    local_dir_use_symlinks=False
)