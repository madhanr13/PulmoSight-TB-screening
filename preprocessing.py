"""Input validation and radiograph preprocessing for the TB classifier."""

from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image, UnidentifiedImageError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TARGET_SIZE = (224, 224)


class ImageValidationError(ValueError):
    pass


@dataclass
class ProcessedImage:
    tensor: np.ndarray
    filename: str
    image_size: dict


def preprocess_upload(upload) -> ProcessedImage:
    filename = upload.filename or "radiograph"
    extension = "." + \
        filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise ImageValidationError("Use a JPG, PNG, or WEBP chest radiograph.")

    raw = upload.read()
    if not raw:
        raise ImageValidationError("The uploaded image is empty.")

    try:
        image = Image.open(BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise ImageValidationError(
            "That file is not a readable image.") from error

    original_size = {"width": image.width, "height": image.height}
    image = image.convert("RGB").resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    array = np.asarray(image, dtype=np.float32)
    # MobileNetV2 expects pixels scaled to [-1, 1].
    tensor = (array / 127.5) - 1.0
    return ProcessedImage(tensor=np.expand_dims(tensor, axis=0), filename=filename, image_size=original_size)
