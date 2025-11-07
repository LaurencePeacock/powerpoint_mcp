import os
import logging
import dotenv
from datetime import datetime
from typing import Dict
from mcp.server import FastMCP
from SessionManager import SessionManager
from utils.presentations.create_new_presentation_from_template import create_new_presentation_from_template
from utils.presentations.save_presentation_to_presentations_directory import save_presentation_to_directory

logger = logging.getLogger(__name__)

def register_presentation_tools(
        pp_app: FastMCP,
        session_manager: SessionManager
):
    @pp_app.tool()
    def set_prs_on_sess_man_and_save_presentation_to_dir(presentation_filename: str) -> Dict:
        """
        Takes the presentation_filename that is stored in the session state under the presentation_filename key
        Creates a new presentation from templates directory
        Sets the presentation on the session manager
        Saves the presentation to presentations directory.

        :param presentation_filename: string This MUST be the same filename that is stored in the session state under the presentation_filename key
        :return: dictionary
        """
        try:
            prs = create_new_presentation_from_template()
            logger.info(f"Setting '{presentation_filename}' as presentation on session manager at id:")
            session_manager.active_sessions[presentation_filename] = {}
            session_manager.active_sessions[presentation_filename]['presentation'] = prs
            # set name on title slide and add title to slide
            slides = prs.slides
            title_slide = slides[0]
            title_slide.name = "Title Slide"
            title = presentation_filename.split("-")[0]
            add_content_to_title_slide(title_slide, title)
            save_presentation_to_directory(prs, f"{presentation_filename}")
            return {
                "status": "success"
            }
        except Exception as e:
            raise Exception(f'Unable to access pptx template in templates directory: {e}')




    @pp_app.tool()
    def save_presentation(presentation_filename: str) -> str:
        """
        Saves the current state of the in-memory presentation to its file on disk.
        This should be called after making modifications like adding slides or content.

        :return: a message indicating the success or failure of the tool.

        Example of Successful Return Message:
            Successfully saved presentation to presentations/work_in_progress.pptx

        Example of Failure Return Message:
            Error: Failed to save presentation. Details: presentations directory does not exist
        """
        try:
            presentation = session_manager.get_presentation(presentation_filename)
            if not presentation:
                return "Error: Failed to save presentation. Details: Presentation not found for session."
            
            logger.info(f"---- Saving presentation to presentations directory as: {presentation_filename}")
            save_presentation_to_directory(presentation, presentation_filename)
            return f"Successfully saved presentation to presentations directory as {presentation_filename}"
        except Exception as e:
            logger.error(f"---- Failed to save presentation: {e}")
            return f"Error: Failed to save presentation. Details: {e}"

    def add_content_to_title_slide(
            title_slide,
            title: str,
            sub_title: str = None):

        date_string = datetime.now().strftime('%d/%m/%Y')

        for placeholder in title_slide.placeholders:
            if placeholder.placeholder_format.type.name in ('TITLE',):
                if placeholder.has_text_frame:
                    title_placeholder = placeholder
                    title_placeholder.text_frame.text = title

    @pp_app.tool()
    def add_title_slide_to_presentation(
            presentation_filename: str,
            title: str,
            sub_title: str = "",
            slide_layout: str = None
    ) -> dict:
        """
        Adds or updates a Title Slide at the 0th index of the presentation.

        - If a title slide already exists, its content is overwritten.
        - If a `slide_layout` is provided and a title slide already exists, the existing title slide is deleted and replaced with a new one using the specified layout.
        - If no title slide exists, a new one is created at the 0th index.

        This only modifies the slide in memory. Call 'save_presentation' to persist changes.

        :param presentation_filename: filename of the presentation file.
        :param title: The title for the presentation. This MUST be provided.
        :param sub_title: Optional. The subtitle for the presentation.
        :param slide_layout: Optional. The user-friendly name of the title slide layout to use (e.g., "Title Slide - Black").
        :return: A dictionary indicating the success or failure of the tool.

        Example of Successful Return Dictionary when title slide already exists:
        {
            "status": "success",
            "title_slide_exists": "True",
            "message": f"Title slide already exists. Successfully overwrote content of exisitng presentation title slide at index 0. Title: {title} Sub_title: {sub_title} "
        }

        Example of Successful Return Dictionary when title slide is new:
        {
            "status": "success",
            "title_slide_exists": "False",
            "message": f"Successfully added new title slide to presentation at index 0. Title: {title} Sub_title: {sub_title} "
        }
        """
        try:
            prs = session_manager.get_presentation(presentation_filename)
            if not prs:
                return {"status": "failure", "message": "Presentation not found for the current session."}

            zero_index_slide = prs.slides[0]
            layout_type = zero_index_slide.slide_layout.name

            # Scenario 1: A title slide exists and a new layout is requested.
            if slide_layout and layout_type.startswith('Jaywing Cover'):
                # 1. Find the new layout from metadata
                layout_to_add = next((l for l in session_manager.slide_layouts_metadata['layouts'] if l['user_friendly_name'] == slide_layout), None)
                if not layout_to_add:
                    return {"status": "failure", "message": f"Slide layout '{slide_layout}' not found."}
                new_layout = prs.slide_layouts[layout_to_add['slide_layout_index']]

                # 1. Add a new slide with the specified layout (it's added to the end)
                new_title_slide = prs.slides.add_slide(new_layout)
                add_content_to_title_slide(new_title_slide, title, sub_title)

                # 2. Delete the current slide at 0th index
                xml_slides = prs.slides._sldIdLst
                slides = list(xml_slides)
                xml_slides.remove(slides[0])


                return {
                    "status": "success",
                    "message": f"Successfully replaced title slide with '{slide_layout}' layout and added content."
                }

            # Scenario 2: A title slide exists, but no new layout is requested.
            elif layout_type.startswith('Jaywing Cover'):
                # Just overwrite its content
                add_content_to_title_slide(zero_index_slide, title, sub_title)
                return {
                    "status": "success",
                    "title_slide_exists": "True",
                    "message": f"Title slide already exists. Successfully overwrote content. Title: {title}, Sub_title: {sub_title}"
                }

            # Scenario 3: No title slide exists at the 0th index.
            else:
                # Add a new title slide
                title_slide_layout = prs.slide_layouts[0] # Default to the first layout
                title_slide = prs.slides.add_slide(title_slide_layout)
                add_content_to_title_slide(title_slide, title, sub_title)

                # Move the newly added title slide to the 0th index
                xml_slides = prs.slides._sldIdLst
                slides = list(xml_slides)
                new_slide_xml = slides[-1]
                xml_slides.remove(new_slide_xml)
                xml_slides.insert(0, new_slide_xml)
                
                return {
                    "status": "success",
                    "title_slide_exists": "False",
                    "message": f"Successfully added new title slide. Title: {title}, Sub_title: {sub_title}"
                }

        except Exception as e:
            logger.error(f"---- Failed to add title slide to presentation: {e}")
            return {"status": "failure", "message": f"Failed to add title slide to presentation. Details: {e}"}

    def add_content_to_thank_you_slide(
            slide,
            name: str,
            job_role: str = "",
            email_address: str = "",
    ):
        placeholders = slide.placeholders
        for placeholder in placeholders:
            if placeholder.placeholder_format.type.name == 'BODY' and placeholder.name == 'Text Placeholder 1':
                placeholder.text_frame.text = name
            if placeholder.placeholder_format.type.name == 'BODY' and placeholder.name == 'Text Placeholder 2':
                placeholder.text_frame.text = job_role
            if placeholder.placeholder_format.type.name == 'BODY' and placeholder.name == 'Text Placeholder 3':
                placeholder.text_frame.text = email_address


    @pp_app.tool()
    def add_thank_you_slide_to_presentation(
            presentation_filename: str,
            name: str,
            job_role: str = "",
            email_address: str = "",
    ) -> dict:
        """
        Adds a Thank You Slide to the end of the working presentation with name, job role and email address.
        If a thank you slide already exists, its content will be overwritten.

        This only modifies the slide in memory. Call 'save_presentation' to persist changes.

        :param presentation_filename: The filename of the presentation.
        :param name: String. The name of the author of the presentation.
        :param job_role: String. Optional. The job_role of the author of the presentation.
        :param email_address: String. Optional. The email address of the author of the presentation.

        :return: a dictionary indicating the success or failure of the tool.

        Example of Successful Return Dictionary:
        {
            "status": "success",
            "message": Successfully added name: Bob Dylan, job role: Legend and email address: bob@dylan to placeholders on the Thank You slide."
        }

        """
        try:
            prs = session_manager.get_presentation(presentation_filename)
            if not prs:
                return {
                    "status": "failure",
                    "message": "Presentation not found for the current session."
                }
            slides = prs.slides
            # Check if last slide is thankyou slide
            if slides[-1].slide_layout.name == '4_Jaywing Thank you Slide':
                add_content_to_thank_you_slide(slides[-1], name, job_role, email_address)
                return {
                    "status": "success",
                    "message": f"Successfully added name: {name}, job role: {job_role} and email address: {email_address} to placeholders on the Thank You slide.",
                }

            layouts = prs.slide_layouts
            for layout in layouts:
                if layout.name == '4_Jaywing Thank you Slide':
                    thank_you_slide = layout
            if thank_you_slide:
                slide = prs.slides.add_slide(thank_you_slide)
                add_content_to_thank_you_slide(slide, name, job_role, email_address)
                return {
                    "status": "success",
                    "message": f"Successfully added new Thank You Slide and added name: {name}, job role: {job_role} and email address: {email_address} to placeholders.",
                }
            else:
                return {
                    "status": "failure",
                    "message": "Unable to locate 4_Jaywing Thank you Slide layout slide in presentation"
                }
        except Exception as e:
            return {
                    "status": "failure",
                    "message": f"Unable to add Thank You slide to presentation: {e}"
                }

    def add_client_x_project_title_and_pagination_to_footers(
            presentation_filename: str,
            client_name: str = "",
            project_title: str = ""
    ) -> dict:
        """
        Adds client and project details to all available footers in the Presentation

        This only modifies the slide in memory. Call 'save_presentation' to persist changes.

        :param presentation_filename: The filename of the presentation.
        :param client_name: String. The name of the client
        :param project_title: String. Optional. The project title

        :return: a dictionary indicating the success or failure of the tool.
        """
        try:
            prs = session_manager.get_presentation(presentation_filename)
            if not prs:
                return {
                    "status": "failure",
                    "message": "Presentation not found for the current session."
                }
            # get all slides
            slides = prs.slides
            # for all slides, get placeholders
            for index, slide in enumerate(slides):
                placeholders = slide.placeholders
                #   find footer placeholders
                for placeholder in placeholders:
                    if placeholder.placeholder_format.type.name == 'FOOTER' and placeholder.text == "Client x Jaywing Project Title":
                        if client_name and project_title:
                            placeholder.text_frame.text = f'{client_name} x {project_title}'
                        else:
                            placeholder.text_frame.text = ""
                    if placeholder.placeholder_format.type.name == 'SLIDE_NUMBER':
                        slide_number = str(index + 1)
                        placeholder.text = slide_number
            return {
                "status": "success",
                "message": "Successfully added Client Name x Jaywing Project Title and pagination to footers"
            }
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Unable to add Client Name x Jaywing Project Title and pagination to presentation: {e}"
            }



    @pp_app.tool()
    def get_slide_to_edit_from_user_slide_number(presentation_filename: str, user_slide_number: int) -> dict:
        """
        Takes a slide number from a user and returns the required slide to edit.
        As users will provide 1-indexed slide numbers, this tool removes 1 from the user_slide_number to return the 0-indexed slide
        Returns the slide to edit at the 'slide' property of the returned dictionary.

        :param presentation_filename:
        :param user_slide_number:
        :return: dict. A dictionary indicating the success or failure of the tool. If successful, the slide to edit is returned at the 'slide' property.
        """
        try:
            prs = session_manager.get_presentation(presentation_filename)
            if not prs:
                return {
                    "status": "failure",
                    "message": "Presentation not found for the current session."
                }
            slides = prs.slides
            slide = slides[user_slide_number-1]
            return {
                "status": "success",
                "slide": slide,
            }
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Unable to get slide to edit from user: {e}"
                    }

    @pp_app.tool()
    def delete_slide(presentation_filename: str, user_slide_number: int) -> dict:
        """
        Deletes a slide at a given index from the presentation
        ONLY EVER use this tool when instructed to by the user
        As users will provide 1-indexed slide numbers, this tool removes 1 from the user_slide_number to return the 0-indexed slide

        This only modifies the presentation in memory. Call 'save_presentation' to persist changes.

        :param presentation_filename:
        :param user_slide_number:
        :return:
        """
        try:
            presentation = session_manager.get_presentation(presentation_filename)
            if not presentation:
                return {
                    "status": "failure",
                    "message": "Presentation not found for the current session."
                }

            slide_index = user_slide_number - 1
            if slide_index < 0 or slide_index >= len(presentation.slides):
                return {
                    "status": "failure",
                    "message": f"Invalid slide index. The presentation has {len(presentation.slides)} slides."
                }

            # Get the internal list of slides
            xml_slides = presentation.slides._sldIdLst
            slides = list(xml_slides)

            xml_slides.remove(slides[slide_index])

            return {
                "status": "success",
                "message": f"Successfully deleted slide at index {slide_index}."
            }
        except Exception as e:
            logger.error(f"---- Failed to delete slide: {e}")
            return {
                "status": "failure",
                "message": f"Failed to delete slide. Details: {e}"
            }

    @pp_app.tool()
    def show_presentation_summary(presentation_filename: str) -> dict:
        """
        CRITICAL INSTRUCTION: NEVER call this tool unless you have EXPLICITLY been asked to by the user
        IMPORTANT: This information is ONLY useful to the user. You MUST NEVER call this tool unprompted.

        This tool returns a dictionary of summary information about the presentation currently being edited
        The presentation summary includes:
         - the total number of slides in the presentation
         - the index number of the slide in the presentation. Slide numbers are 1-indexed
         - the slide layout name of the slide in the presentation.

        :return: presentation_summary dictionary

         Example of Return dictionary
         {
            "total_num_slides": 3,
            "slide_information":
            {
                "slide_index": 1,
                "slide_name": "title",
            },
            {
                "slide_index": 2,
                "slide_name": "summary",
            },
            {
                "slide_index": 3,
                "slide_name": "main_finding",
            }
         }
        """
        try:
            logger.info(f"---- Getting presentation summary")
            presentation = session_manager.get_presentation(presentation_filename)
            if not presentation:
                return {
                    "status": "failure",
                    "message": "Presentation not found for the current session."
                }
            summary = {
                "total_num_slides": len(presentation.slides),
                "slide_information": []
            }
            slides = presentation.slides
            for slide in slides:
                slide_info = {
                    "slide_index": presentation.slides.index(slide) + 1,
                    "slide_name": slide.name,
                }
                summary["slide_information"].append(slide_info)
            return summary
        except Exception as e:
            logger.error(f"---- Failed to get presentation summary: {e}")
            return {
                "status": "failure",
                "message": f"Failed to get presentation summary. Details: {e}"
            }

