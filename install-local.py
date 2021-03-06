#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import unicode_literals

import contextlib
import distutils.spawn
import io
import os.path
import shutil
import subprocess
import sys
import tarfile


if str is bytes:
    from urllib import urlopen
else:
    from urllib.request import urlopen


TGZ = (
    'https://pypi.python.org/packages/source/v/virtualenv/'
    'virtualenv-1.11.6.tar.gz'
)
PKG_PATH = '/tmp/.virtualenv-pkg'


def clean():
    if os.path.exists(PKG_PATH):
        shutil.rmtree(PKG_PATH)


@contextlib.contextmanager
def clean_path():
    try:
        yield
    finally:
        clean()


def virtualenv(path):
    clean()

    print('Downloading ' + TGZ)
    tar_contents = io.BytesIO(urlopen(TGZ).read())
    with contextlib.closing(tarfile.open(fileobj=tar_contents)) as tarfile_obj:
        # Chop off the first path segment to avoid having the version in
        # the path
        for member in tarfile_obj.getmembers():
            _, _, member.name = member.name.partition('/')
            if member.name:
                tarfile_obj.extract(member, PKG_PATH)
    print('Done.')

    with clean_path():
        return subprocess.call((
            sys.executable, os.path.join(PKG_PATH, 'virtualenv.py'), path,
        ))


def main():
    venv_path = os.path.join(os.environ['HOME'], '.pre-commit-venv')
    virtualenv(venv_path)

    subprocess.check_call((
        os.path.join(venv_path, 'bin', 'pip'), 'install', 'pre-commit',
    ))

    bin_dir = os.path.join(os.environ['HOME'], 'bin')
    script_src = os.path.join(venv_path, 'bin', 'pre-commit')
    script_dest = os.path.join(bin_dir, 'pre-commit')
    print('*' * 79)
    print('Installing pre-commit to {0}'.format(script_dest))
    print('*' * 79)

    if not os.path.exists(bin_dir):
        os.mkdir(bin_dir)

    # os.symlink is not idempotent
    if os.path.exists(script_dest):
        os.remove(script_dest)

    os.symlink(script_src, script_dest)

    if not distutils.spawn.find_executable('pre-commit'):
        print('It looks like {0} is not on your path'.format(bin_dir))
        print('You may want to add it.')
        print('Often this does the trick: source ~/.profile')


if __name__ == '__main__':
    exit(main())
