def urljoin(*args):
    return "/".join(map(lambda x: str(x).strip("/"), args))
