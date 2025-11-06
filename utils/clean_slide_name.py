import logging
import re

logger = logging.getLogger(__name__)
def clean_slide_name(original_string) -> str:
    logger.info(f'--- Cleaning slide name: {original_string}')
    """
    Removes any XML characters from slide names, replaces spaces with _ and makes lower case
    :param original_string:
    :return: string
    """
    try:
        regex = r'[\\/:\*\?"<>\|]'
        remove_xml_characters = re.sub(regex, '', original_string)
        sanitised_name = remove_xml_characters.replace(' ', '_').lower()
        logger.info(f'--- Returning sanitised name: {sanitised_name}')
        return sanitised_name
    except Exception as e:
        logger.error(f"unable to clean slide name:{e}")
        return original_string