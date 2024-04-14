
from pathlib import Path
import tarfile

from textual.app import ComposeResult
from textual.widget import Widget
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Markdown, Input, TextArea, Collapsible, Label
from textual.message import Message
from textual.reactive import reactive, Reactive
from textual.worker import Worker, WorkerState

from trans_latex.ui.localization import resources
from trans_latex.ui.widgets.labeled_input import InputWithLabel
from trans_latex.ui.utils import adownload
from trans_latex.ui.widgets.validate import ValidDirPath, ValidTemperature
from trans_latex.ui.task import current_task

from trans_latex.llm import LLMServiceConfig, check_valid_key
from trans_latex.chat_prompt import ChatPromptTemplate
from trans_latex.tex_source import LatexSourcesLoader
from trans_latex.translator import LatexProjectTranslator


class ConfigPage(Widget):

    class Finished(Message):
        def __init__(self, id: str) -> None:
            self.id = id
            super().__init__()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'config-page-confirm':
            self.post_message(self.Finished(self.id))
            event.stop()


class LatexProjectDir(ConfigPage):

    project_loader: LatexSourcesLoader | None = None
    is_valid_project: reactive[bool] = reactive(False)
    status_text: Reactive[str] = reactive('')

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown(resources.get(r'p1_text_1'), classes='emph-text')

            yield Markdown(resources.get(r'p1_text_2'))
            with Horizontal(classes='input-and-submit'):
                yield Input(
                    placeholder=resources.get(r'p1_text_3'),
                    id='arxiv-input'
                    )
                yield Button('OK', id='button-download', classes='button-submit')
            
            yield Markdown(resources.get(r'p1_text_4'))
            with Horizontal(classes='input-and-submit'):
                yield Input(
                    placeholder=resources.get(r'p1_text_5'),
                    validators=[ValidDirPath()],
                    valid_empty=False,
                    id='path-input'
                    )
                yield Button('OK', id='button-checkdir', classes='button-submit')

            yield Markdown('', id='status-text')
            yield Button(
                resources.get(r'confirm'), 
                variant='primary', 
                id='config-page-confirm', 
                disabled=True
            )
    
    def on_mount(self) -> None:
        pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)

        if event.button.id == 'button-download':
            arxiv_id = self.query_one('#arxiv-input').value.strip()
            self.status_text = f'Fetching arXiv {arxiv_id}...'
            self.run_worker(
                self.download_and_parse_latex_project(arxiv_id),
                group='sources_loading',
                exclusive=True
            )

        if event.button.id == 'button-checkdir':
            target_path = Path( self.query_one('#path-input').value )
            if '~' in str(target_path):
                target_path = target_path.expanduser()
            self.status_text = f'Parsing LaTeX project at {target_path}...'
            self.run_worker(
                self.parse_latex_project(target_path),
                group='sources_loading',
                exclusive=True
            )
        event.stop()
    
    async def download_and_parse_latex_project(self, arxiv_identifier: str) -> None:
        url = f'https://arxiv.org/src/{arxiv_identifier}'
        save_dir = Path(f'~/.cache/translatex/{arxiv_identifier}').expanduser()
        save_dir.mkdir(parents=True, exist_ok=True)
        tar_path = save_dir / f'{arxiv_identifier}.tar.gz'
        await adownload(url, tar_path)
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(path=save_dir)
        await self.parse_latex_project(save_dir)
    
    async def parse_latex_project(self, project_dir: Path) -> None:
        self.project_loader = LatexSourcesLoader(project_dir)
        ret = await self.project_loader.load_sources()
        if ret:
            self.is_valid_project = True
            self.status_text = f'Project loaded successfully! Main source found: {self.project_loader.main_source}'
        else:
            self.status_text = f'Failed.'

    def watch_status_text(self, old_str: str, new_str: str) -> None:
        if new_str == '':
            self.query_one('#status-text').styles.display = 'none'
        else:
            self.query_one('#status-text').styles.display = 'block'
        self.query_one('#status-text').update(new_str)
    
    def watch_is_valid_project(self, old_bool: bool, new_bool: bool) -> None:
        if old_bool != new_bool:
            self.query_one('#config-page-confirm').disabled = not new_bool


