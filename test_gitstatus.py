"""
Test module for gitstatus

Fixtures used to to setup git repo scenarios on the fly.
Tests are short and at the end of this file.
"""
from __future__ import absolute_import, print_function
import os
import re
import shlex
import shutil
import subprocess
import tempfile

import pytest

import gitstatus

GIT_STATUS = os.path.join(os.path.dirname(__file__), 'gitstatus.py')


def run_gitstatus():
    """
    Helper to simply run gitstatus in the current directory.

    Returns:
        The output of gitstatus.py in the CWD.
    """
    return subprocess.check_output(['python', GIT_STATUS]).decode('utf-8', errors='ignore')


@pytest.yield_fixture(scope="function")
def git_repo_compute_stats():
    """
    Create a fake git repo with the following properties:
        - upstream set to another local git repo
        - 3 staged files (1 changed, 2 additions)
        - 1 changed file unstaged
        - 2 untracked files
        - 1 stashed change set
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    folder_up = folder + "_upstream"
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line",
        "second:A single line",
        "third:A single line",
        "touch untracked1 untracked2",
        "git add first",
        "git commit -m 'first commit'",
        "first:Changes to stash",
        "git stash",
        "first:Changes to stage",
        "git add first second third",
        "first:Changes but unstaged",
        "cp -R %s %s" % (folder, folder_up),
        "git remote add -f up %s" % folder_up,
        "git branch --set-upstream-to=up/master",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(shlex.split(cmd),
                                          stdout=devnull, stderr=subprocess.STDOUT)

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


@pytest.yield_fixture(scope="function")
def git_repo_compute_stats_only_conflicts():
    """
    Create a fake git repo with the following properties:
        - upstream set to another local git repo
        - edit the same file and create a merge conflict
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    folder_up = folder + "_upstream"
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line\nsecond line\third line",
        "git add first",
        "git commit -m 'first commit'",
        "first:fourth line\nfifth line\n",
        "git add first",
        "git commit -m 'second commit'",
        "cp -R %s %s" % (folder, folder_up),
        "git reset --hard HEAD~1",
        "first:ninth line\ntenth line\n",
        "git add first",
        "git commit -m 'new second commit'",
        "git remote add -f up %s" % folder_up,
        "git branch --set-upstream-to=up/master",
        "git fetch up",
        "git merge up/master",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                try:
                    with open(os.devnull, 'w') as devnull:
                        subprocess.check_call(shlex.split(cmd),
                                              stdout=devnull, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError:
                    pass

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


@pytest.yield_fixture(scope="function")
def git_repo_branch_on_hash():
    """
    Create a fake git repo with the following properties:
        - 3 commits made
        - yield when on checkout hash
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line",
        "git add first",
        "git commit -m 'first commit'",
        "first:A second line",
        "git add first",
        "git commit -m 'second commit'",
        "git checkout HEAD~1",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(shlex.split(cmd),
                                          stdout=devnull, stderr=subprocess.STDOUT)

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


@pytest.yield_fixture(scope="function")
def git_repo_branch_on_master():
    """
    Create a fake git repo with the following properties:
        - 3 commits made
        - yield when on checkout hash
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line",
        "git add first",
        "git commit -m 'first commit'",
        "first:A second line",
        "git add first",
        "git commit -m 'second commit'",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(shlex.split(cmd),
                                          stdout=devnull, stderr=subprocess.STDOUT)

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


@pytest.yield_fixture(scope="function")
def git_repo_remote_ahead():
    """
    Create a fake git repo with the following properties:
        - main repo has 3 commits
        - upstream repo has 2 commits
        - main repo has upstream set and is AHEAD by 1 commit
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    folder_up = folder + "_upstream"
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line",
        "git add first",
        "git commit -m 'first commit'",
        "first:Second line",
        "git add first",
        "git commit -m 'second commit'",
        "cp -R %s %s" % (folder, folder_up),
        "first:third line",
        "git add first",
        "git commit -m 'third commit'",
        "git remote add -f up %s" % folder_up,
        "git branch --set-upstream-to=up/master",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(shlex.split(cmd),
                                          stdout=devnull, stderr=subprocess.STDOUT)

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


@pytest.yield_fixture(scope="function")
def git_repo_remote_behind():
    """
    Create a fake git repo with the following properties:
        - main repo has 2 commits
        - upstream repo has 3 commits
        - main repo has upstream set and is BEHIND by 1 commit
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    folder_up = folder + "_upstream"
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line",
        "git add first",
        "git commit -m 'first commit'",
        "first:Second line",
        "git add first",
        "git commit -m 'second commit'",
        "first:third line",
        "git add first",
        "git commit -m 'third commit'",
        "cp -R %s %s" % (folder, folder_up),
        "git remote add -f up %s" % folder_up,
        "git branch --set-upstream-to=up/master",
        "git reset --hard HEAD~1",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(shlex.split(cmd),
                                          stdout=devnull, stderr=subprocess.STDOUT)

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


@pytest.yield_fixture(scope="function")
def git_repo_remote_diverged():
    """
    Create a fake git repo with the following properties:
        - main repo has 3 commits
        - upstream repo has 3 commits
        - main repo has upstream set and is has diverged by 1 commit each way
    """
    cwd = os.getcwd()
    folder = tempfile.mkdtemp()
    folder_up = folder + "_upstream"
    cmds = [
        "git init",
        "git config user.email 'you@example.com'",
        "git config user.name 'Your Name'",
        "first:A single line",
        "git add first",
        "git commit -m 'first commit'",
        "first:Second line",
        "git add first",
        "git commit -m 'second commit'",
        "first:third line",
        "git add first",
        "git commit -m 'third commit'",
        "cp -R %s %s" % (folder, folder_up),
        "git remote add -f up %s" % folder_up,
        "git branch --set-upstream-to=up/master",
        "git reset --hard HEAD~1",
        "first:different third line",
        "git add first",
        "git commit -m 'different third commit'",
    ]
    try:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.makedirs(folder)
        os.chdir(folder)

        for cmd in cmds:
            if re.match(r'\S+:', cmd):
                assert len(cmd.split(":")) == 2
                fname, text = cmd.split(":")
                with open(os.path.join(folder, fname), 'a') as fout:
                    fout.write(text + '\n')
            else:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(shlex.split(cmd),
                                          stdout=devnull, stderr=subprocess.STDOUT)

        yield

    finally:
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass
        try:
            shutil.rmtree(folder_up)
        except (OSError, IOError):
            pass
        os.chdir(cwd)


def test_run_cmd():
    """ Simple string to suppress doc warning. """
    out = gitstatus.run_cmd(["echo", "It works"])
    assert out == "It works"


def test_run_cmd_fail():
    """ Simple string to suppress doc warning. """
    with pytest.raises(gitstatus.ProcessError):
        gitstatus.run_cmd(["false"])


def test_branch_fatal():
    """ Simple string to suppress doc warning. """
    cwd = os.getcwd()
    try:
        folder = tempfile.mkdtemp()
        os.chdir(folder)
        try:
            gitstatus.get_branch()
            assert False
        except SystemExit:
            pass
    finally:
        os.chdir(cwd)
        try:
            shutil.rmtree(folder)
        except (OSError, IOError):
            pass


def test_branch_master(git_repo_branch_on_master):
    """ Simple string to suppress doc warning. """
    assert gitstatus.get_branch() == 'master'


def test_branch_hash(git_repo_branch_on_hash):
    """ Simple string to suppress doc warning. """
    actual_hash = gitstatus.run_cmd(shlex.split('git rev-parse --short HEAD'))
    assert gitstatus.get_branch() == gitstatus.SYM_PREHASH + actual_hash


def test_compute_stats_no_conflicts(git_repo_compute_stats):
    """ Simple string to suppress doc warning. """
    assert run_gitstatus() == 'master 0 0 3 0 1 2 1'


def test_compute_stats_only_conflicts(git_repo_compute_stats_only_conflicts):
    """ Simple string to suppress doc warning. """
    assert run_gitstatus() == 'master 1 1 0 1 1 0 0'


def test_remote_ahead(git_repo_remote_ahead):
    """ Simple string to suppress doc warning. """
    assert run_gitstatus() == 'master 0 1 0 0 0 0 0'


def test_remote_behind(git_repo_remote_behind):
    """ Simple string to suppress doc warning. """
    assert run_gitstatus() == 'master 1 0 0 0 0 0 0'


def test_remote_diverged(git_repo_remote_diverged):
    """ Simple string to suppress doc warning. """
    assert run_gitstatus() == 'master 1 1 0 0 0 0 0'
