
import os
from typing import List, Dict, Optional
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

    def __init__(self, project_dir=os.getcwd(), main=None) -> None:
        self.project_dir: str = project_dir
        self.main_source: str = main
        self.sources: Dict[str, List[LatexNode]] = {}

        if self.main_source is None:
            self.find_document_environment()
    
    @staticmethod
    def parse_latex_file(file_path) -> List[LatexNode]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        walker = LatexWalker(content)
        node_list, _, _ = walker.get_latex_nodes()
        return node_list
    
    @staticmethod
    def get_text_from_nodes(node_list: List[LatexNode]) -> str:
        texts = []
        for n in node_list:
            if n is None: continue
            texts.append(n.latex_verbatim())
        
        return ''.join(texts)
    
    @staticmethod
    def contains_environment(path, environment: str) -> bool:
        node_list = LatexSourcesLoader.parse_latex_file(path)
        for node in node_list:
            if LatexSourcesLoader.find_env_node(node, environment):
                    return True
        return False
    
    @staticmethod
    def find_env_node(cur_node, environment: str) -> Optional[LatexNode]:
        if cur_node is None or \
           cur_node.nodeType() not in [LatexEnvironmentNode, LatexGroupNode, LatexMacroNode]: 
                return None
        if cur_node.isNodeType(LatexEnvironmentNode) and \
           cur_node.envname == environment:
                return cur_node

        node_list, env_node = None, None
        if cur_node.isNodeType(LatexMacroNode):
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

    def find_document_environment(self) -> None:
        print(f'No main source file specified. Looking for "document" latex environment in {self.project_dir} ...')
        for n in os.listdir(self.project_dir):
            file_path = os.path.join(self.project_dir, n)
            if os.path.isfile(file_path) and file_path.split('.')[-1] == 'tex':
                if self.contains_environment(file_path, 'document'):
                    self.main_source = n
    
    @staticmethod
    def find_macro_nodes(nodes, name) -> List[LatexNode]:
        results = []
        for node in nodes:
            if node.isNodeType(LatexMacroNode):
                if node.macroname == name:
                    results.append(node)
        return results

    def _load_includes(self, node_list) -> None:
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
                new_nodes = self.parse_latex_file(filepath)
                self.sources[filename] = new_nodes
                self._load_includes(new_nodes)
    
    def load_sources(self):
        if self.main_source is None or not os.path.exists(os.path.join(self.project_dir, self.main_source)):
            raise ValueError('Main document source is not found.')
        nodes_main = self.parse_latex_file(os.path.join(self.project_dir, self.main_source))
        self.sources[self.main_source] = nodes_main

        document_env_node = None
        for node in nodes_main:
            document_env_node = LatexSourcesLoader.find_env_node(node, 'document')
            if document_env_node:
                break
        
        document_nodes: List[LatexNode] = document_env_node.nodelist
        self._load_includes(document_nodes)
        print('LaTeX source files detected:')
        for k in self.sources.keys():
            print(f'  - {k}')
