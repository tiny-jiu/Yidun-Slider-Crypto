"""Explore Yidun's slider encryption, image matching, and motion encoding."""

import json
import math
import random
import re
import urllib.parse
from io import BytesIO
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image
import requests


__SBOX__ = "a7be3f3933fa8c5fcf86c4b6908b569ba1e26c1a6d7cfbf60ae4b00e074a194dac4b73e7f898541159a39d08183b76eedee3ed341e6685d2357440158394b1ff03a9004cbbb5ca7dcb7f41489a16e03dcc9c71eb3c9796685b1d01b4d56193a6e1f1a2470445c191ae49c5d82765dc82c350f263387a24a502fcbf442e2dddaad0e936d9ea22b89275307b42518fbc3a626ba806d4ecd6d725f50cc8c72fefa4551ccd6fc9b2b7ab954f815c7264c6e51f4eaf99885a79892b1b60a0b3526e57ba5d178d370958847eb9fd28f9ce0bc023f4148a2adfe632126769057043d3bd8eda0df7872629f3809ef05310e83113216afe202c460fc23e789f77d1addb5e"
__SEED_KEY__ = "fd6a43ae25f74398b61c03c83be37449"
__ROUND_KEY__ = "037606da0296055c"

BASE64_ALPHABET = "i/x1XgU0z7k8N+lCpOnPrv6\\qu2Gj9HRcwTYZ4bfSJBhaWstAeoMIEQ5mDdVFLKy"
BASE64_PADDING = "3"
PRIVATE_B64_ALPHABET = "MB.CfHUzEeJpsuGkgNwhqiSaI4Fd9L6jYKZAxn1/Vml0c5rbXRP+8tD3QTO2vWyo"
PRIVATE_B64_PADDING = "7"

CB_SUFFIX = "m25b40"
CB_CODE = "vfnv46"
CB_POS = [1, 10, 12, 13, 26, 31]
SAMPLE_NUM = 50

CRC32_TABLE = [
    0x0, 0x77073096, 0xee0e612c, 0x990951ba, 0x76dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
    0xedb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x9b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
    0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
    0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172, 0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
    0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
    0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
    0x76dc4190, 0x1db7106, 0x98d220bc, 0xefd5102a, 0x71b18589, 0x6b6b51f, 0x9fbfe4a5, 0xe8b8d433,
    0x7807c9a2, 0xf00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x86d3d2d, 0x91646c97, 0xe6635c01,
    0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e, 0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
    0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
    0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
    0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0, 0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
    0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
    0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
    0xedb88320, 0x9abfb3b6, 0x3b6e20c, 0x74b1d29a, 0xead54739, 0x9dd277af, 0x4db2615, 0x73dc1683,
    0xe3630b12, 0x94643b84, 0xd6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0xa00ae27, 0x7d079eb1,
    0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
    0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc, 0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
    0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
    0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
    0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236, 0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
    0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
    0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x26d930a, 0x9c0906a9, 0xeb0e363f, 0x72076785, 0x5005713,
    0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0xcb61b38, 0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0xbdbdf21,
    0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
    0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
    0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
    0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
    0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
    0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94, 0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d,
]


def to_byte(value):
    """Clamp an integer to a signed byte."""
    value &= 0xFF
    return value - 256 if value > 127 else value


def hex_to_byte(value):
    return to_byte(int(value, 16))


def hexs_to_bytes(value):
    return [hex_to_byte(value[index:index + 2]) for index in range(0, len(value), 2)]


def int_to_bytes(value):
    """Return a 32-bit integer as four signed bytes."""
    return [to_byte(value >> shift) for shift in (24, 16, 8, 0)]


def string_to_bytes(value):
    """Match the JavaScript URI encoding behavior."""
    encoded = urllib.parse.quote(value, safe="")
    result = []
    index = 0
    while index < len(encoded):
        if encoded[index] == "%" and index + 2 < len(encoded):
            result.append(hex_to_byte(encoded[index + 1:index + 3]))
            index += 3
        else:
            result.append(to_byte(ord(encoded[index])))
            index += 1
    return result


