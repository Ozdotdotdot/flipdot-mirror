# Research: Real-Time Digital Mirror for a 35×21 Binary Flip-Dot Display

Target: 735 strictly-binary pixels, real time, from a live camera, must keep a person (face/arms/hands/gestures) recognizable. Findings below are grouped by source category; every entry is something actually found via search/fetch, with links. Where I couldn't verify a detail (resolution, sensor, license) from the source, I say so instead of guessing.

---

## 1. Closest direct analog: 64×64 LED-matrix "Vision Matrix" (Cornell ECE 5725)

**Project:** Vision Matrix — https://courses.ece.cornell.edu/ece5990/ECE5725_Spring2024_Projects/03%20Tuesday%20May%2014/12%20Vision%20Matrix/W_G12_pw463_kk858_kgp33/index.html

- **Camera/sensor:** Raspberry Pi Camera (PiCamera), ordinary RGB, no depth/IR.
- **Output:** Two 64×32 RGB LED matrix panels (4mm pitch) wired in parallel → 64×64 combined resolution, driven via `rpi-rgb-led-matrix`. Not strictly binary (RGB), but they explicitly threshold down to a binary mask for the "mirror" mode.
- **Pipeline:** RPi 4B captures 320×240 frames (downscaled for speed) → **MediaPipe Selfie Segmentation** produces a soft grayscale mask → mask is **thresholded at 0.5 confidence to binary** → binary silhouette is drawn to the LED matrix. A second "Stick Mode" instead runs MediaPipe **Pose** (33 landmarks/connections) and draws a skeletal stick figure. A "Disco" mode reuses the same segmentation mask but cycles colors, and "Art Mode" tracks the index fingertip via **Hand** landmarks for drawing.
- **Does well:** Very close to our exact problem — RGB webcam → MediaPipe → binary mask → low-res matrix, with a frame-rate trick of drawing every 3rd frame to stay real-time on a Pi.
- **Limitations (their own writeup):** Selfie segmentation "performs well for solo individuals... but struggles with multiple people or close-up shots"; pose tracking adds noticeable latency; they were stuck on an older 32-bit MediaPipe build for Pi compatibility; LED flicker required tuning `led_gpio_slowdown`.
- **What to adapt:** This is essentially a smaller-resolution proof that "MediaPipe Selfie Segmentation → 0.5 threshold → binary matrix" works in real time on Pi-class hardware. Their "Stick Mode" (pose skeleton) is a good fallback/hybrid for when segmentation collapses thin limbs — see recommended pipeline B below, which proposes overlaying pose-derived limb strokes onto the segmentation mask specifically to stop arms/hands from disappearing.

---

## 2. Depth vs. RGB segmentation head-to-head write-up (directly on-topic)

**Project:** Silhouette-Segmentation-Approaches (Antimodular Research) — https://github.com/antimodular/Silhouette-Segmentation-Approaches

This is a research doc built by an installation-art studio specifically to decide which silhouette-extraction method to use for future interactive installations — i.e., someone already did the sensor/algorithm survey we're asking for.

