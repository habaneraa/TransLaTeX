
import os
import re
import time

from pylatexenc.latexwalker import LatexEnvironmentNode

from .prompts import get_prompt, default_system
from .chat import chat_completion, create_messages
from .tokenizer import count_message_tokens, tiktoken_length
from .sources_loader import LatexSourcesLoader
from .splitter import LatexSourceSplitter


class LatexTranslator:
    pattern = r'\"\"\"(.+?)\"\"\"'

    def __init__(self, source_language, target_language, chunk_size) -> None:
        self.splitter = LatexSourceSplitter(chunk_size=chunk_size)
        self.source_language = source_language
        self.target_language = target_language
        self.source_loader = None

        self._tokens_cost = 0
        self.start_time = time.monotonic()
    
    def translate(self, text: str) -> str:
        text_chunks = self.splitter.split_text(text)
        translated_chunks = []
        for chunk in text_chunks:
            translated_txt, tokens = chat_completion(get_prompt(chunk, self.source_language, self.target_language), default_system)
            match = re.search(self.pattern, translated_txt, re.DOTALL)
            if match:
                translated_chunks.append(match.group(1).replace('"""', ''))
            else:
                translated_chunks.append(translated_txt.replace('"""', ''))
            print(f'translation chat cost tokens: {tokens} ')
            self._tokens_cost += tokens
        return ''.join(translated_chunks)
    
    def estimate_tokens_cost(self, text: str):
        text_chunks = self.splitter.split_text(text)
        result_tokens = 0
        for chunk in text_chunks:
            messages = create_messages(get_prompt(chunk, self.source_language, self.target_language), default_system)
            message_tokens = count_message_tokens(messages)
            result_tokens += message_tokens
        translation_tokens = tiktoken_length(text)
        result_tokens += translation_tokens
        return len(text_chunks), result_tokens
    
    def estimate_work(self, from_dir, to_dir, main_tex) -> None:
        if self.source_loader is None:
            self.source_loader = LatexSourcesLoader(from_dir, main_tex)
            self.source_loader.load_sources()

        total_chunks, total_tokens = 0, 0

        document_nodes = None
        for node in self.source_loader.sources[self.source_loader.main_source]:
            document_node = LatexSourcesLoader.find_env_node(node, 'document')
            if document_node:
                document_nodes = document_node.nodelist
        
        txt = self.source_loader.get_text_from_nodes(document_nodes)
        n_chunks, n_tokens = self.estimate_tokens_cost(txt)
        total_chunks += n_chunks
        total_tokens += n_tokens

        # then translate every referenced tex file
        for source in self.source_loader.sources.keys():
            if source == self.source_loader.main_source:
                continue
            txt = self.source_loader.get_text_from_nodes(self.source_loader.sources[source])
            n_chunks, n_tokens = self.estimate_tokens_cost(txt)
            total_chunks += n_chunks
            total_tokens += n_tokens
        
        print(f'Total text chunks: {total_chunks}')
        print(f'Total estimated tokens: {total_tokens}')
        user = input('Type "yes" to confirm: ')
        if user != 'yes':
            exit(1)

    
    def translate_project(self, from_dir, to_dir, main_tex) -> None:
        if self.source_loader is None:
            self.source_loader = LatexSourcesLoader(from_dir, main_tex)
            self.source_loader.load_sources()

        # first translate latex text within \begin{document} \end{document}
        document_nodes = None
        text_before_document_env, text_after_document_env = '', '\n\\end{document}'
        for node in self.source_loader.sources[self.source_loader.main_source]:
            document_node = LatexSourcesLoader.find_env_node(node, 'document')
            if document_node:
                document_nodes = document_node.nodelist
                continue
            if document_nodes is None:
                text_before_document_env += node.latex_verbatim()
            else:
                text_after_document_env += node.latex_verbatim()
        text_before_document_env += '\n\\begin{document}\n'

        txt = self.source_loader.get_text_from_nodes(document_nodes)
        translated_txt = self.translate(txt)
        main_full_text = text_before_document_env + translated_txt + text_after_document_env

        save_path = os.path.join(to_dir, self.source_loader.main_source)
        print(f'Translation of source file {self.source_loader.main_source} is completed. Saving to {save_path}')
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(main_full_text)

        # then translate every referenced tex file
        for source in self.source_loader.sources.keys():
            if source == self.source_loader.main_source:
                continue
            txt = self.source_loader.get_text_from_nodes(self.source_loader.sources[source])
            translated_txt = self.translate(txt)
            save_path = os.path.join(to_dir, source)
            print(f'Translation of source file {source} is completed. Saving to {save_path}')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(translated_txt)

    def show_cost(self) -> None:
        print('Time:', time.monotonic() - self.start_time)
        print('Total tokens:', self._tokens_cost)
        print('API usage:', self._tokens_cost * 0.002 / 1000, 'USD')

