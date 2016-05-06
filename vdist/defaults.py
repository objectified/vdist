import os
import sys

PYTHON_BASEDIR = '/opt'
PYTHON_VERSION = '2.7.9'
LOCAL_PROFILES_DIR = 'buildprofiles'
LOCAL_PROFILES_FILE = 'profiles.json'
VDIST_USERDIR = os.path.join(os.path.expanduser('~'), '.vdist')
BUILD_BASEDIR = os.path.join(VDIST_USERDIR, 'dist')
SCRATCH_BUILDSCRIPT_NAME = 'buildscript.sh'
SCRATCH_DIR = 'scratch'
SHARED_DIR = '/work'
PACKAGE_INSTALL_ROOT = PYTHON_BASEDIR
PACKAGE_TMP_ROOT = '/tmp'

PYTHON3_INTERPRETER = True if sys.version_info[0] == 3 else False
