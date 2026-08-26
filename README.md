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

**Hard threshold** is the default raster mode because it preserves narrow arms and gestures better at 35×21. Filled silhouette and both dithering algorithms remain available as deliberate visual treatments.

Framing is also selectable:

- **Mirror / full camera frame** preserves the installation-as-mirror composition.
- **Fit detected subject** crops around foreground motion, maintains the display's 5:3 aspect ratio, and enlarges the subject without stretching them. Subject padding controls how much environment remains visible.

Background calibration is intentionally local and model-free. It works well for a fixed installation camera but must be repeated if the camera or lighting changes substantially.

## Display interpretation

- White page/canvas: inactive display surface.
- Black circles: dots that would be actuated to the black face.
- Resolution: exactly 35×21 = 735 dots.

This version intentionally stops at the logical framebuffer. Hardware serialization, module-chain remapping, ESP32 transport, and physical transition choreography will be separate layers.
