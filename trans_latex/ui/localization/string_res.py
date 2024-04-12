__all__ = ['resources']

import yaml
import pathlib


class StringResources:

    resource_paths = {
        'en': pathlib.Path(__file__).parent / 'en.yaml',
    }

    def __init__(self, locale: str = 'en') -> None:
        self.locale = locale
        self.resources = self.load_resources()
    
    def load_resources(self) -> dict[str, str]:
        with open(self.resource_paths[self.locale], 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)['string_values']
    
    def get(self, key: str) -> str:
        return self.resources[key]
    
    def switch_locale(self, locale: str) -> None:
        raise NotImplementedError()


resources = StringResources()
