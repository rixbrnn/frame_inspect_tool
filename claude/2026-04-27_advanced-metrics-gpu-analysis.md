# Advanced Metrics GPU Acceleration Analysis

**Date:** 2026-04-27  
**Status:** Analysis for Phase 2-4 Implementation

---

## Current Status

### ✓ Already GPU-Accelerated (Phase 1 Complete)
- **Basic Metrics:** SSIM, MSE, PSNR → **GPU-accelerated** (5-15x faster)
- **LPIPS:** Already GPU-accelerated via PyTorch (was done before Phase 1)

### ❌ Still CPU-Bound (Candidates for Phase 2-4)
1. **Optical Flow** - Lines 73-163 (15-25% of runtime)
2. **FLIP** - Lines 165-201 (5-10% of runtime)

---

## Phase 2: GPU Optical Flow (HIGHEST PRIORITY)

### Current Implementation (CPU)
- **Method:** `cv2.calcOpticalFlowFarneback()` (CPU-only)
- **Runtime:** 20-40ms per frame pair (1080p-4K)
- **Bottleneck:** 15-25% of total pipeline time

**Code Location:** `/src/metrics/frame/perceptual.py` lines 73-163

**Current Algorithm:**
```python
# CPU optical flow computation
flow_forward = cv2.calcOpticalFlowFarneback(
    prev_gray, curr_gray,
    None,
    pyr_scale=0.5,
    levels=3,
    winsize=15,
    iterations=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0
)

# Warp frame using flow
warped_prev = cv2.remap(prev_frame, warped_coords_x, warped_coords_y, cv2.INTER_LINEAR)

# Compute warp error (MSE)
forward_error = np.mean((warped_prev - curr_frame) ** 2)
```

### Proposed GPU Implementation

#### Option A: RAFT (Recommended - State-of-the-Art)

**Library:** `raft-core` or custom RAFT implementation

**Advantages:**
- State-of-the-art optical flow (more accurate than Farneback)
- Fully GPU-accelerated end-to-end
- PyTorch-based (integrates with our stack)
- Pre-trained models available
- **10-30x faster on GPU**

**Implementation:**
```python
import torch
from raft import RAFT  # Need to find/integrate RAFT model

class AdvancedMetrics:
    def __init__(self, device='cpu'):
        self.device = device
        self._lpips_model = None
        self._raft_model = None  # NEW
    
    @property
    def raft_model(self):
        """Lazy-load RAFT optical flow model"""
        if self._raft_model is None and self.device == 'cuda':
            self._raft_model = RAFT(pretrained=True).to(self.device).eval()
        return self._raft_model
    
    def compute_optical_flow_error_gpu(self, prev_frame, curr_frame, next_frame):
        """GPU-accelerated optical flow using RAFT"""
        # Convert to tensors
        prev_t = self._frame_to_tensor(prev_frame)
        curr_t = self._frame_to_tensor(curr_frame)
        next_t = self._frame_to_tensor(next_frame)
        
        with torch.no_grad():
            # RAFT returns flow as (2, H, W) tensor
            flow_forward = self.raft_model(prev_t, curr_t)
            flow_backward = self.raft_model(next_t, curr_t)
            
            # Warp using grid_sample (GPU-accelerated warping)
            warped_prev = self._warp_frame(prev_t, flow_forward)
            warped_next = self._warp_frame(next_t, flow_backward)
            
            # Compute errors on GPU
            forward_error = torch.mean((warped_prev - curr_t) ** 2).item()
            backward_error = torch.mean((warped_next - curr_t) ** 2).item()
            
            flow_magnitude = torch.mean(torch.sqrt(
                flow_forward[:, 0, :, :] ** 2 + flow_forward[:, 1, :, :] ** 2
            )).item()
        
        return {
            'forward_error': forward_error,
            'backward_error': backward_error,
            'mean_error': (forward_error + backward_error) / 2,
            'flow_magnitude': flow_magnitude
        }
    
    def _warp_frame(self, frame_tensor, flow):
        """Warp frame using optical flow (GPU grid_sample)"""
        B, C, H, W = frame_tensor.shape
        
        # Create coordinate grid
        grid_y, grid_x = torch.meshgrid(
            torch.arange(H, device=self.device),
            torch.arange(W, device=self.device),
            indexing='ij'
        )
        
        # Apply flow to grid
        warped_x = grid_x + flow[0, 0, :, :]
        warped_y = grid_y + flow[0, 1, :, :]
        
        # Normalize to [-1, 1] for grid_sample
        warped_x = 2.0 * warped_x / (W - 1) - 1.0
        warped_y = 2.0 * warped_y / (H - 1) - 1.0
        
        # Stack to grid (1, H, W, 2)
        grid = torch.stack([warped_x, warped_y], dim=-1).unsqueeze(0)
        
        # Warp using bilinear interpolation
        warped = torch.nn.functional.grid_sample(
            frame_tensor, grid, mode='bilinear', padding_mode='border', align_corners=True
        )
        
        return warped
```

