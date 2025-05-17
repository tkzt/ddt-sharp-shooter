import time
from skimage.feature import match_template
from typing import Tuple
import numpy as np
from logger import logger
import pyautogui
import ddddocr
from numpy import ndarray
from skimage import color, measure, io, feature
from PIL import Image

_ocr = ddddocr.DdddOcr(show_ad=False)
_ocr.set_ranges("0123456789")


def _recognize_digit(image: ndarray) -> str:
    # ndarray to PIL image
    image = np.array(image)
    image = Image.fromarray(image)
    result = _ocr.classification(image, probability=True)
    s = ""
    for i in result["probability"]:
        s += result["charsets"][i.index(max(i))]
    return s


def _capture_region(region: tuple[int, int, int, int], gray_scale=False) -> ndarray:
    img = pyautogui.screenshot(region=region, imageFilename=f"{time.time()}.png")
    img = img.convert("RGB")
    if gray_scale:
        img = img.convert("L")
    img = np.array(img)
    return img


def _left_side_more_dark(image: ndarray, debug=False) -> bool:
    image_bin = _binarize_image_by_reference(image, (141, 141, 232), 50)
    shape = image_bin.shape
    if debug:
        io.imsave("tmp_left_side_dark.png", image_bin)
    return bool(
        np.mean(image_bin[:, : shape[1] // 2]) > np.mean(image_bin[:, shape[1] // 2 :])
    )


def recognize(region: tuple[int, int, int, int]) -> str:
    image = _capture_region(region)
    result = _recognize_digit(image)
    return result


def recognize_wind(region: tuple[int, int, int, int] | ndarray) -> tuple[int, bool]:
    if isinstance(region, np.ndarray):
        image = region
    else:
        image = _capture_region(region)

    # before everything, try to remove all red color to improve the recognition
    image_bin = _binarize_image_by_reference(np.array(image), (200, 6, 15), 50)
    image[image_bin == 1] = [255, 255, 255]

    result = _recognize_digit(image)
    if len(result) == 3:
        result = result[0] + result[2]

    try:
        result = int(result) / 10
    except ValueError:
        result = 0

    if result < 1:
        image_gray = color.rgb2gray(image)
        image_bin = image_gray > np.mean(image_gray) * 0.618
        image_bin = image_bin[:, : image_bin.shape[1] // 2]

        contours = measure.find_contours(image_bin, 0.8)
        largest_contour = max(contours, key=len)
        min_x = int(np.min(largest_contour[:, 1]))
        max_x = int(np.max(largest_contour[:, 1]))
        w = max_x - min_x
        if w / image_bin.shape[1] < 0.37:
            result += 1

    return result, _left_side_more_dark(image)


def find_template(
    template: np.ndarray, region: Tuple[int, int, int, int] = None
) -> Tuple[int, int] | None:
    """
    Find the coordinates of the best match for a template image within a region.

    Args:
        template (ndarry): template image.
        region (Tuple[int, int, int, int], optional): Region to search (left, top, width, height).

    Returns:
        Tuple[int, int]: Coordinates of the best match's center.
    """

    # Capture the region of the screen
    screenshot_array = _capture_region(region, True)

    # Perform template matching
    result = match_template(screenshot_array, template)

    # The confidence of result should be better then 0.8
    if np.max(result) < 0.8:
        logger.warning("Template matches none result.")
        return None

    ij = np.unravel_index(np.argmax(result), result.shape)
    x, y = ij[::-1]

    # Calculate the center of the matched region
    center_x = x + template.shape[1] // 2
    center_y = y + template.shape[0] // 2

    return center_x, center_y


def _binarize_image_by_reference(
    image: ndarray, reference: tuple[int, int, int], threshold: float
) -> ndarray:
    """
    Binarize the image based on the reference color.

    Args:
        image (ndarray): The input image (should be rgb image).
        reference (tuple[int, int, int]): The reference color (R, G, B).
        threshold (float): The threshold for binarization.

    Returns:
        ndarray: The binarized image.
    """
    distances = np.sqrt(np.sum((image - reference) ** 2, axis=2))
    mask = distances <= threshold
    image = np.where(mask[:, :, np.newaxis], 0, 1)
    image = image[:, :, 0]
    image = np.logical_not(image)
    return image


def _recognize_rect(image: ndarray, debug=False) -> tuple[int, int, int, int]:
    """
    Recognize the rectangle in the image.

    Args:
        image (ndarray): The input image (should be rgb image).

    Returns:
        Tuple[int, int, int, int]: The coordinates of the rectangle (x, y, w, h).
    """
    target_color = np.array([160, 163, 169])
    image = _binarize_image_by_reference(image, target_color, 61.8)

    if debug:
        io.imsave("tmp.png", image)

    image = feature.canny(image, sigma=1)
    contours = measure.find_contours(image, 0.8)
    largest_contour = max(contours, key=len)
    min_x = int(np.min(largest_contour[:, 1]))
    max_x = int(np.max(largest_contour[:, 1]))
    min_y = int(np.min(largest_contour[:, 0]))
    max_y = int(np.max(largest_contour[:, 0]))
    # calculate the width and height of the rectangle
    w = max_x - min_x
    h = max_y - min_y

    if debug:
        # draw the rectangle on the image with matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig, ax = plt.subplots()
        ax.imshow(image, cmap="gray")
        rect = patches.Rectangle(
            (min_x, min_y), w, h, linewidth=1, edgecolor="r", facecolor="none"
        )
        ax.add_patch(rect)
        plt.show()

    return min_x, min_y, w, h


def recognize_ten_units(
    region: tuple[int, int, int, int] | ndarray, debug=False
) -> tuple[int, int]:
    """
    Recognize the ten units in the image.

    Args:
        region (tuple[int, int, int, int]): The region to capture.

    Returns:
        tuple[int, int]: The ten units.
    """
    if isinstance(region, np.ndarray):
        image = region
    else:
        image = _capture_region(region)
    result = _recognize_rect(image, debug)
    return result[2]


if __name__ == "__main__":
    image = io.imread("wind_11.png")
    res = recognize_wind(image)
    print(res)

    # image = io.imread("minimap_7.png")
    # res = recognize_ten_units(image, True)
    # print(res)
