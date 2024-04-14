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


class ValidTemperature(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            t = float(value)
        except ValueError as e:
            return self.failure()
        if 0.0 <= t <= 1.0:
            return self.success()
        else:
            return self.failure()
