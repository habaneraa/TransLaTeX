
from dataclasses import dataclass, asdict
import litellm


litellm.register_model({
    "deepseek-chat": {
        "max_tokens": 16_000, 
        "input_cost_per_token": 0.0, 
        "output_cost_per_token": 0.0, 
        "litellm_provider": "openai", 
        "mode": "chat"
    },
})


@dataclass
class LLMServiceConfig:
    api_base: str = 'https://api.openai.com/v1'
    api_key: str = ''
    model: str = 'gpt-3.5-turbo'
    temperature: float = 0.1


def chat_completion(llm_config: LLMServiceConfig, messages: list[dict[str, str]]):
    response = litellm.completion(
        messages=messages,
        stream=False,
        **asdict(llm_config)
    )
    completion_cost = litellm.completion_cost(response)
    return response, completion_cost


async def async_chat_completion(llm_config: LLMServiceConfig, messages: list[dict[str, str]]):
    response = await litellm.acompletion(
        messages=messages,
        stream=False,
        **asdict(llm_config),
        # mock_response="It's simple to use and easy to get started"
    )
    return response



"""
{
  'choices': [
    {
      'finish_reason': str,     # String: 'stop'
      'index': int,             # Integer: 0
      'message': {              # Dictionary [str, str]
        'role': str,            # String: 'assistant'
        'content': str          # String: "default message"
      }
    }
  ],
  'created': str,               # String: None
  'model': str,                 # String: None
  'usage': {                    # Dictionary [str, int]
    'prompt_tokens': int,       # Integer
    'completion_tokens': int,   # Integer
    'total_tokens': int         # Integer
  }
}
"""


async def check_valid_key(llm_config: LLMServiceConfig):
    """    Checks if a given API key is valid for a specific model    """
    try:
        response = await litellm.acompletion(
            messages=[{"role": "user", "content": "Hey, how's it going?"}],
            stream=False,
            max_tokens=5,
            **asdict(llm_config)
        )
        return True
    except litellm.AuthenticationError as e:
        return False
    except Exception as e:
        return False


def count_tokens(text: str | None = None, messages: list[dict[str, str]] | None = None) -> int:
    ret = 0
    if text:
        ret += litellm.token_counter("", text=text)
    if messages:
        ret += litellm.token_counter("", messages=messages)
    return ret