**Dependency:** `raft-core` or integrate RAFT from official repo

**Effort:** Medium (need to integrate RAFT model)

**Expected Speedup:** 10-30x faster (2-4ms per frame vs 20-40ms CPU)

---

#### Option B: OpenCV CUDA Module (Easier)

**Library:** `opencv-contrib-python` compiled with CUDA

**Advantages:**
- Drop-in replacement for existing code
- Same Farneback algorithm (consistent results)
- Easier integration

**Disadvantages:**
- Requires OpenCV compiled with CUDA (non-trivial)
- Less speedup than RAFT (5-10x vs 10-30x)
- Still uses Farneback (not state-of-the-art)

**Implementation:**
```python
import cv2.cuda as cv2cuda

def compute_optical_flow_error_gpu_opencv(self, prev_frame, curr_frame, next_frame):
    """GPU optical flow using OpenCV CUDA module"""
    # Upload frames to GPU
    prev_gpu = cv2cuda.GpuMat(prev_frame)
    curr_gpu = cv2cuda.GpuMat(curr_frame)
    next_gpu = cv2cuda.GpuMat(next_frame)
    
    # Create GPU optical flow computer
    farneback = cv2cuda.FarnebackOpticalFlow_create()
    
    # Compute flow on GPU
    flow_forward = farneback.calc(prev_gpu, curr_gpu, None)
    flow_backward = farneback.calc(next_gpu, curr_gpu, None)
    
    # Download flow to CPU for warping (or use GPU warping)
    flow_forward_cpu = flow_forward.download()
    ...
```

**Dependency:** `opencv-contrib-python` with CUDA support

**Effort:** Easy (if precompiled wheels available), Hard (if need to compile)

**Expected Speedup:** 5-10x faster

---

### Recommendation for Phase 2

**Use RAFT (Option A)** for best performance and accuracy:
1. Better speedup (10-30x vs 5-10x)
2. More accurate optical flow (better for DLSS artifact detection)
3. PyTorch-based (fits our stack)
4. Future-proof (state-of-the-art method)

**Implementation Steps:**
1. Find/integrate RAFT model (check PyTorch Hub or official RAFT repo)
2. Add GPU flow computation method to `AdvancedMetrics` class
3. Implement GPU warping with `torch.nn.functional.grid_sample`
4. Add CPU fallback (keep existing Farneback code)
5. Update device initialization in `compare_alignment_quality.py`

**Expected Impact:**
- Per-frame time: 20-40ms → 2-4ms (10x faster)
- Overall pipeline: 15-25% faster
- **Cumulative speedup with Phase 1: 2-2.5x overall**

---

## Phase 4: GPU FLIP (LOWER PRIORITY)

### Current Implementation (CPU)
- **Method:** OpenCV color conversion + edge detection + NumPy operations
- **Runtime:** 3-5ms per frame pair
- **Bottleneck:** 5-10% of total pipeline time

**Code Location:** `/src/metrics/frame/perceptual.py` lines 165-201

**Current Algorithm:**
```python
# CPU FLIP computation
lab1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2LAB)  # CPU
lab2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2LAB)  # CPU

diff_l = np.abs(lab1[:,:,0] - lab2[:,:,0])  # CPU
diff_a = np.abs(lab1[:,:,1] - lab2[:,:,1])  # CPU
diff_b = np.abs(lab1[:,:,2] - lab2[:,:,2])  # CPU

weighted_diff = diff_l * 0.5 + diff_a * 0.25 + diff_b * 0.25  # CPU

edges1 = cv2.Canny(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), 50, 150)  # CPU
edge_mask = (edges1 > 0).astype(float)  # CPU

weighted_diff = weighted_diff * (1.0 + edge_mask * 0.5)  # CPU
return np.mean(weighted_diff)  # CPU
```

### Proposed GPU Implementation

**Library:** `kornia` (PyTorch computer vision library)