class APIKey(ConfigPage):

    llm_service_config: LLMServiceConfig | None = None

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown(resources.get(r'p2_text_1'), classes='emph-text')

            yield InputWithLabel(
                'API base',
                placeholder='https://api.openai.com/v1',
                id='api-base-input',
            )
            yield InputWithLabel(
                'API key',
                placeholder='sk-xxxxxxxxxxxxxxxxxxx',
                id='api-key-input',
            )
            yield InputWithLabel(
                'Model',
                placeholder='gpt-3.5-turbo',
                id='model-input',
            )
            yield InputWithLabel(
                'Temperature',
                validators=[ValidTemperature()],
                placeholder='0.2',
                id='temperature-input',
            )

            self.test_button = Button(
                'Click to test the API', 
                variant='default', 
                id='test-api-button'
            )
            yield self.test_button

            yield Button(
                resources.get(r'confirm'), 
                variant='primary', 
                id='config-page-confirm', 
                disabled=True
            )
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'test-api-button':
            event.button.loading = True
            worker = self.run_worker(
                check_valid_key(self.get_api_service_config()),
                name='test_api'
            )
            event.stop()
        super().on_button_pressed(event)
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == 'test_api':
            if event.worker.is_finished and event.worker.state == WorkerState.SUCCESS:
                self.test_button.loading = False
                if event.worker.result == True:
                    self.test_button.label = 'API request successful!'
                    self.test_button.variant = 'success'
                    self.test_button.disabled = True
                else:
                    self.test_button.label = 'API request failed, please check the network and key.'
                    self.test_button.variant = 'warning'
                    self.test_button.disabled = True
            else:
                self.test_button.loading = False
            event.stop()
    
    def on_input_changed(self, event: Input.Changed):
        self.test_button.variant = 'default'
        self.test_button.label = 'Click to test the API'
        if result := self.get_api_service_config():
            self.llm_service_config = result
            self.test_button.disabled = False
            self.query_one('#config-page-confirm').disabled = False
        else:
            self.test_button.disabled = True
            self.query_one('#config-page-confirm').disabled = True
        event.stop()
    
    def get_temperature(self) -> float:
        try:
            return float(self.query_one('#temperature-input').value)
        except ValueError as e:
            return 0.1
    
    def get_api_service_config(self) -> LLMServiceConfig | None:
        data = LLMServiceConfig(
            api_base=self.query_one('#api-base-input').value,
            api_key=self.query_one('#api-key-input').value,
            model=self.query_one('#model-input').value,
            temperature=self.get_temperature(),
        )
        if data.api_key:
            return data
        else:
            return None


class TranslationOptions(ConfigPage):

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown(resources.get(r'p3_text_1'), classes='emph-text')

            yield InputWithLabel(
                'Source Language',
                value='English',
                id='src-lang-input',
            )
            yield InputWithLabel(
                'Target Language',
                value='Chinese',
                id='tgt-lang-input',
            )
            yield InputWithLabel(
                'Token Chunk Size',
                value='1000',
                id='chunk-size-input',
                type='number'
            )

            with Collapsible(title=resources.get(r'p3_collapse_title'), classes='collapse_prompt'):
                yield Markdown(resources.get(r'p3_text_3'))

                self.prompt_text_area = TextArea(
                    text="",
                    soft_wrap=True,
                    tab_behavior='indent',
                )
                self.prompt_text_area.border_title = resources.get(r'p3_text_2')
                yield self.prompt_text_area
            
            with Collapsible(title=resources.get(r'p3_preview_title'), classes='collapse_prompt'):
                yield Markdown('...', id='preview_prompt_md')

            yield Button(resources.get(r'confirm'), variant='primary', id='config-page-confirm')
    
    def on_mount(self) -> None:
        self.query_one('#chunk-size-input').tooltip = resources.get(r'chunk_size_tip')
        self.update_preview_md()
    
    def on_input_changed(self, event: Input.Changed):
        self.update_preview_md()
        event.stop()
    
    def update_preview_md(self) -> None:
        template = self.create_prompt_template()
        msg = template.create_messages("<TeX source to be translated>")
        md_text = f"### System:\n\n{msg[0]['content']}\n\n### User:\n\n{msg[1]['content']}"
        self.query_one('#preview_prompt_md').update(md_text)
    
    def create_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate(
            src_lang=self.query_one('#src-lang-input').value,
            tgt_lang=self.query_one('#tgt-lang-input').value,
            extra_prompt=self.prompt_text_area.text,
        )


class CostEstimation(ConfigPage):

    total_chunks: int | None = reactive(None)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown(resources.get(r'p4_text_1'), classes='emph-text')

            self.results_md = Markdown('...')
            yield self.results_md

            with Collapsible(title=resources.get(r'p4_collapse_title')):
                yield Label(resources.get(r'p4_dir_input'))
                yield Input(
                    value='./translated/',
                    id='target-dir-input'
                )

            yield Button(
                resources.get(r'p4_start_button_0'),
                variant='default',
                id='config-page-confirm',
                disabled=True
            )
    
    def on_mount(self) -> None:
        self.results_md.loading = True

    def run_estimation(self) -> None:
        translator = LatexProjectTranslator(
            current_task.tex_sources,
            current_task.prompt_template,
            current_task.llm_service_config,
            current_task.chunk_size
        )
        if not translator.source or not translator.source.sources:
            self.notify("Empty source.", severity='error')
            return
        x, y = translator.estimate_total_work()

        current_task.num_chunks = x

        self.results_md.update(resources.get(r'p4_estimation_result').format(x=x, y=y))
        self.results_md.loading = False

        self.run_worker(current_task.is_ready(), exclusive=True, name='check_ready')
    
    def on_input_changed(self, event: Input.Changed) -> None:
        current_task.target_dir = Path(event.input.value)
        
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != 'check_ready':
            return
        if event.worker.is_finished and event.worker.state == WorkerState.SUCCESS:
            button: Button = self.query_one('#config-page-confirm')
            if event.worker.result:
                button.variant = 'success'
                button.disabled = False
                button.label = resources.get(r'p4_start_button_ok')
            else:
                button.variant = 'error'
                button.label = resources.get(r'p4_start_button_failed')
            event.stop()
