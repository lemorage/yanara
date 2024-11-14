import os

from dotenv import find_dotenv, load_dotenv


def load_env():
    _ = load_dotenv(find_dotenv())


def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def get_lark_app_id_and_secret():
    load_env()
    lark_app_id = os.getenv("LARK_APP_ID")
    lark_app_secret = os.getenv("LARK_APP_SECRET")
    return lark_app_id, lark_app_secret
