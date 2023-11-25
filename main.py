"""
This is the main script of the application doc string.
"""
import argparse
import logging
from openai import OpenAI

from api.openai_functions.gpt_chat import chat_function
from voice.elm327 import handle_voice_commands_elm327
from voice.voice_recognition import handle_common_voice_commands
from audio.audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, EMAIL_PROVIDER

import api.microsoft_functions.graph_api as graph_api
import api.microsoft_functions.ms_authserver as ms_authserver
import api.google_functions.google_api as google_api

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    filemode="a",  # Append mode (use 'w' for overwrite mode)
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


email_provider = EMAIL_PROVIDER


client = OpenAI(api_key=OPENAI_API_KEY)

# initialize_audio()

try:
    response_text = chat_function("Hello")
    logging.info(response_text)
    initialize_audio()
    tts_output(response_text)
except ValueError as e:
    logging.exception(f"Failed to get response from chat_function or output it.{e}")

parser = argparse.ArgumentParser(description="Choose the device type")
parser.add_argument(
    "--device",
    choices=["none", "elm327"],
    default="none",
    help="Select the device type (default: none)",
)

args = parser.parse_args()

SELECTED_API = None

if email_provider == "365":
    authorization_code = ms_authserver.get_auth_code()
    graph_api.perform_graph_api_request(authorization_code)
    SELECTED_API = graph_api
elif email_provider == "Google":
    SELECTED_API = google_api

try:
    # Check the device type from command line arguments
    if args.device == "elm327":
        # If the device type is "elm327", handle voice commands for ELM327
        handle_voice_commands_elm327(graph_api.user_object_id)
    else:
        if email_provider == "365":
            handle_common_voice_commands(
                args,
                graph_api.user_object_id,
                email_provider
            )
        elif email_provider == "Google":
            handle_common_voice_commands(args, email_provider=email_provider)
except ValueError as e:
    logging.exception(f"Error occurred while handling voice commands: {e}")
