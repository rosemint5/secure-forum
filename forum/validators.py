import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class StrongPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 12:
            raise ValidationError(_("Hasło musi mieć co najmniej 12 znaków."))
        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Hasło musi zawierać małą literę."))
        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Hasło musi zawierać wielką literę."))
        if not re.search(r"\d", password):
            raise ValidationError(_("Hasło musi zawierać cyfrę."))
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError(_("Hasło musi zawierać znak specjalny."))

    def get_help_text(self):
        return _("Hasło musi mieć min. 12 znaków i zawierać małą/wielką literę, cyfrę oraz znak specjalny.")