def hex_format(value):
    return f"{value & 0xFF:02x}"


def bytes_to_hex(values):
    return "".join(hex_format(value) for value in values)


def bytes_to_string(values):
    return urllib.parse.unquote("".join("%" + hex_format(value) for value in values))


def copy_to_bytes(source, source_offset, destination, destination_offset, count):
    for index in range(count):
        if source_offset + index < len(source):
            destination[destination_offset + index] = source[source_offset + index]
    return destination


def padding_array_zero(length):
    return [0] * length


def hex_to_bytes_simple(value):
    return [int(value[index:index + 2], 16) for index in range(0, len(value), 2)]


SBOX_BYTES = hex_to_bytes_simple(__SBOX__)


def xor_byte(first, second):
    return to_byte(to_byte(first) ^ to_byte(second))


def xors(data, key):
    if not key:
        return data[:]
    return [xor_byte(value, key[index % len(key)]) for index, value in enumerate(data)]


def xor_encode(key, data):
    return base64_encode(xors(string_to_bytes(data), string_to_bytes(key)))


def gen_crc32(values):
    crc = 0xFFFFFFFF
    for value in values:
        value &= 0xFF
        crc = (crc >> 8) ^ CRC32_TABLE[(crc ^ value) & 0xFF]
    return bytes_to_hex(int_to_bytes(crc ^ 0xFFFFFFFF))


def b64_encode_3to4(chunk, alphabet, padding):
    length = len(chunk)
    b0 = chunk[0]
    b1 = chunk[1] if length > 1 else 0
    b2 = chunk[2] if length > 2 else 0
    if length == 1:
        return alphabet[(b0 >> 2) & 0x3F] + alphabet[((b0 << 4) & 0x30) + ((b1 >> 4) & 0xF)] + padding + padding
    if length == 2:
        return alphabet[(b0 >> 2) & 0x3F] + alphabet[((b0 << 4) & 0x30) + ((b1 >> 4) & 0xF)] + alphabet[((b1 << 2) & 0x3C) + ((b2 >> 6) & 0x3)] + padding
    return alphabet[(b0 >> 2) & 0x3F] + alphabet[((b0 << 4) & 0x30) + ((b1 >> 4) & 0xF)] + alphabet[((b1 << 2) & 0x3C) + ((b2 >> 6) & 0x3)] + alphabet[b2 & 0x3F]


def b64_decode_4to3(indices):
    length = len(indices)
    result = []
    if length >= 2:
        result.append(to_byte(((indices[0] << 2) & 0xFF) + ((indices[1] >> 4) & 0x3)))
    if length >= 3:
        result.append(to_byte(((indices[1] << 4) & 0xFF) + ((indices[2] >> 2) & 0xF)))
    if length >= 4:
        result.append(to_byte(((indices[2] << 6) & 0xFF) + (indices[3] & 0x3F)))
    return result


def base64_encode_core(values, alphabet, padding):
    if not values:
        return ""
    unsigned = [value & 0xFF for value in values]
    result = []
    index = 0
    while index < len(unsigned):
        if index + 3 <= len(unsigned):
            result.append(b64_encode_3to4(unsigned[index:index + 3], alphabet, padding))
            index += 3
        else:
            result.append(b64_encode_3to4(unsigned[index:], alphabet, padding))
            break
    return "".join(result)


def base64_decode_core(value, alphabet, padding):
    padding_index = value.find(padding)
    characters = value[:padding_index] if padding_index != -1 else value
    indices = [alphabet.index(character) for character in characters]
    result = []
    index = 0
    while index < len(indices):
        if index + 4 <= len(indices):
            result.extend(b64_decode_4to3(indices[index:index + 4]))
            index += 4
        else:
            result.extend(b64_decode_4to3(indices[index:]))
            break
    return result


def base64_encode(values):
    return base64_encode_core(values, BASE64_ALPHABET, BASE64_PADDING)


