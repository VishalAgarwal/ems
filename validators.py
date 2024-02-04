from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_ten_digits(value):
    if len(value) != 10 or value.isnumeric() == False:
        raise ValidationError(
            _("%(value)s is not a valid 10 digit mobile number"),
            params={"value": value},
        )
