EMAIL_REGULAR_FOR_VALIDATION = (
    r"(?:[a-z0-9!#$%&"
    r"'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
    r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|'
    r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9]'
    r"(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|"
    r"\[(?:(?:25[0-5]|2[0-4][0-9]|"
    r"[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|"
    r"[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:"
    r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|"
    r"\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
)
PHONE_REGULAR_FOR_VALIDATION = r"^\+7\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}$"
SKYPE_REGULAR = r"skype:([a-z]+.)*[a-z]+"
SKYPE_REGULAR_FOR_VALIDATION = (r"^({}$|" r'<a href="{}\?call">.*</a>$)').format(
    SKYPE_REGULAR, SKYPE_REGULAR
)
