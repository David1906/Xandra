import re


def normalizeToRegex(txt: str):
    txt = txt.replace(" ", "\s*")
    txt = txt.replace("(", "\(")
    txt = txt.replace(")", "\)")
    txt = txt.replace(":", "\s*:")
    return txt.strip()
