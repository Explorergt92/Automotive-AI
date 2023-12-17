"""
This is the main script of the application doc string.
"""
import sys
import os
import argparse
import logging
from openai import OpenAI
from dotenv import load_dotenv

from api.openai_functions.gpt_chat import chat_gpt
from voice.elm327 import handle_voice_commands_elm327
from voice.voice_recognition import handle_common_voice_commands
from audio.audio_output import tts_output, initialize_audio
from config import OPENAI_API_KEY, EMAIL_PROVIDER

import api.microsoft_functions.graph_api as graph_api
import api.microsoft_functions.ms_authserver as ms_authserver
import api.google_functions.google_api as google_api


logging.basicConfig(
    filename="app.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Set the logging level for comtypes to WARNING or higher to reduce verbosity
logging.getLogger('comtypes').setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

email_provider = EMAIL_PROVIDER


client = OpenAI(api_key=OPENAI_API_KEY)

initialize_audio()

try:
    response_text = chat_gpt("Hello")
    logging.debug(response_text)
    tts_output(response_text)
except SystemExit:
    logging.exception("All attempts to get response failed. Restarting app.")
    os.execv(sys.executable, ['python'] + sys.argv)  # Restart the application

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
    logging.exception("Error occurred while handling voice commands: %s", e)
    tts_output("Sorry, I could not understand you.")
