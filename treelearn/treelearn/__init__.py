import collections

### HyperOptimization Parameters ###

Scalar = collections.namedtuple("Scalar", ("scale", "default", "min", "max"))
Either = collections.namedtuple("Either", ("alternatives",))

def linear(default, min = None, max = None):
    return Scalar("linear", default, min, max)

def logarithmic(default, min = None, max = None):
    return Scalar("logarithmic", default, min, max)

def either(*options):
    return Either(options)

### Execution ###

Command = collections.namedtuple("Command", ("shell", "chdir", "options"))

def command(shell, chdir = None, options = {}):
    """Defines a runnable command for a TreeLearn stage."""
    return Command(shell, chdir, options)

### Running ###

import argparse, os, subprocess, string, logging
from os import path

def sh(cmd, **subs):
    """Run the given shell command."""
    full_cmd = string.Template(cmd).substitute(**subs)
    logging.debug("$ %s", full_cmd)
    subprocess.check_call(full_cmd, shell=True)

def clone_or_update(remote, local):
    """Clone or update the git repository 'remote' in path 'local'.
    Note that 'remote' may be of the form 'uri@branch', in which case the specified
    branch is checked out, or brought up-to-date in the clone."""
    parts = remote.split("@")
    remote_url = parts[0]
    branch = parts[-1] if len(parts) >= 2 else "master"
    if path.exists(path.join(local)):
        sh("git -C ${LOCAL} checkout -q ${BRANCH} && git -C ${LOCAL} pull -q",
           LOCAL = local, BRANCH = branch)
    else:
        sh("git clone ${REMOTE} ${LOCAL} -q --branch ${BRANCH}",
           REMOTE = remote_url, LOCAL = local, BRANCH = branch)

def run(init, step, eval,
        description = "(unknown)",
        repositories = {}):
    """The main entry point for a treelearn application (defines a console entry point)."""

    parser = argparse.ArgumentParser(description="TreeLearn: %s" % description)
    parser.add_argument("-w", "--working", metavar="DIR",
                        help="Set the working directory for optimization",
                        default = path.join(os.getcwd(), "out"))
    args = parser.parse_args()

    # Set the current directory as requested - ideally, nothing else should change
    # working directory, after this
    if not path.exists(args.working):
        os.makedirs(args.working)
    os.chdir(args.working)

    # Initial clone of repositories
    logging.debug("Fetching repositories %s", ' '.join(repositories.keys()))
    local_repo_base = "repo"
    if not path.exists(local_repo_base):
        os.makedirs(local_repo_base)
    local_repos = {key: path.join(local_repo_base, key) for key in repositories}
    for key in repositories:
        clone_or_update(repositories[key], local_repos[key])

    # Main operation loop
    while True:
        pass # TODO
