from vdist.source import git


def test_source_type_git():
    s = git(uri='https://github.com/objectified/vdist')
    assert s['uri'] == 'https://github.com/objectified/vdist'

    s = git(uri='https://github.com/objectified/vdist.git')
    assert s['uri'] == 'https://github.com/objectified/vdist'