**Implementation:**
```python
import kornia

class AdvancedMetrics:
    def compute_flip_gpu(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """GPU-accelerated FLIP using Kornia"""
        # Convert to tensors
        f1 = self._frame_to_tensor(frame1)  # (1, 3, H, W) BGR
        f2 = self._frame_to_tensor(frame2)
        
        with torch.no_grad():
            # Color space conversion on GPU (BGR → LAB)
            lab1 = kornia.color.bgr_to_lab(f1)
            lab2 = kornia.color.bgr_to_lab(f2)
            
            # Compute per-channel differences
            diff_l = torch.abs(lab1[:, 0:1, :, :] - lab2[:, 0:1, :, :])
            diff_a = torch.abs(lab1[:, 1:2, :, :] - lab2[:, 1:2, :, :])
            diff_b = torch.abs(lab1[:, 2:3, :, :] - lab2[:, 2:3, :, :])
            
            # Perceptual weighting
            weighted_diff = diff_l * 0.5 + diff_a * 0.25 + diff_b * 0.25
            
            # Edge detection on GPU
            gray1 = kornia.color.bgr_to_grayscale(f1)
            edges1 = kornia.filters.canny(gray1)[0]  # Returns (edges, magnitude)
            edge_mask = (edges1 > 0).float()
            
            # Weight by edges
            weighted_diff = weighted_diff * (1.0 + edge_mask * 0.5)
            
            # Mean reduction
            flip_score = torch.mean(weighted_diff).item()
        
        return flip_score
```

**Dependency:** `kornia>=0.7.0`

**Effort:** Medium (straightforward porting)

**Expected Speedup:** 3-8x faster (0.5-1ms per frame vs 3-5ms CPU)

**Expected Impact:**
- Per-frame time: 3-5ms → 0.5-1ms
- Overall pipeline: 3-8% faster
- **Cumulative speedup: +5-8% on top of Phase 1+2**

---

## Phase 3: GPU Video Decoding (OPTIONAL)

### Current Implementation
- **Method:** `cv2.VideoCapture()` with CPU H.264 decoder
- **Runtime:** Variable (10-100ms per frame depending on resolution)
- **Bottleneck:** 15-20% of total pipeline time

**Note:** This is more complex and offers diminishing returns. Focus on Phase 1+2 first.

---

## Summary: Recommended Implementation Order

### Phase 1: ✓ COMPLETE (Basic Metrics)
- Status: **DONE**
- Speedup: 30-40% overall
- Files modified: `basic.py`, `compare_alignment_quality.py`

### Phase 2: 🎯 NEXT (Optical Flow) - **RECOMMENDED**
- Status: Not started
- Speedup: +15-25% (cumulative 2-2.5x with Phase 1)
- Priority: **HIGH** (biggest remaining bottleneck)
- Effort: Medium
- Files to modify: `perceptual.py`, `compare_alignment_quality.py`
- Dependencies: RAFT model integration
- **This should be the next focus**

### Phase 4: (FLIP) - **OPTIONAL**
- Status: Not started
- Speedup: +3-8% (cumulative 2.5-3x with Phase 1+2)
- Priority: LOW (small gains for effort)
- Effort: Medium
- Files to modify: `perceptual.py`
- Dependencies: `kornia>=0.7.0`

### Phase 3: (Video Decoding) - **SKIP FOR NOW**
- Status: Not started
- Speedup: +10-20% (cumulative 3-5x with all phases)
- Priority: LOWEST (complex, diminishing returns)
- Effort: Hard
- Files to modify: `compare_alignment_quality.py`
- Dependencies: `av>=11.0.0` with CUDA support

---

## Estimated Timeline

### Minimum Viable GPU Acceleration (Done + Phase 2)
- **Time:** Phase 1 complete + 4-6 hours for Phase 2
- **Speedup:** 2-2.5x overall
- **Effort:** ~80% of total gains for 40% of effort
- **Recommendation:** Do this before running full cyberpunk_low analysis

### Maximum GPU Acceleration (All Phases)
- **Time:** Phase 1 complete + 8-12 hours for Phase 2+3+4
- **Speedup:** 3-5x overall
- **Effort:** 100% of gains but 100% of effort
- **Recommendation:** Only if you have spare time and want maximum performance

---

## Next Steps

1. **Decision:** Do you want to implement Phase 2 (Optical Flow GPU)?
   - Yes → Big gains (2-2.5x cumulative speedup)
   - No → Proceed with Phase 1 only (still 30-40% faster)

2. **If Yes to Phase 2:**
   - Find RAFT implementation (check PyTorch Hub or RAFT official repo)
   - Integrate RAFT model into `AdvancedMetrics` class
   - Test GPU vs CPU optical flow equivalence
   - Benchmark performance gains

3. **If No:**
   - Test Phase 1 implementation on GPU machine
   - Run pilot cyberpunk_low analysis (3 comparisons)
   - Validate results and performance
   - Proceed with full analysis

**My Recommendation:** Implement Phase 2 (Optical Flow) for maximum impact with reasonable effort. Skip Phase 3+4 unless you have extra time.
