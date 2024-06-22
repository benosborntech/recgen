SEP = ":"

def key_concat(*args: list[str]) -> str:
    return SEP.join(args)

def key_split(key: str) -> str:
    return key.split(SEP)[-1]