def base64_encode_private(values, alphabet=None, padding=None):
    return base64_encode_core(values, alphabet or PRIVATE_B64_ALPHABET, padding or PRIVATE_B64_PADDING)


def base64_decode(value):
    return base64_decode_core(value, BASE64_ALPHABET, BASE64_PADDING)


def sub_bytes(block):
    return [to_byte(SBOX_BYTES[16 * ((value >> 4) & 0xF) + (value & 0xF)]) for value in block]


def shift_add(first, second):
    return to_byte(first + second)


def shifts(data, key):
    if not key:
        return data[:]
    return [shift_add(value, key[index % len(key)]) for index, value in enumerate(data)]


def apply_round_key(block):
    """Apply the custom sequence of round-key operations."""
    round_key = __ROUND_KEY__
    index = 0
    while index < len(round_key):
        operation = hex_to_byte(round_key[index:index + 2])
        argument = hex_to_byte(round_key[index + 2:index + 4])
        if operation == 0:
            if argument + 0x100 < 0:
                return []
        elif operation == 1:
            block = [xor_byte(value, argument) for value in block] if block else []
        elif operation == 2:
            block = [shift_add(value, argument) for value in block] if block else []
        elif operation in (3, 4, 5, 6):
            updated = []
            for value in block:
                if operation == 3:
                    updated.append(xor_byte(value, argument))
                    argument = to_byte(argument + 1)
                elif operation == 4:
                    updated.append(shift_add(value, argument))
                    argument = to_byte(argument + 1)
                elif operation == 5:
                    updated.append(xor_byte(value, argument))
                    argument = to_byte(argument - 1)
                else:
                    updated.append(shift_add(value, argument))
                    argument = to_byte(argument - 1)
            block = updated
        index += 4
    return block


def generate_random_iv():
    return [to_byte(random.randint(0, 255)) for _ in range(4)]


def expand_key(key_bytes):
    if not key_bytes:
        return padding_array_zero(64)
    if len(key_bytes) >= 64:
        return key_bytes[:64]
    return [key_bytes[index % len(key_bytes)] for index in range(64)]


def pad_pkcs7(data):
    if not data:
        return padding_array_zero(64)
    data_length = len(data)
    remainder = data_length % 64
    padding_length = 64 - remainder - 4 if remainder <= 60 else 128 - remainder - 4
    padded = [0] * (data_length + padding_length + 4)
    copy_to_bytes(data, 0, padded, 0, data_length)
    copy_to_bytes(int_to_bytes(data_length), 0, padded, data_length + padding_length, 4)
    return padded


