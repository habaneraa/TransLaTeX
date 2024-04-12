
import os
from pathlib import Path
import aiofiles
from pylatexenc.latexwalker import (
    LatexWalker,
    LatexNode,
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
)


class LatexSourcesLoader:

    def __init__(self, project_dir: Path, main: str | None = None) -> None:
        self.project_dir: Path = project_dir
        self.main_source: str | None = main
        self.sources: dict[str, list[LatexNode]] = {}
    
    @staticmethod
    async def parse_latex_file(file_path) -> list[LatexNode]:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        walker = LatexWalker(content)
        node_list, _, _ = walker.get_latex_nodes()
        return node_list
    
    @staticmethod
    def get_text_from_nodes(node_list: list[LatexNode]) -> str:
        texts = []
        for n in node_list:
            if n is None: continue
            texts.append(n.latex_verbatim())
        
        return ''.join(texts)
    
    @staticmethod
    async def contains_environment(path, environment: str) -> bool:
        node_list = await LatexSourcesLoader.parse_latex_file(path)
        for node in node_list:
            if LatexSourcesLoader.find_env_node(node, environment):
                    return True
        return False
    
    @staticmethod
    def find_env_node(cur_node: LatexNode | None, environment: str) -> LatexEnvironmentNode | None:
        if cur_node is None or \
           cur_node.nodeType() not in [LatexEnvironmentNode, LatexGroupNode, LatexMacroNode]: 
                return None
        if isinstance(cur_node, LatexEnvironmentNode) and \
           cur_node.envname == environment:
                return cur_node

        node_list, env_node = None, None
        if isinstance(cur_node, LatexMacroNode):
            if cur_node.nodeargd is None: 
                return None
            node_list = cur_node.nodeargd.argnlist
        else:
            node_list = cur_node.nodelist

        for node in node_list:
            if node is None: continue
            env_node = LatexSourcesLoader.find_env_node(node, environment)
            if env_node: break
        
        return env_node
    
    @staticmethod
    def find_macro_nodes(nodes: list[LatexNode], name: str) -> list[LatexMacroNode]:
        results = []
        for node in nodes:
            if isinstance(node, LatexMacroNode):
                if node.macroname == name:
                    results.append(node)
        return results
    
    async def find_document_environment(self) -> None:
        print(f'No main source file specified. Looking for "document" latex environment in {self.project_dir} ...')
        for n in os.listdir(self.project_dir):
            file_path = os.path.join(self.project_dir, n)
            if os.path.isfile(file_path) and file_path.split('.')[-1] == 'tex':
                if await self.contains_environment(file_path, 'document'):
                    self.main_source = n

    async def _load_includes(self, node_list: list[LatexNode]) -> None:
        """recursively load sources"""
        input_nodes = self.find_macro_nodes(node_list, 'input')
        for inode in input_nodes:
            # print(inode.latex_verbatim())
            # input macro -> first arg -> first node -> text
            filename = inode.nodeargd.argnlist[0].nodelist[0].chars
            if not filename.endswith('.tex'):
                filename = filename + '.tex'
            filepath = os.path.join(self.project_dir, filename)
            assert os.path.exists(filepath)
            if self.sources.get(filename) is None:
                new_nodes = await self.parse_latex_file(filepath)
                self.sources[filename] = new_nodes
                await self._load_includes(new_nodes)
    
    async def load_sources(self) -> dict[str, list[LatexNode]]:
        if self.main_source is None:
            await self.find_document_environment()
        if self.main_source is None or not os.path.exists(os.path.join(self.project_dir, self.main_source)):
            # raise ValueError('Main document source is not found.')
            return self.sources
        
        nodes_main = await self.parse_latex_file(os.path.join(self.project_dir, self.main_source))
        self.sources[self.main_source] = nodes_main

        document_env_node = None
        for node in nodes_main:
            document_env_node = LatexSourcesLoader.find_env_node(node, 'document')
            if document_env_node:
                break
        
        document_nodes: list[LatexNode] = document_env_node.nodelist
        await self._load_includes(document_nodes)
        return self.sources
