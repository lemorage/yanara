from letta import EmbeddingConfig, LLMConfig, client, create_client
from letta.schemas.llm_config import LLMConfig

from yanara.config import get_openai_api_key
from yanara.util.decorators import entry

client = create_client()

model_settings = {
    "openai_api_key": get_openai_api_key(),
}

# set automatic defaults for LLM/embedding config
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))
client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="text-embedding-ada-002"))


@entry
def main():
    pass
