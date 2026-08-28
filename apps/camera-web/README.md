# F30 Camera Prototype

A local, hardware-independent prototype of the 35×21 F30 display canvas.

## Run

Camera access generally requires a secure browser context. `localhost` counts as secure, while opening the HTML directly with a `file://` URL may not.

From this folder, run:

```sh
python3 -m http.server 8765
```

Then open:

```text
http://localhost:8765
```

Allow camera access when prompted. After permission is granted, the camera menu will show the actual cameras available on that machine.

## Silhouette workflow

1. Fix the camera in place.
2. Start the camera.
3. Step completely out of view.
4. Select **Capture empty background**.
5. Step back into view.
6. Adjust foreground sensitivity and mask cleanup.
7. Compare ordered dithering, Floyd–Steinberg dithering, and hard thresholding.

**Solid silhouette** is the default raster mode. At only 35×21 pixels, a continuous human outline is usually more legible than facial shading. The dithering modes remain available as deliberate visual treatments rather than the default interpretation.

Background calibration is intentionally local and model-free. It works well for a fixed installation camera but must be repeated if the camera or lighting changes substantially.

## AI person mirror

The default mode now loads MediaPipe person segmentation and pose tracking in the browser. Its pipeline is semantic person mask → pose-based limb reinforcement → area-coverage reduction to 35×21 → per-dot hysteresis. This is designed to retain arms and gestures without converting photographic shading into unstable dithering. The first load requires internet access for the MediaPipe runtime and models; camera frames remain in the browser.

- **AI cell coverage** controls how much of a physical dot's source area must contain the person before it turns on.
- **Limb reinforcement** draws a minimum-width pose skeleton into the person mask before downsampling. Set it to zero to inspect raw segmentation.
- **Dot hysteresis** gives an active dot a slightly lower turn-off threshold, reducing chatter at mask boundaries.
- The original calibrated background-subtraction, portrait, and luminance modes remain available for direct comparison.

## Display interpretation

- White page/canvas: inactive display surface.
- Black circles: dots that would be actuated to the black face.
- Resolution: exactly 35×21 = 735 dots.

This version intentionally stops at the logical framebuffer. Hardware serialization, module-chain remapping, ESP32 transport, and physical transition choreography will be separate layers.
