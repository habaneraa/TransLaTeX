
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

def tiktoken_length(text: str) -> int:
    return len(encoding.encode(text))


def count_message_tokens(messages) -> int:
    """Returns the number of tokens used by a list of messages."""
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += tiktoken_length(value)
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens
