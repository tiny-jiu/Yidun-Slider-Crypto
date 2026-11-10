# Yidun Slider Crypto

A Python look at Yidun's slider puzzle, from its custom encryption to image matching and motion encoding. The code follows the complete request flow and keeps the individual pieces easy to inspect.

## What it covers

- Custom byte encoding and two Base64 alphabets
- CRC32 generation and PKCS7-style padding
- IV generation and the custom CBC-like encryption routine
- `cb` parameter generation
- Slider image matching with OpenCV
- Motion generation and request payload encoding

## Encryption notes

The routine named `aes` is not a standard AES implementation. It uses a custom S-box, a fixed seed, and a sequence of round-key operations.

The main flow is:

1. Convert the input to bytes.
2. Append a CRC32 value.
3. Pad the data to 64-byte blocks.
4. Generate and expand the IV.
5. Transform each block with the round-key operations, XOR, addition, and S-box substitutions.
6. Encode the raw IV and encrypted bytes with the private Base64 alphabet.

## Request flow

The solver follows four stages:

1. `getconf` retrieves the puzzle configuration.
2. `get` retrieves the background, puzzle piece, and token.
3. Several OpenCV matching methods estimate the gap position.
4. The motion data is generated, encoded, and sent to `check`.

Image matching combines masked template matching, Canny edges, Sobel gradients, and correlation. Results that sit too far from the median are discarded.

## Motion data

Motion is generated in four parts: acceleration, a faster approach, a slower adjustment, and final alignment. Small vertical variations keep the points from forming a perfectly straight line.

The submitted fields contain sampled motion points, the final position, timestamps, and the number of points.

## JavaScript references

`before-analysis.js` keeps the original reference snapshot, while `after-analysis.js` provides the processed version for comparison.

## Setup

```bash
pip install requests opencv-python numpy pillow
python slider_crypto.py
```

For security research and authorized testing only.
