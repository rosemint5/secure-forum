import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    """
    Additional password strength rules.
    Minimum length is handled by Django's MinimumLengthValidator
    to avoid duplicate error messages.
    """

    def validate(self, password, user=None):
        # Do NOT check length here (handled by MinimumLengthValidator)

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter.")
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter.")
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                _("Password must contain at least one digit.")
            )

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError(
                _("Password must contain at least one special character.")
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