def blocks_from_bytes(values):
    if len(values) % 64 != 0:
        return []
    return [values[index * 64:(index + 1) * 64] for index in range(len(values) // 64)]


def generate_iv():
    seed_bytes = expand_key(string_to_bytes(__SEED_KEY__))
    random_bytes = generate_random_iv()
    seed_bytes = xors(seed_bytes, expand_key(random_bytes))
    return expand_key(seed_bytes), random_bytes


def aes(input_string):
    """Run the custom CBC-like encryption used by the slider."""
    data_bytes = string_to_bytes(input_string)
    iv, raw_iv = generate_iv()
    combined = data_bytes + string_to_bytes(gen_crc32(data_bytes))
    blocks = blocks_from_bytes(pad_pkcs7(combined))
    result = raw_iv[:] + [0] * (len(blocks) * 64)
    previous = iv[:]
    for index, block in enumerate(blocks):
        block = xors(apply_round_key(block), iv)
        block = shifts(block, previous)
        block = xors(block, previous)
        previous = sub_bytes(sub_bytes(block))
        copy_to_bytes(previous, 0, result, 64 * index + 4, 64)
    return base64_encode_private(result)


def sample_arr(values, target_length):
    if len(values) <= target_length:
        return values
    result = []
    for index, value in enumerate(values):
        if index >= (len(result) * (len(values) - 1)) / (target_length - 1):
            result.append(value)
    return result


def unique_2d_array(values, column=0):
    seen = set()
    result = []
    for row in values:
        key = row[column] if column < len(row) else None
        if key is not None and key not in seen:
            seen.add(key)
            result.append(row)
    return result


def generate_uuid(length=32):
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(characters) for _ in range(length))


def generate_cb():
    characters = list(generate_uuid(32))
    for index, position in enumerate(CB_POS):
        if position < len(characters):
            characters[position] = CB_CODE[index]
    return aes("".join(characters))


def encode_trace_point(token, x, y, elapsed, trust):
    return xor_encode(token, f"{round(x)},{round(y)},{elapsed},{trust}")


def build_slider_data(token, trace_points: List[Tuple[float, float, int, int]], slider_left, slider_width, mouse_down_counts=1):
    """Encode the fields expected by the slider check request."""
    trace_data = [xor_encode(token, f"{round(point[0])},{round(point[1])},{point[2]},{point[3]}") for point in trace_points]
    atom_trace_data = unique_2d_array(trace_points, 2)
    timestamps = sorted(set(point[2] for point in atom_trace_data))
    position_percent = int(slider_left) / slider_width * 100
    return {
        "d": aes(":".join(sample_arr(trace_data, SAMPLE_NUM))),
        "m": "",
        "p": aes(xor_encode(token, str(position_percent))),
        "f": aes(xor_encode(token, ",".join(str(value) for value in timestamps))),
        "ext": aes(xor_encode(token, f"{mouse_down_counts},{len(trace_data)}")),
    }


def generate_track(distance, duration_ms=800):
    """Create a varied drag path with approach and alignment stages."""
    points = []
    current = 0.0
    elapsed = 0
    middle = distance * random.uniform(0.50, 0.60)
    while current < middle:
        acceleration = 2.0 + random.uniform(0, 3.0) * (current / max(middle, 1))
        current = min(middle, current + acceleration + random.uniform(0, 1))
        y = random.gauss(0, 0.8) + math.sin(current / 25) * 2
        elapsed += random.randint(6, 12)
        points.append((current, y, elapsed, 1))

    fast = distance * random.uniform(0.88, 0.94)
    while current < fast:
        velocity = 4.0 + random.uniform(0, 4) * (1 - (current - middle) / max(fast - middle, 1))
        current = min(fast, current + velocity + random.uniform(-0.3, 0.8))
        y = random.gauss(0, 0.6) + math.sin(current / 18) * 1.2
        elapsed += random.randint(7, 14)
        points.append((current, y, elapsed, 1))

    while current < distance - 3:
        velocity = max(0.3, 2.5 * (distance - current) / max(distance, 1))
        current = min(distance - 3, current + velocity + random.uniform(-0.3, 0.2))
        y = random.gauss(0, 0.5) + math.sin(current / 12)
        elapsed += random.randint(15, 30)
        points.append((current, y, elapsed, 1))

    while current < distance:
        current = min(distance, current + random.uniform(0.2, 0.5))
        elapsed += random.randint(20, 45)
        points.append((current, random.gauss(0, 0.3), elapsed, 1))
    if points[-1][0] != distance:
        elapsed += random.randint(5, 10)
        points.append((distance, 0, elapsed, 1))
    return points


def url_to_cv2(url):
    """Download an image and convert it to an OpenCV array."""
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    if image.mode == "RGBA":
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)
    return cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)