- **Camera/sensor comparison:**
  - Intel RealSense D435i (~$199, ~10m range) — "best cost-to-performance," depth + ROI thresholding, no ML overhead, works across lighting, but **"tends to merge the background with foreground"** when a subject gets close to a wall/surface, and needs manual background masking.
  - Azure Kinect DK (~$400) — good in low light, has a Body Tracking SDK giving real skeletons, ~7m range.
  - ZED stereo camera (~$450) — best outdoor/daylight performance (depth from stereo, not IR, so sunlight doesn't blind it).
  - Kinect v2 (~$280) — noted as discontinued/unsupported.
  - ML/RGB-based: BodyPix2, OAK-D + DeepLabV3+ (on-device), Azure Kinect Body Tracking SDK, Nvidia Broadcast Engine, Detectron — multi-person capable, ID persistence, ignore non-human background clutter, but shorter effective range, angle-sensitive, heavier compute.
- **Their recommendation:** RealSense D435i + depth thresholding as the best cost/range/ease-of-dev/lighting-robustness tradeoff; Azure Kinect when you specifically need skeletons/multi-person ID.
- **What to adapt:** This directly informs our "sensor" question (item 5 below) — depth is the standard choice for installation-grade robustness to lighting, but has a known failure mode (subject silhouette merging into a wall behind them) that we'd need a fixed minimum stand-off distance or an adaptive far-plane threshold to avoid.

---

## 3. Flip-dot–specific prior art

### 3a. Flipdisc.io — open build/software guide for flip-disc panels
https://flipdisc.io/
- **Hardware:** 9× Alfazeta flip-disc panels (84×42 discs) in a 3×3 grid, RS485-driven, an **Nvidia Jetson Orin Nano** with an **IMX708 (Raspberry Pi Camera Module 3)** camera and a Waveshare audio board.
- **Software:** Node.js display driver over RS485; scenes composed in PIXI.js (2D) / Three.js (3D) rendered to a canvas, then luminance-mapped + **dithered down to binary** flip-disc frames; **MediaPipe** used for gesture/vision-driven interactivity. Companion Expo mobile app for control/drawing.
- **Relevance:** This is the most direct flip-dot analog found — same MediaPipe-based camera pipeline, same target of binary output, same "canvas → dithered binary" final step. Camera-to-silhouette specifics (thresholding method, limb handling) weren't documented on the page itself, but the hardware/software stack (Jetson + IMX708 + MediaPipe + Node.js RS485 driver) is a plausible reference architecture if the flip-dot mirror is to run on Jetson/RPi rather than in-browser.

### 3b. BREAKFAST (kinetic flip-disc studio) — depth-sensor mirror mode
https://theartistbreakfast.com/flip-discs , via https://www.hackster.io/news/breakfast-builds-a-kinetic-display-using-thousands-of-flipping-discs-88755ad509d4
- Modular 17"×17" panels of 784 half-inch discs, ~30fps disc flip rate.
- Several installations "see the space in front of them via a depth array sensor," and in at least one piece, "when someone is close and interacts with the piece, a depth sensor sees them and replaces the visualization with a reflection of themselves." Confirms depth sensing (not plain RGB) is the sensor of choice for this class of large flip-disc art install, but no public code/pipeline was found — this is a commercial studio, not open-source.

### 3c. Interactive Flip-Dot Display, Think Create
https://thinkcreate.us/portfolio-interactive-flip-dot-display.html
- 784-dot modules; one mode is "real-time body tracking" via an unspecified **3D depth camera**. No pipeline detail or code published; confirms the pattern (depth camera → body tracking → flip-dot) recurs but isn't independently useful beyond that confirmation.

### 3d. Other flip-dot GitHub repos found (driver-level, not vision)
- https://github.com/jakkra/FlipDot — web UI to draw/scroll text/GIFs to a flip-dot matrix (no camera).
- https://github.com/cazacov/FlipDot, https://github.com/RobsyRocket/Flip-The-Dot, https://github.com/N0TB0T/dottie — hardware/driver-level flip-dot controller projects (ESP32/microcontroller), useful for the *output* driver side of our project, not the vision pipeline.
- https://github.com/delhatch/Flipdot_video — camera (D8M module) streamed to a 58×24 flip-dot display, but processing is done **entirely in Verilog RTL on an FPGA** (Cyclone IV) — interesting architecturally (proves a camera→flip-dot pipeline can run with zero software stack) but not portable to a Python/browser prototype.

---

## 4. Non-flip-dot low-res/binary "mirror" art and installations

- **Daniel Rozin's mechanical mirrors** (bitforms gallery: https://www.bitforms.art/exhibition/contours/, https://www.bitforms.art/artwork/fabric-mirror-2 ; overview: https://synkroniciti.com/technology-and-the-shadow-interactive-mirrors-by-daniel-rozin/) — decades of work turning a hidden camera feed into a coarse physical-pixel reflection (wooden tiles, trash, pegs, fabric) that shift brightness/angle in real time. **"One Candle Mirror"** renders the viewer purely as a **silhouette formed by absence of light** — directly relevant conceptually: at extreme "resolution" (a few hundred physical pixels), Rozin's approach is always luminance/shading-driven rather than literal grayscale copy, i.e. treat the output as a *shaded relief of the silhouette*, not a downsampled photo. No source code (custom mechanical + software, not published), but the design principle — coarse physical pixels reproduce *shape and gesture*, not photographic detail — is exactly our constraint.
- **Jason Bruges Studio — Shadow Wall** (https://designawards.core77.com/Interaction/97058/Shadow-Wall, https://wembleypark.com/Shadow-Wall-by-Jason-Bruges/) — underpass installation, "bespoke infrared light sensors" (not a camera+CV pipeline — each node senses ambient IR level itself) feeding a **Unity**-based control system; deliberately elongates the persistence/decay of each lit trace to "stretch" motion and make running/walking visible as a streak. One build used a **180×120 LED array** at Sydney's Vivid Festival, ported "to Python to use full OpenCV," per a related article (exact pipeline not documented beyond that). Relevant idea: **deliberately slow decay / motion trails** as a cheap way to keep fast-moving thin limbs (a waving arm) visible for more frames than their true dwell time, effectively free temporal anti-aliasing for gesture visibility on a sparse binary grid.
- **PJRC Shadow Wall** (https://www.pjrc.com/shadow-wall-art-installation/) — confirms a **180×120 LED (~21,600 px) display** project also ported its pixel-processing to Python + OpenCV for speed of serial transfer; low detail beyond that on the actual CV algorithm from the fetched page.

---

## 5. Real-time video→ASCII / video→braille / terminal camera projects

These solve a structurally similar problem (continuous tone → discrete low-res symbolic grid, real time), though none target strictly 1-bit output at 35×21.

| Project | Link | Notes |
|---|---|---|
| ASCII-Vision (AlexEidt) | https://github.com/AlexEidt/ASCII-Vision | Python, MIT license. PIL/NumPy/NumExpr; maps grayscale luminance to a density-sorted ASCII ramp; `FACTOR` parameter divides frame dims for speed; includes Sobel/edge-outline filter modes as alternates to plain luminance mapping — the edge-filter mode is closer to what we'd want (edges/silhouette vs. raw luminance). |
| ASCIIcamera (jrajan14) | https://github.com/jrajan14/ASCIIcamera | Browser-only (getUserMedia + Canvas), no backend; multiple resolution presets including "Ultra Low," and a **Binary** character mode — i.e. already has a 1-bit-style output mode worth inspecting directly for its downsampling code. |
| ascii-cam (cesarferreira) | https://github.com/cesarferreira/ascii-cam | Rust, terminal renderer, real-time; less relevant architecturally (terminal-specific) but demonstrates real-time full native-code capture→convert→render loop. |
| BrailleVideo (PyroCalzone) | https://github.com/PyroCalzone/BrailleVideo | Converts video frames to Unicode braille cells (each cell = 2×4 sub-pixel binary block) — structurally the *exact* problem of "map a photographic region to a small fixed grid of binary dots," just for offline video rather than live camera, and per-cell/per-dot threshold logic isn't documented in the README (would need to read source directly). Braille's 2×4 dot cell is a useful mental model for "sub-pixel binary blocks" if the flip-dot layout is ever grouped into cells for local dithering. |
| rfong "Low-res webcam processing experiments" (blog) | https://rfong.github.io/rflog/2021/10/14/low-res-webcams/ | Directly on-topic personal write-up comparing: an ASCII webcam (~240×144 chars, 10fps), a **binary Floyd-Steinberg dithering webcam ("dithercam")** in vanilla JS achieving ~8fps at 800×600 pre-dither resolution, and older Canny-edge / row-delay experiments. Confirms client-side Floyd-Steinberg on live video is practical in-browser at interactive frame rates — a candidate baseline for our browser prototype's dithering stage. |

---

## 6. Segmentation / background-subtraction / pose technique notes

- **MOG2 / KNN background subtraction + morphology (OpenCV):** standard combo — MOG2 handles lighting adaptation and shadow labeling; morphological **closing** (dilate→erode) is the standard fix for small gaps/holes that fragment thin limbs, then **opening** (erode→dilate) removes stray noise blobs. (https://docs.opencv.org/4.13.0/d1/dc5/tutorial_background_subtraction.html, https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html) Direct applicability: closing kernel size should be tuned relative to expected on-screen limb width in pixels *before* downsampling to 35×21, not after — closing after downsampling will just fatten/erase whatever the downsample already destroyed.
- **Hysteresis thresholding for motion/foreground detection** — classic two-threshold (low/high) approach from edge detection literature, reused in background-subtraction papers to avoid single-threshold flicker: a pixel already classified foreground stays foreground under a looser threshold, while new foreground needs the stricter threshold to "turn on." Directly reusable as our **per-pixel/per-dot flip hysteresis** to reduce flip-dot chatter (see §8).
- **Shadow-aware silhouette extraction** (multiple academic sources found, e.g. Horprasert et al.-style HSV/statistical shadow removal) — relevant only if the flip-dot mirror uses fixed ambient lighting and a plain RGB camera; shadows on the floor/wall behind the subject can otherwise get segmented in as part of the "person" blob.
- **MediaPipe Selfie Segmentation:** general model input 256×256, landscape model 144×256 (https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/selfie_segmentation.md); docs suggest a **joint bilateral filter** against the original image to clean up mask boundaries. A real, documented failure mode: GitHub issue https://github.com/google/mediapipe/issues/3919 reports the **Python** implementation's mask boundary is visibly worse/jaggier than the **JS/web** demo under identical conditions, with only marginal improvement from moving the threshold 0.1→0.5 — worth validating early if prototyping in Python (may push toward doing segmentation in the browser via `@mediapipe/selfie_segmentation` JS instead, which is also what several browser demos above already use).
- **BodyPix** (TF.js): https://blog.tensorflow.org/2019/11/updated-bodypix-2.html, https://github.com/google-coral/project-bodypix, https://github.com/allo-/virtual_webcam_background — older than MediaPipe's segmenter but has an explicit **internalResolution** speed/quality knob and a **body-part** segmentation mode (not just person/background), which could let us treat "arm," "hand," "head" regions differently (e.g. force-preserve minimum arm width) rather than a single undifferentiated mask.
- **Silhouette Segmentation Approaches repo (§2)** already covers the depth-based alternative in detail.

---

## 7. Psychophysics: how few pixels does a person actually need?

Useful ground truth for how aggressively we can downsample before recognizability breaks, though none of these studies target our exact 35×21 binary case:

- Classic face-recognition-from-pixels literature (via search) puts usable face identification around **16×16 px**, and ~**5 px per face** at 2.5 cycles/face for bare detectability — but that's *grayscale*, not 1-bit.
- General object/scene recognition: accuracy plateaus above roughly **24×24–32×32 px**; below 24×24 several object classes drop under 50% recognition.
- "Peepers & Pixels" (arXiv 2503.20108, https://arxiv.org/abs/2503.20108 / PDF https://arxiv.org/pdf/2503.20108) — human *face-matching* accuracy collapses to near chance (50.7%) at 10px inter-pupillary distance and below chance (35.9%) at 5px IPD, even though confidence stays high — a caution that **face identity** will not survive 735-pixel binary rendering; the achievable goal is recognizing *a person's presence, pose, and gesture*, not who they are. This matches the project's own framing (arms/hands/gestures, not facial identity) and justifies weighting the pipeline toward pose/silhouette fidelity over any facial detail.

(These numbers are for continuous-tone imagery; no equivalent study for 1-bit dithered silhouettes was found — treat as directional context, not a hard spec.)

---

## 8. Temporal strategies specifically for flicker/stability at low resolution

- **Per-pixel/per-dot hysteresis:** borrow the two-threshold idea from §6 — each of the 735 dots keeps its last state unless the new confidence crosses a *larger* margin than what would be needed to keep it in its current state. This directly reduces the mechanical/visual chatter of flip-dots (which have audible, physical latency, unlike an LED) flipping back and forth on segmentation-mask noise.
- **Temporal dithering / frame-sequential error diffusion:** patent/technical literature on video halftoning (search results, no single canonical open project found) describes diffusing quantization error across *both* space and time, and choosing a long enough repeat period (e.g. spreading over ~16 frames at 60Hz) to push flicker below the ~4–30Hz range the eye is most sensitive to. For flip-dots specifically, physical flip cost (audible clack, finite lifetime per dot) argues for *biasing dithering to minimize dot-state changes frame-to-frame*, not just minimizing visual error — i.e. a modified error-diffusion pass that treats "changing an already-correct dot" as a cost, not just "wrong dot."
- **Motion trail / decay** (Jason Bruges Shadow Wall, §4): lingering illumination after a fast-moving limb passes is a cheap way to make a briefly-sampled arm/hand gesture visible for longer than one exposure — could be implemented as a decaying "recently-on" bias added into the hysteresis threshold above.
- **Bayer/ordered dithering vs. Floyd–Steinberg error diffusion:** ordered dithering keeps a fixed spatial pattern per intensity level (stable frame-to-frame, since the same input intensity always dithers the same way) at the cost of visible fixed patterning; Floyd–Steinberg gives better local accuracy per frame but the diffusion pattern is unstable frame-to-frame under any change in mask boundary, which reads as flicker/noise on video (general dithering literature + Wikipedia Floyd–Steinberg page: https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering). For a *silhouette mask* (already binary-ish, unlike photographic grayscale) this matters less than for the ASCII/braille luminance-mapping case — recommend skipping error-diffusion dithering entirely once you already have a segmentation mask, and instead spatially resample the mask with **coverage-thresholding** (does >X% of this cell's downsampled area fall inside the mask?) which is inherently stable frame to frame.

---

## 9. Recommended pipelines to prototype

### A. Lightweight RGB + background subtraction (no ML)
1. Fixed camera, ideally a plain, evenly-lit, non-cluttered wall behind the subject (this pipeline is the most lighting/background-sensitive of the three).
2. OpenCV `createBackgroundSubtractorMOG2` (or KNN) with shadow detection enabled; capture a clean empty-room reference for the model to converge against at startup.
3. Morphological **close** then **open** on the foreground mask, kernel sized relative to expected arm width in source-resolution pixels (tune empirically — likely a kernel that closes ~1–2cm gaps at the subject's expected standing distance).
4. Find largest contour (or largest N contours) to reject small noise blobs; optionally dilate contour outward by ~1 flip-dot's worth of source pixels to compensate for the fact that downsampling will erode a thin mask, not just resample it.
5. Downsample to 35×21 via **area-coverage thresholding**, not naive nearest/bilinear resize: for each of the 735 cells, compute the fraction of foreground pixels in its source-image footprint, dot = ON if fraction > threshold (start ~35–40%, biased low so limbs survive).
6. Apply per-dot **hysteresis** (§8) frame-to-frame before driving hardware.
7. Cheapest to build, runs on almost anything, but will need a controlled backdrop/lighting to be robust — closest in spirit to the antimodular RealSense writeup's "no-ML" branch but doing it in 2D/RGB instead of depth.

### B. ML person-segmentation pipeline (MediaPipe Selfie Segmentation)
1. Webcam → **MediaPipe Selfie Segmentation** (general model, 256×256 input) — run in the **browser via `@mediapipe/selfie_segmentation`** JS rather than Python, given the documented Python-vs-web mask-quality gap (§6, issue #3919); this also matches a browser-prototype deployment target directly.
2. Optional: joint-bilateral-filter the mask against the source frame (per MediaPipe's own docs) to sharpen boundaries before downsampling.
3. **Limb-preservation step (the key addition beyond the Cornell "Vision Matrix" baseline):** in parallel, run **MediaPipe Pose** (or Holistic) landmarks on the same frame; draw the arm/forearm/hand bone segments as a thick stroke (width ≈ 1 flip-dot cell at final resolution, projected back to source resolution) and **OR** this stroke mask into the segmentation mask before downsampling. This directly targets the "arms/hands vanish" failure mode that plain segmentation-then-downsample will hit, since a forearm is often only 1–2 flip-dot cells wide and coverage-thresholding alone will drop it under fast motion or motion blur.
4. Downsample via the same area-coverage-thresholding approach as pipeline A.
5. Per-dot hysteresis + optional short-decay "motion trail" bias (§8) for fast gesture visibility.
6. This is the pipeline the Cornell Vision Matrix project already validates in miniature (64×64, MediaPipe, 0.5-threshold binary) — our addition is the pose-skeleton limb reinforcement and the coverage-threshold downsample, neither of which their writeup mentions doing.

### C. Depth-camera pipeline (RealSense/Kinect)
1. Intel RealSense D435i (per the antimodular comparison, best cost/robustness tradeoff) or Azure Kinect if multi-person/skeleton ID is wanted.
2. Depth-threshold filter (`pyrealsense2.threshold_filter`, e.g. min 0.4m–max 2.0m) to isolate anything in a defined "standing zone," sidestepping RGB lighting/background problems entirely.
3. Guard against the documented failure mode (subject silhouette merging with a wall/background once they're close to it): either enforce a minimum stand-off distance via a physical marker/floor decal, or make the far-plane threshold adaptive based on a captured empty-room depth reference (similar in spirit to the RGB background-subtraction reference frame in pipeline A) rather than a fixed distance.
4. Morphological close/open on the resulting depth mask exactly as in pipeline A (thin-limb loss from noisy depth edges is the same problem as thin-limb loss from RGB segmentation noise).
5. Same area-coverage downsample + hysteresis + optional decay as pipelines A/B.
6. Optionally fuse with Azure Kinect Body Tracking SDK skeleton (if using Kinect) the same way pipeline B fuses MediaPipe Pose — draw thickened limb strokes into the mask to guarantee arm/hand visibility independent of depth-edge noise.
7. Most robust to lighting and background clutter of the three (this is the sensor choice recurring across the actual flip-dot/LED installations found in §3 — BREAKFAST and Think Create both use depth, not RGB), at the cost of extra hardware and, per antimodular, a background-merging edge case near walls.

**Suggested prototyping order:** B first (cheapest to iterate — laptop webcam + browser, and directly validated at small scale by the Cornell project) to nail the downsample/hysteresis/limb-preservation logic, which is display-resolution-specific and reusable regardless of final sensor choice; then C if lighting/background robustness in the real installation space proves to be the limiting factor, since that's what every actual flip-dot/kinetic-art installation found in this research (BREAKFAST, Think Create) ended up using.

---

## Sources referenced above

- https://courses.ece.cornell.edu/ece5990/ECE5725_Spring2024_Projects/03%20Tuesday%20May%2014/12%20Vision%20Matrix/W_G12_pw463_kk858_kgp33/index.html
- https://github.com/antimodular/Silhouette-Segmentation-Approaches
- https://flipdisc.io/
- https://theartistbreakfast.com/flip-discs
- https://www.hackster.io/news/breakfast-builds-a-kinetic-display-using-thousands-of-flipping-discs-88755ad509d4
- https://thinkcreate.us/portfolio-interactive-flip-dot-display.html
- https://github.com/jakkra/FlipDot
- https://github.com/cazacov/FlipDot
- https://github.com/RobsyRocket/Flip-The-Dot
- https://github.com/N0TB0T/dottie
- https://github.com/delhatch/Flipdot_video
- https://www.bitforms.art/exhibition/contours/
- https://www.bitforms.art/artwork/fabric-mirror-2
- https://synkroniciti.com/technology-and-the-shadow-interactive-mirrors-by-daniel-rozin/
- https://designawards.core77.com/Interaction/97058/Shadow-Wall
- https://wembleypark.com/Shadow-Wall-by-Jason-Bruges/
- https://www.pjrc.com/shadow-wall-art-installation/
- https://github.com/AlexEidt/ASCII-Vision
- https://github.com/jrajan14/ASCIIcamera
- https://github.com/cesarferreira/ascii-cam
- https://github.com/PyroCalzone/BrailleVideo
- https://rfong.github.io/rflog/2021/10/14/low-res-webcams/
- https://docs.opencv.org/4.13.0/d1/dc5/tutorial_background_subtraction.html
- https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html
- https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/selfie_segmentation.md
- https://github.com/google/mediapipe/issues/3919
- https://blog.tensorflow.org/2019/11/updated-bodypix-2.html
- https://github.com/google-coral/project-bodypix
- https://github.com/allo-/virtual_webcam_background
- https://arxiv.org/abs/2503.20108 / https://arxiv.org/pdf/2503.20108
- https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering
