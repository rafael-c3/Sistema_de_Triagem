# triagem/validators.py
import re
from django.core.exceptions import ValidationError

class RequiresUppercaseValidator:
    """Validador que exige pelo menos uma letra maiúscula."""
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "A senha deve conter pelo menos uma letra maiúscula.",
                code='password_no_upper',
            )

    def get_help_text(self):
        return "Sua senha deve conter pelo menos uma letra maiúscula."


class RequiresNumberValidator:
    """Validador que exige pelo menos um número."""
    def validate(self, password, user=None):
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                "A senha deve conter pelo menos um número.",
                code='password_no_number',
            )

    def get_help_text(self):
        return "Sua senha deve conter pelo menos um número."