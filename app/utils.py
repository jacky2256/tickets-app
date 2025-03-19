import os
import logging
from app.settings import OUT_DIR


def save_content_in_file(content: str, directory='output_content',
                         filename='output_linkedin', extension='html'):
    """
    Saves the given content to a file in the specified directory with the specified filename and extension.

    Args:
        content (str): The content to be saved.
        directory (str, optional): The directory where the file will be saved. Defaults to 'output_zoominfo'.
        filename (str, optional): The name of the file without the extension. Defaults to 'zoominfo'.
        extension (str, optional): The file extension. Defaults to 'html'.
    """
    try:
        path_dir = os.path.join(str(OUT_DIR.absolute()), directory)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        path = f"{path_dir}/{filename}.{extension}"
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        # logger.info(f"Data was saved to {path}")
    except OSError as err:
        logging.error(f"OS error occured: {err}")
    except Exception as err:
        logging.error(f"Unexpected error occurred: {err}")