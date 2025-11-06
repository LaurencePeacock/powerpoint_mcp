from mcp.server import FastMCP
from fastmcp.server.context import Context
import logging
from SessionManager import SessionManager
from utils.clean_slide_name import clean_slide_name

logger = logging.getLogger(__name__)

def register_text_tools(
        pp_app: FastMCP,
        session_manager: SessionManager
):
    @pp_app.tool()
    def count_words(text: str)-> int:
        return len(text.split())

    def placeholder_has_space_for_text(text: str, layout_name: str) -> bool:
        try:
            text_length = len(text.split())
            logger.info(f'Text length: {text_length}')
            text_limit = 0
            for layout in session_manager.slide_layouts_metadata['layouts']:
                if layout["slide_layout_name"] == layout_name:
                    logger.info(f'Found slide layout from metadata with name: {layout_name}')
                    text_limit = 200
                    logger.info(f'Text Limit is {text_limit}')
                    break
            if text_limit:
                return True if text_length <= text_limit else False
            return False
        except Exception as e:
            logger.error(e)

    @pp_app.tool()
    def add_text_to_slide(
            presentation_filename: str,
            text: str,
            layout_name: str,
            slide_name: str = None,
            slide_index: int = None,

    ) -> dict:
        """
        IMPORTANT - only use the slide_name or slide_index provided to find the slide. DO NOT USE the get_presentation_summary tool
        IMPORTANT - follow the tool code precisely. Do not attempt to work out your own plan.

        This tool:
        1. Finds a slide by its index or name
        2. Locates an available content text placeholder
        3. Checks to see if the text placeholder can fit the text provided
        4. If the text placeholder can fit the text, adds the text. If the text placeholder cannot fit the text,
        returns a message stating this.

        This only modifies the slide in memory. Call 'save_presentation' to persist changes.
        :param presentation_filename: string. The filename of the presentation
        :param text: string. The string of text to add to the slide.
        :param layout_name: string. The name of the slide layout template taken from the dictionary returned from get_slide_layouts_metadata,
        :param slide_name: string or None. The name of the slide to add text to, E.G 'title' or 'main'
        :param slide_index: integer or None. The index of the slide to add text to (0-based).


        :return: a dictionary indicating the success or failure of the tool with an accompanying message

        Example of Successful Return Dictionary:
        {
            "status": "success",
            "message": "Successfully added text to slide results slide, index: 5. Remember to save."
        }


        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: Invalid slide index. The presentation only has 3 slides."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: Unable to find slide to add text to."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: This is either because no placeholder for text was found on the slide. Or no empty content placeholder was found on slide results_slide, index: 4. Please add another slide."
        }
        """
        logger.info(f"---- Attempting to add text to slide")
        presentation = session_manager.get_presentation(presentation_filename)
        if not presentation:
            return {
                "status": "failure",
                "message": "Presentation not found for the current session in add_new_slide_tool."
            }
        logger.info(
            f"---- Tool called with arguments: text: {text}, slide_name: {slide_name}, slide_index: {slide_index}, layout_name: {layout_name}")
        if slide_index and slide_index >= len(presentation.slides):
            return {
                "status": "failure",
                "message": f"Error: Invalid slide index. The presentation only has {len(presentation.slides)} slides."
            }
        logger.info(f"---- Provided with slide name: {slide_name} and / or index {slide_index}")
        if slide_name:
            logger.info(f"---- Using the slide name to find the slide in the presentation")
            cleaned_name = clean_slide_name(slide_name)
            for named_slide in presentation.slides:
                if named_slide.name == cleaned_name:
                    slide_to_edit = named_slide
        else:
            logger.info(f"---- slide name was not provided. Using Index to find the slide in the presentation")
            slide_to_edit = presentation.slides[slide_index]

        if not slide_to_edit:
            return {
                "status": "failure",
                "message": "Error: Unable to find slide to add text to."
            }

        # Find the first empty placeholder suitable for body or content text
        text_placeholder = None
        logger.info(f"---- finding placeholders on slide: {slide_to_edit.name}")
        logger.info(f"---- There are {len(slide_to_edit.placeholders)} placeholders on slide")
        for shape in slide_to_edit.placeholders:
            logger.info(f"---- Placeholder Type: {shape.placeholder_format.type}")
            if shape.placeholder_format.type.name in ('OBJECT',):
                logger.info(f"---- Found object placeholders on slide: {slide_to_edit.name}")
                if shape.has_text_frame and not shape.text_frame.text:
                    logger.info(f"---- Checking if placeholder_has_space_for_text")
                    if placeholder_has_space_for_text(text, layout_name):
                        text_placeholder = shape
                        break
                    logger.info(f"---- No room for text in the available placeholders")
        if text_placeholder:
            text_placeholder.text_frame.text = text
            logger.info(f"---- Successfully added text to slide {slide_to_edit.name}, index: {slide_index}.")
            return {
                "status": "success",
                "message": f"Successfully added text to slide {slide_to_edit.name}, index: {slide_index}. Remember to save."
            }
        else:
            logger.warning(
                f"---- No empty content placeholder was found on slide {slide_to_edit.name}, index: {slide_index}. Please add another slide"
            )
            return {
                "status": "failure",
                "message": f"Error: This is either because no placeholder for text was found on the slide. "
                    f"Or no empty content placeholder was found on slide {slide_to_edit.name}, index: {slide_index}. Please add another slide."
            }

    @pp_app.tool()
    def add_title_to_slide(
            presentation_filename: str,
            title: str,
            slide_name: str = None,
            slide_index: int = None
    )-> dict:
        """
        IMPORTANT - only use the slide_name or slide_index provided to find the slide. DO NOT USE the get_presentation_summary tool
        IMPORTANT - follow the tool code precisely. Do not attempt to work out your own plan.

        Finds a slide by its index or name and adds a title to the Title content placeholder.
        This only modifies the slide in memory. Call 'save_presentation' to persist changes.
        :param presentation_filename: string. The presentation filename.
        :param text: string. The string of text to add to the slide.
        :param slide_name: string or None. The name of the slide to add text to, E.G 'title' or 'main'
        :param slide_index: integer or None. The index of the slide to add text to (0-based).

        :return: a dictionary indicating the success or failure of the tool with an accompanying message

        Example of Successful Return Dictionary:
        {
            "status": "success",
            "message": "Successfully added title to slide results slide, index: 5. Remember to save."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: Invalid slide index. The presentation only has 3 slides."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: Unable to find slide to add title to."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: This is either because no placeholder for title was found on the slide. Or no empty content placeholder was found on slide results_slide, index: 4. Please add another slide."
        }

        """
        logger.info(f"---- Attempting to add title to slide")
        presentation = session_manager.get_presentation(presentation_filename)
        if not presentation:
            return {
                "status": "failure",
                "message": "Presentation not found for the current session in add_new_slide_tool."
            }
        logger.info(
            f"---- Tool called with arguments: title: {title}, slide_name: {slide_name}, slide_index: {slide_index}")
        if slide_index and slide_index >= len(presentation.slides):
            return {
                "status": "failure",
                "message": f"Error: Invalid slide index. The presentation only has {len(presentation.slides)} slides."
            }
        logger.info(f"---- Provided with slide name: {slide_name} and / or index {slide_index}")
        if slide_name:
            logger.info(f"---- Using the slide name to find the slide in the presentation")
            cleaned_name = clean_slide_name(slide_name)
            for named_slide in presentation.slides:
                if named_slide.name == cleaned_name:
                    slide_to_edit = named_slide
        else:
            logger.info(f"---- slide name was not provided. Using Index to find the slide in the presentation")
            slide_to_edit = presentation.slides[slide_index]

        if not slide_to_edit:
            return {
                "status": "failure",
                "message": "Error: Unable to find slide to add text to."
            }

        # Find the first empty placeholder suitable for body or content text
        title_placeholder = None
        logger.info(f"---- finding placeholders on slide: {slide_to_edit.name}")
        logger.info(f"---- There are {len(slide_to_edit.placeholders)} placeholders on slide")
        for shape in slide_to_edit.placeholders:
            logger.info(f"---- Placeholder Type: {shape.placeholder_format.type}")
            if shape.placeholder_format.type.name in ('TITLE',):
                logger.info(f"---- found object placeholders on slide: {slide_to_edit.name}")
                if shape.has_text_frame and not shape.text_frame.text:
                    text_placeholder = shape
                    break
        if text_placeholder:
            text_placeholder.text_frame.text = title
            logger.info(f"---- Successfully added text to slide {slide_to_edit.name}, index: {slide_index}.")
            return {
                "status": "success",
                "message": f"Successfully added text to slide {slide_to_edit.name}, index: {slide_index}. Remember to save."
            }
        else:
            logger.warning(
                f"---- No empty content placeholder was found on slide {slide_to_edit.name}, index: {slide_index}. Please add another slide"
            )
            return {
                "status": "failure",
                "message": f"Error: This is either because no placeholder for text was found on the slide. "
                           f"Or no empty content placeholder was found on slide {slide_to_edit.name}, index: {slide_index}. Please add another slide."
            }

    @pp_app.tool()
    def add_subtitle_to_slide(
            presentation_filename: str,
            subtitle: str,
            slide_name: str = None,
            slide_index: int = None
    ) -> dict:
        """
        IMPORTANT - only use the slide_name or slide_index provided to find the slide. DO NOT USE the get_presentation_summary tool
        IMPORTANT - follow the tool code precisely. Do not attempt to work out your own plan.

        Finds a slide by its index or name and adds a title to the Title content placeholder.
        This only modifies the slide in memory. Call 'save_presentation' to persist changes.
        :param presentation_filename: string. The presentation filename.
        :param text: string. The string of text to add to the slide.
        :param slide_name: string or None. The name of the slide to add text to, E.G 'title' or 'main'
        :param slide_index: integer or None. The index of the slide to add text to (0-based).

        :return: a dictionary indicating the success or failure of the tool with an accompanying message

        Example of Successful Return Dictionary:
        {
            "status": "success",
            "message": "Successfully added title to slide results slide, index: 5. Remember to save."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: Invalid slide index. The presentation only has 3 slides."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: Unable to find slide to add title to."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": "Error: This is either because no placeholder for title was found on the slide. Or no empty content placeholder was found on slide results_slide, index: 4. Please add another slide."
        }

        """
        logger.info(f"---- Attempting to add title to slide")
        presentation = session_manager.get_presentation(presentation_filename)
        if not presentation:
            return {
                "status": "failure",
                "message": "Presentation not found for the current session in add_new_slide_tool."
            }
        logger.info(
            f"---- Tool called with arguments: title: {subtitle}, slide_name: {slide_name}, slide_index: {slide_index}")
        if slide_index and slide_index >= len(presentation.slides):
            return {
                "status": "failure",
                "message": f"Error: Invalid slide index. The presentation only has {len(presentation.slides)} slides."
            }
        logger.info(f"---- Provided with slide name: {slide_name} and / or index {slide_index}")
        if slide_name:
            logger.info(f"---- Using the slide name to find the slide in the presentation")
            cleaned_name = clean_slide_name(slide_name)
            for named_slide in presentation.slides:
                if named_slide.name == cleaned_name:
                    slide_to_edit = named_slide
        else:
            logger.info(f"---- slide name was not provided. Using Index to find the slide in the presentation")
            slide_to_edit = presentation.slides[slide_index]

        if not slide_to_edit:
            return {
                "status": "failure",
                "message": "Error: Unable to find slide to add text to."
            }

        # Find the first empty placeholder suitable for body or content text
        title_placeholder = None
        logger.info(f"---- finding placeholders on slide: {slide_to_edit.name}")
        logger.info(f"---- There are {len(slide_to_edit.placeholders)} placeholders on slide")
        for shape in slide_to_edit.placeholders:
            logger.info(f"---- Placeholder Type: {shape.placeholder_format.type}")
            if shape.placeholder_format.type.name in ('BODY',):
                logger.info(f"---- found object placeholders on slide: {slide_to_edit.name}")
                if shape.has_text_frame and not shape.text_frame.text:
                    text_placeholder = shape
                    break
        if text_placeholder:
            text_placeholder.text_frame.text = subtitle
            logger.info(f"---- Successfully added text to slide {slide_to_edit.name}, index: {slide_index}.")
            return {
                "status": "success",
                "message": f"Successfully added text to slide {slide_to_edit.name}, index: {slide_index}. Remember to save."
            }
        else:
            logger.warning(
                f"---- No empty content placeholder was found on slide {slide_to_edit.name}, index: {slide_index}. Please add another slide"
            )
            return {
                "status": "failure",
                "message": f"Error: This is either because no placeholder for text was found on the slide. "
                           f"Or no empty content placeholder was found on slide {slide_to_edit.name}, index: {slide_index}. Please add another slide."
            }