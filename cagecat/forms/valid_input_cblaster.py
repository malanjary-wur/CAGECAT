"""Input validation functionality

Author: Matthias van den Belt
"""

import decimal

from wtforms import ValidationError

malicious_characters = ':“%$#>\'<'

def is_safe_string_value(form, field):
    if field.data is None:
        return

    unsafe_string, is_safe = is_safe_string(field.data)
    if not is_safe:
        raise ValidationError(f'Malicious character found: {unsafe_string}')

def is_safe_string(_string):
    if not isinstance(_string, (int, decimal.Decimal)):
        for char in _string:
            if char in malicious_characters:
                return char, False
    return None, True
