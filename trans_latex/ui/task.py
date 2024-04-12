
from pathlib import Path

from trans_latex.tex_source import LatexSourcesLoader
from trans_latex.chat_prompt import ChatPromptTemplate
from trans_latex.llm import LLMServiceConfig, check_valid_key


class TranslationTask:

    prompt_template: ChatPromptTemplate | None = None
    tex_sources: LatexSourcesLoader | None = None
    llm_service_config: LLMServiceConfig | None = None
    chunk_size: int | None = None
    num_chunks: int | None = None
    target_dir: Path | None = None

    async def is_ready(self) -> None:
        if (
            not self.prompt_template or
            not self.tex_sources or
            not self.tex_sources.sources or
            not self.llm_service_config or
            not isinstance(self.chunk_size, int) or
            not self.num_chunks
        ):
            return False
        if await check_valid_key(self.llm_service_config):
            return True
        else:
            return False


# singleton~ 🤪
current_task: TranslationTask = TranslationTask()