def find_gap_position(background, front):
    """Combine several matching methods and reject outlying positions."""
    front_rgb = front[:, :, :3]
    alpha = front[:, :, 3]
    _, mask = cv2.threshold(alpha, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x_crop, y_crop, width_crop, height_crop = cv2.boundingRect(contours[0])
    else:
        x_crop, y_crop = 0, 0
        width_crop, height_crop = front.shape[1], front.shape[0]

    front_crop = front_rgb[y_crop:y_crop + height_crop, x_crop:x_crop + width_crop]
    mask_crop = mask[y_crop:y_crop + height_crop, x_crop:x_crop + width_crop]
    results = []

    result = cv2.matchTemplate(background, front_crop, cv2.TM_CCOEFF_NORMED, mask=mask_crop)
    _, score, _, location = cv2.minMaxLoc(result)
    results.append(("CCOEFF_crop", location[0] + x_crop, score))

    background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    front_gray = cv2.cvtColor(front_rgb, cv2.COLOR_BGR2GRAY)
    background_sobel = np.abs(cv2.Sobel(background_gray, cv2.CV_64F, 1, 0, ksize=3)).astype(np.uint8)
    front_sobel = np.abs(cv2.Sobel(front_gray, cv2.CV_64F, 1, 0, ksize=3)).astype(np.uint8)
    background_canny = cv2.Canny(background_gray, 50, 150)
    front_canny = cv2.Canny(front_gray, 50, 150)
    eroded = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)
    front_canny = cv2.bitwise_and(front_canny, front_canny, mask=eroded)

    for name, left, right, mask_value in (
        ("Canny", background_canny, front_canny, None),
        ("Sobel", background_sobel, front_sobel, mask),
        ("CCORR", background, front_rgb, mask),
    ):
        method = cv2.TM_CCORR_NORMED if name == "CCORR" else cv2.TM_CCOEFF_NORMED
        if mask_value is None:
            result = cv2.matchTemplate(left, right, method)
        else:
            result = cv2.matchTemplate(left, right, method, mask=mask_value)
        _, score, _, location = cv2.minMaxLoc(result)
        results.append((name, location[0], score))

    positions = [item[1] for item in results]
    median = sorted(positions)[len(positions) // 2]
    inliers = [value for value in positions if abs(value - median) <= 15]
    return float(sorted(inliers)[len(inliers) // 2] if len(inliers) >= 2 else median)


def find_gap_position_v1(background, front):
    """Keep the original three-method matcher available for comparison."""
    front_rgb = front[:, :, :3]
    alpha = front[:, :, 3]
    _, mask = cv2.threshold(alpha, 50, 255, cv2.THRESH_BINARY)
    results = []
    result = cv2.matchTemplate(background, front_rgb, cv2.TM_CCOEFF_NORMED, mask=mask)
    _, _, _, location = cv2.minMaxLoc(result)
    results.append(location[0])
    background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    front_gray = cv2.cvtColor(front_rgb, cv2.COLOR_BGR2GRAY)
    background_edges = cv2.Canny(background_gray, 50, 150)
    front_edges = cv2.Canny(front_gray, 50, 150)
    eroded = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)
    front_edges = cv2.bitwise_and(front_edges, front_edges, mask=eroded)
    result = cv2.matchTemplate(background_edges, front_edges, cv2.TM_CCOEFF_NORMED)
    _, _, _, location = cv2.minMaxLoc(result)
    results.append(location[0])
    result = cv2.matchTemplate(background, front_rgb, cv2.TM_CCORR_NORMED, mask=mask)
    _, _, _, location = cv2.minMaxLoc(result)
    results.append(location[0])
    return float(sorted(results)[len(results) // 2])


API_SERVER = "c.dun.163.com"
CAPTCHA_ID = "eda6d7f57cf54b5d8f9b0ed24e5b6e66"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/149.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://dun.163.com/",
}


def parse_jsonp(response):
    match = re.search(r"\((\{.*\})\)", response.text)
    return json.loads(match.group(1)) if match else {}


def get_config(session):
    callback = f"__JSONP_{random.randint(10000000, 99999999)}"
    params = {
        "referer": "https://dun.163.com/trial/jigsaw-wap", "zoneId": "", "id": CAPTCHA_ID,
        "ipv6": "false", "runEnv": "10", "iv": "5", "loadVersion": "2.5.4", "callback": f"{callback}_0",
    }
    return parse_jsonp(session.get(f"https://{API_SERVER}/api/v2/getconf", params=params, timeout=15))


def get_captcha(session, fingerprint="", ir_token=""):
    callback = f"__JSONP_{random.randint(10000000, 99999999)}"
    params = {
        "referer": "https://dun.163.com/trial/jigsaw-wap", "zoneId": "CN31", "dt": ir_token,
        "irToken": ir_token, "id": CAPTCHA_ID, "fp": fingerprint, "https": "true", "type": "",
        "version": "2.28.5", "dpr": "1", "dev": "1", "cb": generate_cb(), "ipv6": "false",
        "runEnv": "10", "group": "", "scene": "", "lang": "zh-CN", "sdkVersion": "",
        "loadVersion": "2.5.4", "iv": "4", "user": "", "width": "855", "audio": "false",
        "sizeType": "10", "smsVersion": "v3", "token": "", "callback": f"{callback}_0",
    }
    return parse_jsonp(session.get(f"https://{API_SERVER}/api/v3/get", params=params, timeout=15))


def check_captcha(session, token, slider_data, zone_id="CN31", ir_token=""):
    callback = f"__JSONP_{random.randint(10000000, 99999999)}"
    params = {
        "referer": "https://dun.163.com/trial/jigsaw-wap", "zoneId": zone_id, "dt": ir_token,
        "id": CAPTCHA_ID, "token": token, "data": json.dumps(slider_data, separators=(",", ":"), ensure_ascii=True),
        "width": "855", "type": "2", "version": "2.28.5", "cb": generate_cb(), "user": "",
        "extraData": "", "bf": "0", "runEnv": "10", "sdkVersion": "", "loadVersion": "2.5.4",
        "iv": "4", "callback": f"{callback}_0",
    }
    return parse_jsonp(session.get(f"https://{API_SERVER}/api/v3/check", params=params, timeout=15))


def solve_captcha(session, max_retries=10) -> Optional[str]:
    """Run the complete puzzle flow and return a validation string on success."""
    for attempt in range(max_retries):
        print(f"\nAttempt {attempt + 1}/{max_retries}")
        print("[1/4] Requesting puzzle images...")
        captcha_data = get_captcha(session)
        if captcha_data.get("error") != 0:
            print(f"Puzzle request failed: {captcha_data}")
            continue

        data = captcha_data["data"]
        token = data["token"]
        print(f"Token: {token[:20]}...")
        print(f"Type: {data.get('type', 2)}")
        print("[2/4] Estimating the gap position...")
        try:
            background = url_to_cv2(data["bg"][0])
            front = url_to_cv2(data["front"][0])
            gap_x = find_gap_position(background, front)
            print(f"Background: {background.shape}; piece: {front.shape}")
            print(f"Gap position: {gap_x:.1f}px")
        except Exception as error:
            print(f"Image processing failed: {error}")
            continue

        print("[3/4] Building motion data...")
        control_width = 855
        distance = gap_x * control_width / background.shape[1] + random.uniform(-1, 2)
        trace_points = generate_track(distance, duration_ms=random.randint(600, 1200))
        slider_data = build_slider_data(token, trace_points, distance, control_width)
        print(f"Distance: {distance:.1f}px; points: {len(trace_points)}")

        print("[4/4] Submitting the puzzle...")
        result = check_captcha(session, token, slider_data, data.get("zoneId", "CN31"))
        print(f"Response: error={result.get('error')}; result={result.get('data', {}).get('result')}")
        if result.get("error") == 0 and result.get("data", {}).get("result"):
            validate = result.get("data", {}).get("validate", "")
            print("Puzzle completed.")
            print(f"Validation: {validate}")
            return validate
        print("The response was not accepted; trying again.")
    return None


def main():
    print("Yidun slider demo: https://dun.163.com/trial/jigsaw-wap")
    session = requests.Session()
    session.headers.update(HEADERS)
    validate = solve_captcha(session, max_retries=15)
    if validate:
        print(f"Done. Validation: {validate}")
    else:
        print("All attempts failed.")


if __name__ == "__main__":
    main()
