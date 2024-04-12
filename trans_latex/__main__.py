import sys
from trans_latex.app import TransLaTeXTUI


def run_tui_app():
    app = TransLaTeXTUI()
    app.run()
    sys.exit(app.return_code or 0)


if __name__ == "__main__":
    run_tui_app()
