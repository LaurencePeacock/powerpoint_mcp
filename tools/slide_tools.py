from mcp.server import FastMCP
import logging
from SessionManager import SessionManager


logger = logging.getLogger(__name__)

def register_slide_tools(
        pp_app: FastMCP,
        session_manager: SessionManager
):
    @pp_app.tool()
    def add_new_slide(
            presentation_filename: str,
            slide_layout_name: str,
            user_friendly_name: str = None) -> dict:
        """
        Adds a new slide to the current presentation

        Determines a matching slide layout from the session manager slide_layouts_metadata and adds the layout as a new
        slide with a slide name to the current presentation for editing.

        This tool only adds the slide. it does not save the presentation file.
        Call the 'save_presentation' tool to persist changes.

        @param presentation_filename: The filename of the presentation.
        @param slide_layout_name: The name of the slide layout. A required parameter. This corresponds to the slide_layout_name property in slide_layouts_metadata. You must generate this value yourself. It is not user provided.
        @param user_friendly_name: The user friendly name of the slide layout in the slide_layouts_metadata dictionary. This optional parameter may be provided by the user and corresponds to the user_friendly_name property in slide_layouts_metadata

        Example of Successful Return Dictionary:
        {
            "status": "success",
            "message": f"Successfully added new slide weekly report to presentation at slide index 4. "
                       f"Remember to save the presentation with the save_presentation tool."
        }

        Example of Failure Return Dictionary:
        {
                "status": "failure",
                "message": f"Tool failed: Layout template chart_large could not be found."
        }

        Example of Failure Return Dictionary:
        {
            "status": "failure",
            "message": f"Tool failed with an unexpected error"
        }

        """
        logger.info(f"---- Attempting to add new slide with layout")
        try:
            presentation = session_manager.get_presentation(presentation_filename)
            if not presentation:
                return {
                    "status": "failure",
                    "message": "Presentation not found for the current session in add_new_slide_tool."
                }
            # loop gets the matching template dictionary from session_manager.slide_layouts_metadata
            for slide_layout in session_manager.slide_layouts_metadata['layouts']:
                if slide_layout['slide_layout_name'] == slide_layout_name:
                    index = slide_layout['slide_layout_index']
                    break
            # use index to get the layout from template collection in presentation
            new_slide_layout = presentation.slide_layouts[index]
            # add template as new slide
            new_slide = presentation.slides.add_slide(new_slide_layout)
            if user_friendly_name:
                new_slide.name = user_friendly_name
            logger.info(f"Success")
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Unable to find slide template with name: {slide_layout_name}: {e}"
            }

        try:
            slide_index = presentation.slides.index(new_slide)

            logger.info(
                f"---- Successfully added new slide '{new_slide.name}' from template {slide_layout_name} to presentation at slide index {slide_index}. Total slides: {len(presentation.slides)}")
            return {
                "status": "success",
                "message": f"Successfully added new slide '{new_slide.name}' to presentation at slide index {slide_index}. "
                           f"Remember to save the presentation with the save_presentation tool."
            }
        except KeyError:
            logger.warning(f"---- No slide layout found for template '{slide_layout_name}'.")
            return {
                "status": "failure",
                "message": f"Tool failed: Layout template '{slide_layout_name}' could not be found."
            }
        except Exception as e:
            logger.error(f"---- An unexpected error occurred while adding a slide: {e}")
            return {
                "status": "failure",
                "message": f"Tool failed with an unexpected error: {e}"
            }



    @pp_app.tool()
    def get_slide_layouts_metadata(presentation_filename: str) -> dict:
        """
        Returns a dictionary of slide layouts metadata for all the slide layouts that can be used in the presentation.
        """
        try:
            logger.info(f"---- Getting slide layout metadata")
            layouts = [layout for layout in session_manager.slide_layouts_metadata['layouts'] if layout['active'] == True]
            return {
                "status": "success",
                "slide_layout_metadata": layouts
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e)
            }
