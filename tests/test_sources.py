from vdist.source import git, directory, git_directory


def test_source_type_git():
    s = git(uri='https://github.com/objectified/vdist')
    assert s['uri'] == 'https://github.com/objectified/vdist'

    s = git(uri='https://github.com/objectified/vdist.git')
    assert s['uri'] == 'https://github.com/objectified/vdist'


def test_source_type_directory():
    s = directory(path='/foo/bar/baz/')
    assert s['path'] == '/foo/bar/baz'


def test_source_type_git_directory():
    s = git_directory(path='/foo/bar/', branch='foo')
    assert s['branch'] == 'foo'
    assert s['path'] == '/foo/bar'
