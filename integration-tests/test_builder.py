import os
import re
import subprocess
import tempfile

from vdist.builder import Builder
from vdist.source import git, git_directory, directory


def _read_deb_contents(deb_file_pathname):
    entries = os.popen("dpkg -c {0}".format(deb_file_pathname)).readlines()
    file_list = [entry.split()[-1] for entry in entries]
    return file_list


def _purge_list(original_list, purgables):
    list_purged = []
    for entry in original_list:
        entry_free_of_purgables = all(True if re.match(pattern, entry) is None
                                      else False
                                      for pattern in purgables)
        if entry_free_of_purgables:
            list_purged.append(entry)
    return list_purged

# def test_generate_deb_from_git():
#     builder = Builder()
#     builder.add_build(
#         app='vdist-test-generate-deb-from-git',
#         version='1.0',
#         source=git(
#             uri='https://github.com/objectified/vdist',
#             branch='master'
#         ),
#         profile='ubuntu-trusty'
#     )
#     builder.build()
#
#     homedir = os.path.expanduser('~')
#     target_file = os.path.join(
#         homedir,
#         '.vdist',
#         'dist',
#         'vdist-test-generate-deb-from-git-1.0-ubuntu-trusty',
#         'vdist-test-generate-deb-from-git_1.0_amd64.deb'
#     )
#     assert os.path.isfile(target_file)
#     assert os.path.getsize(target_file) > 0


# Scenarios to test:
# 1.- Project containing a setup.py and compiles Python -> only package the
#     whole Python basedir.
# 2.- Project not containing a setup.py and compiles Python -> package both the
#     project dir and the Python basedir.
# 3.- Project containing a setup.py and using a prebuilt Python package (e.g.
#     not compiling) -> package the custom Python basedir only
# 4.- Project not containing a setup.py and using a prebuilt Python package ->
#     package both the project dir and the Python basedir
# More info at:
#   https://github.com/objectified/vdist/pull/7#issuecomment-177818848

# Scenario 1 - Project containing a setup.py and compiles Python -> only package
# the whole Python basedir.
def test_generate_deb_from_git_setup_compile():
    builder = Builder()
    builder.add_build(
        app='geolocate',
        version='1.3.0',
        source=git(
            uri='https://github.com/dante-signal31/geolocate',
            branch='master'
        ),
        profile='ubuntu-trusty',
        compile_python=True,
        compile_python_version='3.4.3',
        fpm_args='--maintainer dante.signal31@gmail.com -a native --url '
                 'https://github.com/dante-signal31/geolocate --description '
                 '"This program accepts any text and searchs inside every IP '
                 'address. With each of those IP addresses, geolocate queries '
                 'Maxmind GeoIP database to look for the city and country where'
                 ' IP address or URL is located. Geolocate is designed to be'
                 ' used in console with pipes and redirections along with '
                 'applications like traceroute, nslookup, etc.'
                 ' " --license BSD-3 --category net',
        requirements_path='/REQUIREMENTS.txt'
    )
    builder.build()
    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'geolocate-1.3.0-ubuntu-trusty',
        'geolocate_1.3.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    file_list = _read_deb_contents(target_file)
    entries_to_purge = [r'[^\.]', r'\./$', r'\./usr/', r'\./opt/$']
    file_list_purged = _purge_list(file_list, entries_to_purge)
    # At this point only a folder should remain if everything is correct.
    correct_install_path = "./opt/geolocate"
    assert all((True if correct_install_path in file_entry else False
                for file_entry in file_list_purged))
    # Geolocate launcher should we in bin folder too.
    geolocate_launcher = "./opt/geolocate/bin/geolocate"
    assert geolocate_launcher in file_list_purged


# Scenario 2.- Project not containing a setup.py and compiles Python -> package
# both the project dir and the Python basedir
def test_generate_deb_from_git_nosetup_compile():
    builder = Builder()
    builder.add_build(
        app='jtrouble',
        version='1.0.0',
        source=git(
            uri='https://github.com/objectified/jtrouble',
            branch='master'
        ),
        profile='ubuntu-trusty',
        compile_python=True,
        compile_python_version='3.4.3',
    )
    builder.build()
    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'jtrouble-1.0.0-ubuntu-trusty',
        'jtrouble_1.0.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    file_list = _read_deb_contents(target_file)
    entries_to_purge = [r'[^\.]', r'\./$', r'\./usr/', r'\./opt/$']
    file_list_purged = _purge_list(file_list, entries_to_purge)
    # At this point only two folders should remain if everything is correct:
    # application folder and compiled interpreter folder.
    correct_folders = ["./opt/jtrouble", "./opt/python3.4.3"]
    assert all((True if any(folder in file_entry for folder in correct_folders)
                else False
                for file_entry in file_list_purged))


