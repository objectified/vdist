def git(uri=None, branch='master'):
    return dict(type='git', uri=uri, branch=branch)


def directory(path=None):
    return dict(type='directory', path=path)

def git_directory(path=None, branch='master'):
    return dict(type='git_directory', path=path, branch=branch)
