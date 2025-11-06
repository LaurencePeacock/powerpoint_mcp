import dotenv
import yaml
import logging
import os
from fastmcp import FastMCP
from fastmcp.exceptions import InvalidSignature
from fastmcp.server.dependencies import get_http_headers
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from fastmcp.server.middleware import Middleware, MiddlewareContext
# from utils.presentations.create_new_presentation_from_template import create_new_presentation_from_template
from SessionManager import SessionManager
from tools.chart_tools import register_chart_tools
from tools.presentation_tools import register_presentation_tools
from tools.text_tools import register_text_tools
from tools.slide_tools import register_slide_tools
from tools.table_tools import register_table_tools
# from utils.presentations.save_presentation_to_S3 import save_presentation_to_presentations_directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pp-mcp-server")
logger.info("Starting PP server")

dotenv.load_dotenv()

logger.info("Generating slide layout metadata for Session Manager")
try:
    with open('indexes/slide_layouts_full.yaml') as slide_yaml:
        slide_layouts_metadata = yaml.safe_load(slide_yaml)
except Exception as e:
    raise Exception("Error opening Slides YAML file at indexes/slides_layout.yaml")

class SessionManagerMiddleware(Middleware):
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def on_message(self, context: MiddlewareContext, call_next):

        try:
            api_key = os.environ["API_KEY"]
        except KeyError:
            raise ValueError("API_KEY not found in environment. Check your .env file location and content.")

        headers = get_http_headers()
        client_api_key = headers.get("authorization")

        if not client_api_key:
            raise InvalidSignature("No authorization header provided for new session.")

        if client_api_key != api_key:
            raise InvalidSignature('Incorrect authorization credentials for new session.')

        return await call_next(context)


app = FastMCP(
    name="powerpoint-mcp-server",
    version="1.0.0",
    log_level="INFO",
)

session_manager = SessionManager(slide_layouts_metadata)
app.add_middleware(SessionManagerMiddleware(session_manager))

register_presentation_tools(app, session_manager)
register_slide_tools(app, session_manager)
register_text_tools(app, session_manager)
register_chart_tools(app, session_manager)
register_table_tools(app, session_manager)


@app.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