# Scenario 3 - Project containing a setup.py and using a prebuilt Python package
# (e.g. not compiling) -> package the custom Python basedir only.
def test_generate_deb_from_git_setup_nocompile():
    builder = Builder()
    builder.add_build(
        app='geolocate',
        version='1.3.0',
        source=git(
            uri='https://github.com/dante-signal31/geolocate',
            branch='master'
        ),
        profile='ubuntu-trusty',
        compile_python=False,
        python_basedir='/usr',
        fpm_args='--maintainer dante.signal31@gmail.com -a native --url '
                 'https://github.com/dante-signal31/geolocate --description '
                 '"This program accepts any text and searchs inside every IP '
                 'address. With each of those IP addresses, geolocate queries '
                 'Maxmind GeoIP database to look for the city and country where'
                 ' IP address or URL is located. Geolocate is designed to be'
                 ' used in console with pipes and redirections along with '
                 'applications like traceroute, nslookup, etc.'
                 ' " --license BSD-3 --category net',
        requirements_path='/REQUIREMENTS.txt'
    )
    builder.build()
    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'geolocate-1.3.0-ubuntu-trusty',
        'geolocate_1.3.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    file_list = _read_deb_contents(target_file)
    entries_to_purge = [r'[^\.]', r'\./$', r'\./opt/$']
    file_list_purged = _purge_list(file_list, entries_to_purge)
    # At this point only a folder should remain if everything is correct.
    correct_install_path = "./usr"
    assert all((True if correct_install_path in file_entry else False
                for file_entry in file_list_purged))
    # If python basedir was properly packaged then /usr/bin/python should be
    # there.
    python_interpreter = "./usr/bin/python"
    assert python_interpreter in file_list_purged
    # If application was properly packaged then launcher should be in bin folder
    # too.
    geolocate_launcher = "./usr/bin/geolocate"
    assert geolocate_launcher in file_list_purged


# Scenario 4.- Project not containing a setup.py and using a prebuilt Python
# package -> package both the project dir and the Python basedir
def test_generate_deb_from_git_nosetup_nocompile():
    builder = Builder()
    builder.add_build(
        app='jtrouble',
        version='1.0.0',
        source=git(
            uri='https://github.com/objectified/jtrouble',
            branch='master'
        ),
        profile='ubuntu-trusty',
        compile_python=False,
        python_basedir='/usr',
    )
    builder.build()
    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'jtrouble-1.0.0-ubuntu-trusty',
        'jtrouble_1.0.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    file_list = _read_deb_contents(target_file)
    entries_to_purge = [r'[^\.]', r'\./$', r'\./opt/$']
    file_list_purged = _purge_list(file_list, entries_to_purge)
    # At this point only two folders should remain if everything is correct:
    # application folder and python basedir folder.
    correct_folders = ["./opt/jtrouble", "./usr"]
    assert all((True if any(folder in file_entry for folder in correct_folders)
                else False
                for file_entry in file_list_purged))
    # If python basedir was properly packaged then /usr/bin/python should be
    # there.
    python_interpreter = "./usr/bin/python"
    assert python_interpreter in file_list_purged


# def test_generate_deb_from_git_suffixed():
#     builder = Builder()
#     builder.add_build(
#         app='vdist-test-generate-deb-from-git-suffixed',
#         version='1.0',
#         source=git(
#             uri='https://github.com/objectified/vdist.git',
#             branch='master'
#         ),
#         profile='ubuntu-trusty'
#     )
#     builder.build()
#
#     homedir = os.path.expanduser('~')
#     target_file = os.path.join(
#         homedir,
#         '.vdist',
#         'dist',
#         'vdist-test-generate-deb-from-git-suffixed-1.0-ubuntu-trusty',
#         'vdist-test-generate-deb-from-git-suffixed_1.0_amd64.deb'
#     )
#     assert os.path.isfile(target_file)
#     assert os.path.getsize(target_file) > 0
#
#
# def test_generate_deb_from_git_directory():
#     tempdir = tempfile.gettempdir()
#     checkout_dir = os.path.join(tempdir, 'vdist')
#
#     git_p = subprocess.Popen(
#         ['git', 'clone',
#          'https://github.com/objectified/vdist',
#          checkout_dir])
#     git_p.communicate()
#
#     builder = Builder()
#     builder.add_build(
#         app='vdist-test-generate-deb-from-git-dir',
#         version='1.0',
#         source=git_directory(
#             path=checkout_dir,
#             branch='master'
#         ),
#         profile='ubuntu-trusty'
#     )
#     builder.build()
#
#     homedir = os.path.expanduser('~')
#     target_file = os.path.join(
#         homedir,
#         '.vdist',
#         'dist',
#         'vdist-test-generate-deb-from-git-dir-1.0-ubuntu-trusty',
#         'vdist-test-generate-deb-from-git-dir_1.0_amd64.deb'
#     )
#     assert os.path.isfile(target_file)
#     assert os.path.getsize(target_file) > 0
#
#
# def test_generate_deb_from_directory():
#     tempdir = tempfile.gettempdir()
#     checkout_dir = os.path.join(tempdir, 'vdist')
#
#     git_p = subprocess.Popen(
#         ['git', 'clone',
#          'https://github.com/objectified/vdist',
#          checkout_dir])
#     git_p.communicate()
#
#     builder = Builder()
#     builder.add_build(
#         app='vdist-test-generate-deb-from-dir',
#         version='1.0',
#         source=directory(
#             path=checkout_dir,
#         ),
#         profile='ubuntu-trusty'
#     )
#     builder.build()
#
#     homedir = os.path.expanduser('~')
#     target_file = os.path.join(
#         homedir,
#         '.vdist',
#         'dist',
#         'vdist-test-generate-deb-from-dir-1.0-ubuntu-trusty',
#         'vdist-test-generate-deb-from-dir_1.0_amd64.deb'
#     )
#     assert os.path.isfile(target_file)
#     assert os.path.getsize(target_file) > 0
