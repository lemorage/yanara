from letta import EmbeddingConfig, LLMConfig, create_client

from yanara.util.config import get_openai_api_key

# Create a Letta client
client = create_client()

model_settings = {
    "openai_api_key": get_openai_api_key(),
}

# set automatic defaults for LLM/embedding config
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))
client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="letta"))
