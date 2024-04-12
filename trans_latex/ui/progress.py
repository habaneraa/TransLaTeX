
from pathlib import Path
from typing import Iterable
import subprocess

from textual.widget import Widget
from textual.widgets import ProgressBar, Label, Button
from textual.screen import Screen
from textual.containers import Middle, Vertical
from textual.reactive import reactive
from textual.worker import Worker, WorkerState

from trans_latex.ui.task import current_task
from trans_latex.ui.utils import copy_files
from trans_latex.translator import LatexProjectTranslator
from trans_latex.ui.localization.string_res import resources


class ProgressScreen(Screen):

    translator: LatexProjectTranslator | None = None
    status_text: reactive[str] = reactive('Starting...')
    completed: bool = False

    def compose(self) -> Iterable[Widget]:
        self.log.error('COMPOSING!', self.completed)
        if self.completed:
            yield Label(resources.get(r'completed_1'), classes='center-label')
            yield Label(resources.get(r'completed_2'), classes='center-label')
            with Middle():
                yield Button(resources.get(r'open_folder'), variant='success')
        else:
            yield Label(resources.get(r'top_warning'), classes='center-label')
            with Middle():
                with Vertical(id='progressbar-container'):
                    yield ProgressBar(id='progress-bar', total=current_task.num_chunks)
            yield Label('...', id='status-text', classes='center-label')
    
    def on_mount(self) -> None:
        self.run_worker(self.translation_task, name='worker')
        ...
    
    async def mock_progress(self) -> None:
        for i in range(10):
            self.query_one(ProgressBar).advance(1.0)
    
    def watch_status_text(self, old_str: str, new_str: str) -> None:
        self.query_one('#status-text').styles.display = 'block'
        self.query_one('#status-text').update(new_str)

    async def translation_task(self) -> None:
        self.status_text = f'Preparing new folder {current_task.target_dir} ...'
        current_task.target_dir.mkdir(parents=True, exist_ok=True)
        await copy_files(Path(current_task.tex_sources.project_dir), Path(current_task.target_dir))

        self.translator = LatexProjectTranslator(
            current_task.tex_sources,
            current_task.prompt_template,
            current_task.llm_service_config,
            current_task.chunk_size
        )
        
        def complete_chunk() -> None:
            self.query_one(ProgressBar).advance(1.0)
        
        def update_ongoing_file(name: str) -> None:
            self.log.info(f'going {name}')
            self.status_text = f'Translating: {name}'
        self.translator.complete_chunk_cb = complete_chunk
        self.translator.update_ongoing_file_cb = update_ongoing_file

        await self.translator.translate_project(current_task.target_dir)

    async def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.is_finished and event.worker.state == WorkerState.SUCCESS:
            self.completed = True
            await self.recompose()
    
    def on_button_pressed(self, event):
        if current_task.target_dir and current_task.target_dir.exists():
            subprocess.run(["explorer.exe", current_task.target_dir])
        event.stop()
