def git(uri=None, branch='master'):
    if uri.endswith('.git'):
        uri = uri[:-4]
    return dict(type='git', uri=uri, branch=branch)


def directory(path=None):
    path = path.rstrip('/')
    return dict(type='directory', path=path)


def git_directory(path=None, branch='master'):
    path = path.rstrip('/')
    return dict(type='git_directory', path=path, branch=branch)
