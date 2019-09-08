# fling

A simple, pure Python 3.7 continuous integration server for use with Gitea.

## Goals

- simple to configure
- simple to run
- lightweight
- runs builds
- reports commit status

## Dependencies

- Python 3.7
- `debootstrap`
- `systemd-nspawn`
- `git`
- `root` access

## Usage

Configure root to have SSH keys to clone repositories you want to use it on.

Then, see `python3 -m fling --help` for usage. Do not bind fling on a public IP
address.

## Execution

When `fling` receives a build via its webhook route `/hook/gitea`, it performs
the following:

- prepare a workspace (checkout the commit to build locally)
- load build configuration (from the default branch or the commit to build, see `--trust`)
- prepares Debian in a chroot if the current one is outdated [1], this is called
  the *template machine*
- runs build commands in an ephemeral snapshot of the template machine

The commit status is updated on Gitea along the way.


[1] these are determined outdated in two cases: if the directory does not exist
at all, it is always considered outdated and recreated. Otherwise, fling
compares a hashsum of the configuration the image was built with with the
configuration that is desired, and if they mismatch, recreates the image


<!-- vim: set tw=80: -->
