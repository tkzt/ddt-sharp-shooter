import pyautogui
import numpy as np
import ddddocr
from numpy import ndarray
from skimage import color
from skimage.filters import threshold_otsu


def recog_digit(image: ndarray, ocr: ddddocr.DdddOcr) -> int:
    result = ocr.classification(image)
    try:
        result = int(result)
    except ValueError:
        result = -1
    return result


def cap_screen(pos: tuple[float, float], w: int, h: int) -> ndarray:
    img = pyautogui.screenshot(region=(int(pos[0]-w/2), int(pos[1]-h/2), w, h))
    img = np.array(img)
    return img


def left_side_more_dark(image: ndarray) -> bool:
    image_gray = color.rgb2gray(image)
    shape = image_gray.shape
    image_bin = image_gray > threshold_otsu(image_gray)
    return np.mean(image_bin[:, :shape[1]//2]) < np.mean(image_bin[:, shape[1]//2:])