
from textual.app import ComposeResult
from textual.widget import Widget
from textual.screen import Screen
from textual.containers import VerticalScroll
from textual.widgets import Button, ContentSwitcher, Label, Header, Footer


from trans_latex.ui.localization import resources
from trans_latex.ui.widgets import config_pages
from trans_latex.ui.task import current_task


class ConfigScreen(Screen):
    """Switch among different configuration pages"""
    
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="sidebar"):
            yield Label(resources.get(r'config_steps'), id='sidebar-title')
            yield Button(resources.get(r'step_1_button').ljust(24), id="step-1", classes="side-button", disabled=True)
            yield Button(resources.get(r'step_2_button').ljust(24), id="step-2", classes="side-button", disabled=True)
            yield Button(resources.get(r'step_3_button').ljust(24), id="step-3", classes="side-button", disabled=True)
            yield Button(resources.get(r'step_4_button').ljust(24), id="step-4", classes="side-button", disabled=True)

        with ContentSwitcher(initial='step-1-page'):
            yield config_pages.LatexProjectDir(id="step-1-page", classes='config-page')
            yield config_pages.APIKey(id="step-2-page", classes='config-page')
            yield config_pages.TranslationOptions(id="step-3-page", classes='config-page')
            yield config_pages.CostEstimation(id="step-4-page", classes='config-page')
        yield Header()
        yield Footer()
        
    def on_config_page_finished(self, event: config_pages.ConfigPage.Finished) -> None:
        side_button_id = 'step-' + event.id[5]
        self.query_one('#' + f'{side_button_id}').add_class('side-button-finished')

        if int(event.id[5]) in (1, 2, 3,):
            next_button_id = 'step-' + str(int(event.id[5]) + 1)
            next_button = self.query_one('#' + f'{next_button_id}')
            next_button.disabled = False
            next_button.press()
        elif event.id == 'step-4-page':
            self.dismiss(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id.startswith('step-'):
            # Switch the page
            
            # change button styles
            side_button_id = 'step-' + self.query_one(ContentSwitcher).current[5]
            self.query_one('#' + f'{side_button_id}').remove_class('side-button-current')
            event.button.add_class('side-button-current')

            self.query_one(ContentSwitcher).current = f'{event.button.id}-page'

            self.update_current_task()
            if event.button.id == 'step-4':
                self.query_one(config_pages.CostEstimation).run_estimation()
            
            event.stop()
        
        if event.button.id == 'start-task-button':
            event.stop()
    
    def update_current_task(self) -> None:
        current_task.prompt_template    = self.query_one(config_pages.TranslationOptions).create_prompt_template()
        current_task.tex_sources        = self.query_one(config_pages.LatexProjectDir).project_loader
        current_task.llm_service_config = self.query_one(config_pages.APIKey).get_api_service_config()
        current_task.chunk_size         = int(self.query_one('#chunk-size-input').value)
        current_task.num_chunks         = self.query_one(config_pages.CostEstimation).total_chunks

    def on_mount(self) -> None:
        self.query_one('#step-1').disabled = False
        self.query_one('#step-1').press()
