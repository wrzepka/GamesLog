def has_uppercase(str):
    for char in str:
        if char.isupper():
            return True
    return False


def has_number(str):
    for char in str:
        if char.isdigit():
            return True
    return False


def has_special(str):
    if not str.isalnum():
        return True
    return False
