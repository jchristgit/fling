# fling

A simple, pure Python 3 continuous integration server for use with Gitea.


## Usage

- Create a token in Gitea's "Application" settings
  (`user/settings/applications`)
- Start `fling` with the generated `--gitea-token`, ensure it is reachable to
  Gitea
- Configure a webhook in your repository to point to
  `http://<FLING_ADDR>/hook/gitea`
- Configure fling in your repository. For example, the following configuration
  can be used to test [`bolt`](https://github.com/jchristgit/bolt):

```dosini
+[fling]
+commands =
+  service postgresql start
+  su postgres -s /bin/sh -c 'psql -c "CREATE USER bolt PASSWORD '"'"'bolt'"'"' SUPERUSER" -d postgres'
+  su postgres -s /bin/sh -c 'psql -c "CREATE DATABASE bolt_test OWNER bolt" -d postgres'
+
+  export MIX_ENV=test
+  export PGSQL_TEST_URL=postgres://bolt:bolt@/bolt_test
+
+  mix local.hex --force
+  mix local.rebar --force
+  mix deps.get
+  mix deps.compile
+  mix compile
+packages = ca-certificates,elixir,erlang,git,postgresql-11
```

The packages specified in `packages` will be cached across invocations.
`commands` are simply run via shell.


## Execution

When `fling` receives a build via its webhook route `/hook/gitea`, it performs
the following:

- prepare a workspace (checkout the commit to build locally)
- load build configuration (from the default branch or the commit to build, see
  `--trust`)
- prepares Debian Stable in a chroot if the current one is outdated [1], this is
  called the *template machine*
- runs build commands in an ephemeral snapshot of the template machine

The commit status is updated on Gitea along the way.

[1] these are determined outdated in two cases: if the directory does not exist
at all, it is always considered outdated and recreated. Otherwise, fling
compares a hashsum of the configuration the image was built with with the
configuration that is desired, and if they mismatch, recreates the image


## Dependencies

- Python 3
- `debootstrap`
- `systemd-nspawn`
- `git`
- `root` access

## Setup

Configure root to have SSH keys to clone repositories you want to use it on.

Then, see `python3 -m fling --help` for usage. Do not bind fling on a public IP
address.

Once the server is running, add a webhook on your repositories to test, pointing
to the address of the fling server, path `/hook/gitea`.


<!-- vim: set tw=80: -->
