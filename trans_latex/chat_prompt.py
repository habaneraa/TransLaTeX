
latex_translation_instructions = """
Translate academic research paper from **{src_lang}** to **{tgt_lang}**. 

Instructions:
- The inputs are LaTeX sources. Your translation should also be in LaTeX format.
- You provide a high-quality, accurate translation of the paper while preserving the original meaning.
- Translate only plain texts in the sources. Do not alter any LaTeX macros or mathematical expressions.
- Both the texts to be translated and your translations are enclosed within triple backticks.
- Ensure your output can be parsed successfully by LaTeX compilers.

""".strip()

default_system_prompt = "You are a helpful assistant, proficient in multiple languages."


class ChatPromptTemplate:
    """Chat prompt template for latex translation."""

    def __init__(self, 
                 src_lang: str = 'English',
                 tgt_lang: str = 'Chinese',
                 extra_prompt: str | None = None,
                 system_prompt: str = default_system_prompt,
                 instruction: str = latex_translation_instructions,
                 ) -> None:
        self.system_prompt = system_prompt

        extra_prompt = extra_prompt.strip() if extra_prompt else ''
        instruction_prompt = instruction.format(src_lang=src_lang, tgt_lang=tgt_lang)

        self.user_prompt = instruction_prompt + '\n\n' + extra_prompt + '\n\n```\n{text_input}\n```'

    def create_messages(self, text_input: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt.format(text_input=text_input)},
        ]


if __name__ == '__main__':
    template = ChatPromptTemplate()
    msgs = template.create_messages('In particular, we focus on four major aspects of LLMs, namely pre-training, adaptation tuning, utilization, and capacity evaluation. Besides, we also summarize the available resources for developing LLMs and discuss the remaining issues for future directions.')
    from llm import chat_completion, LLMServiceConfig
    response, cost = chat_completion(LLMServiceConfig(), msgs)
    print(response)
    print(cost)
