import logging

logger = logging.getLogger("SessionManager")



class SessionManager:
    """Manages all active, authenticated client sessions."""
    def __init__(self, slide_layouts_metadata: dict):
        # The session_id will be the key for our dictionary
        self.active_sessions = {}
        logger.info("SessionManager initialized.")
        self.slide_layouts_metadata = slide_layouts_metadata


    # def start_session(self, session_id: str):
    #     """Adds a new session_id to the active sessions registry."""
    #     if session_id not in self.active_sessions:
    #         self.active_sessions[session_id] = {"status": "active"}
    #         logger.info(f"Session started and authorized: {session_id}")
    #
    # def is_session_active(self, session_id: str) -> bool:
    #     """Checks if a session has been authorized and is active."""
    #     return session_id in self.active_sessions

    def get_presentation(self, presentation_filename: str):
        """Retrieves the presentation for a given session_id."""
        return self.active_sessions[presentation_filename].get('presentation')

