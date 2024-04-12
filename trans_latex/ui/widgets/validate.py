from pathlib import Path
from textual.validation import ValidationResult, Validator


class ValidDirPath(Validator):
    def validate(self, value: str) -> ValidationResult:
        # empty field
        if value == '':
            return self.failure()
        p = Path(value)
        if '~' in str(p):
            p = p.expanduser()
        if p.exists() and p.is_dir():
            return self.success()
        else:
            return self.failure()
