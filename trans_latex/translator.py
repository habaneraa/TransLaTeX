
import re
from pathlib import Path
import aiofiles

from trans_latex.tex_source import LatexSourcesLoader
from trans_latex.splitter import LatexSourceSplitter
from trans_latex.chat_prompt import ChatPromptTemplate
from trans_latex.llm import LLMServiceConfig, async_chat_completion, count_tokens


class LatexProjectTranslator:
    triple_backticks_pattern = r'```(.+?)```'

    def __init__(self,
                 source: LatexSourcesLoader,
                 template: ChatPromptTemplate,
                 api_config: LLMServiceConfig,
                 chunk_size: int,
                 ) -> None:
        self.source = source
        self.template = template
        self.api_config = api_config
        self.splitter = LatexSourceSplitter(chunk_size=chunk_size, length_function=lambda t: count_tokens(text=t))
        self.translation_responses = None
        self.translated_chunks = None
        self.update_ongoing_file_cb = None
        self.complete_chunk_cb = None
    
    async def translate(self, text: str) -> str:
        text_chunks = self.splitter.split_text(text)
        translated_chunks = []
        for chunk in text_chunks:
            response = await async_chat_completion(
                self.api_config,
                self.template.create_messages(chunk)
            )
            self.translated_chunks += 1
            if self.complete_chunk_cb:
                self.complete_chunk_cb()
            self.translation_responses.append(response)
            translated_txt = response.choices[0].message.content
            match = re.search(self.triple_backticks_pattern, translated_txt, re.DOTALL)
            if match:
                translated_chunks.append(match.group(1).replace('```', ''))
            else:
                translated_chunks.append(translated_txt.replace('```', ''))
        return ''.join(translated_chunks)
    
    def estimate_tokens_cost(self, text: str) -> tuple[int, int]:
        text_chunks = self.splitter.split_text(text)
        result_tokens = 0
        for chunk in text_chunks:
            messages = self.template.create_messages(chunk)
            message_tokens = count_tokens(messages)
            result_tokens += message_tokens
        translation_tokens = count_tokens(text)
        result_tokens += translation_tokens
        return len(text_chunks), result_tokens
    
    def estimate_total_work(self) -> tuple[int, int]:
        document_nodes = None
        for node in self.source.sources[self.source.main_source]:
            document_node = LatexSourcesLoader.find_env_node(node, 'document')
            if document_node:
                document_nodes = document_node.nodelist
        
        all_tex_sources = [self.source.get_text_from_nodes(document_nodes)]
        for source in self.source.sources.keys():
            if source == self.source.main_source:
                continue
            txt = self.source.get_text_from_nodes(self.source.sources[source])
            all_tex_sources.append(txt)

        total_chunks, total_tokens = 0, 0
        for text in all_tex_sources:
            n_chunks, n_tokens = self.estimate_tokens_cost(text)
            total_chunks += n_chunks
            total_tokens += n_tokens
        return total_chunks, total_tokens
        
    async def translate_project(self, to_dir: Path) -> None:
        # prepare counters
        self.translation_responses = []
        self.translated_chunks = 0

        # first translate latex text within \begin{document} \end{document}
        document_nodes = None
        text_before_document_env, text_after_document_env = '', '\n\\end{document}'
        if self.update_ongoing_file_cb:
            self.update_ongoing_file_cb(self.source.main_source)
        for node in self.source.sources[self.source.main_source]:
            document_node = LatexSourcesLoader.find_env_node(node, 'document')
            if document_node:
                document_nodes = document_node.nodelist
                continue
            if document_nodes is None:
                text_before_document_env += node.latex_verbatim()
            else:
                text_after_document_env += node.latex_verbatim()
        text_before_document_env += '\n\\begin{document}\n'

        txt = self.source.get_text_from_nodes(document_nodes)
        translated_txt = await self.translate(txt)
        main_full_text = text_before_document_env + translated_txt + text_after_document_env

        async with aiofiles.open(
            to_dir / f'translated_main.tex', 'w', encoding='utf-8'
            ) as f:
            await f.write(main_full_text)

        # then translate every referenced tex file
        for source in self.source.sources.keys():
            if source == self.source.main_source:
                continue
            if self.update_ongoing_file_cb:
                self.update_ongoing_file_cb(source)
            txt = self.source.get_text_from_nodes(self.source.sources[source])
            translated_txt = await self.translate(txt)
            
            async with aiofiles.open(to_dir / source, 'w', encoding='utf-8') as f:
                await f.write(translated_txt)
        
        return
    
    def get_total_usage(self) -> tuple[int, int] | None:
        if self.translation_responses is None:
            return None
        
        prompt_tokens, completion_tokens = 0, 0
        for response in self.translation_responses:
            try:
                prompt_tokens += response['usage']['prompt_tokens']
                completion_tokens += response['usage']['completion_tokens']
            except KeyError as e:
                continue
        return prompt_tokens, completion_tokens
