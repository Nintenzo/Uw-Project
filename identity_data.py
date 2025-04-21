import random

LGBT_IDENTITIES = ["Lesbian", "Gay", "Bisexual", "Transgender"]


def get_pronouns(identity, original_gender=None):
    """Gets pronouns based on identity and original gender for Trans cases."""
    identity = identity.capitalize()
    original_gender = original_gender.capitalize() if original_gender else None

    if identity == "Lesbian":
        return "she/her"
    elif identity == "Gay":
        return "he/him"
    elif identity == "Bisexual":
        return random.choice(["she/her", "he/him", "they/them"])
    elif identity == "Transgender":
        if original_gender == "Female":
            return "he/him"
        elif original_gender == "Male":
            return "she/her"
        else:
            return "they/them"

    elif identity == "Male":
        return "he/him"
    elif identity == "Female":
        return "she/her"
    else:
        return None
