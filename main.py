import os
import getpass
from openai import OpenAI

# Load API key
os.environ["OPENAI_API_KEY"] = getpass.getpass("OPENAI_API_KEY")
