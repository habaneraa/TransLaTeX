
import backoff
import openai
import time
import logging

from .tokenizer import count_message_tokens


# api logger
logger = logging.getLogger('openai-api')
# api request config
model_name = 'gpt-3.5-turbo'
token_limit = 4096
temperature = 0.0
prompt_token_limit = 1500
last_request_timestamp = 0
rate_limit_interval = 20.0


def create_messages(user_prompt, system_prompt):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


@backoff.on_exception(
    backoff.constant, 
    openai.error.OpenAIError, 
    max_tries=5,
    logger=logger,
    interval=rate_limit_interval,
    )
def chat_completion(user_prompt, system_prompt):
    messages = create_messages(user_prompt, system_prompt)
    if count_message_tokens(messages) > token_limit:
        raise ValueError('The prompt is too long.')
    
    # throttle the api requests
    global last_request_timestamp
    if time.time() - last_request_timestamp < rate_limit_interval:
        time.sleep(rate_limit_interval)
    last_request_timestamp = time.time()

    response = openai.ChatCompletion.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
    )
    return response['choices'][0]['message']['content'], response['usage']['total_tokens']
