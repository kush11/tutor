"""
Image encoding helpers for the verification app.
"""
import logging

log = logging.getLogger(__name__)


class InvalidImageData(Exception):
    """
    The provided image data could not be decoded.
    """
    pass


def decode_image_data(data):
    """
    Decode base64-encoded image data.

    Arguments:
        data (str): The raw image data, base64-encoded.

    Returns:
        str

    Raises:
        InvalidImageData: The image data could not be decoded.

    """
    try:
        return (data.split(",")[1]).decode("base64")
    except (IndexError, UnicodeEncodeError):
        log.exception("Could not decode image data")
        raise InvalidImageData
