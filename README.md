# Homebrew Tap for atomgit-cli

Homebrew Formulae for development snapshots of [`atomgit-cli`](https://atomgit.com/hust-open-atom-club/atomgit-cli), powered by [@hust-open-atom-club](https://github.com/hust-open-atom-club).

The official Homebrew Core Formula provides the latest stable release:

```bash
brew install atomgit-cli
```

This tap follows the latest commit on AtomGit's `main` branch. Install it with
the fully qualified Formula name to distinguish it from the stable Core package:

```bash
brew install hust-open-atom-club/tap/atomgit-cli
```

> [!WARNING]
> The Homebrew Core and tap Formulae cannot be installed at the same time.
> Both install the same `ag` command, so take care to select the intended
> Formula. Always use the fully qualified
> `hust-open-atom-club/tap/atomgit-cli` name when installing, upgrading, or
> uninstalling the development snapshot.

The installed executable is named `ag`:

```bash
ag version
ag --help
```

## Upgrade

```bash
brew update
brew upgrade hust-open-atom-club/tap/atomgit-cli
```

## Uninstall

```bash
brew uninstall hust-open-atom-club/tap/atomgit-cli
brew untap hust-open-atom-club/tap
```

## Supported platforms

- macOS on Apple Silicon and Intel
- Linux on ARM64 and x86-64

The Formula pins an immutable AtomGit commit and builds `ag` from source. Its
development version includes the upstream commit timestamp, a collision counter
when needed, and the abbreviated SHA.

## Maintainers

The [`Update atomgit-cli Formula`](.github/workflows/update-formula.yml) workflow checks the latest AtomGit `main` commit every hour and can also be run manually. It pins the commit SHA, derives a Go-style development version from the latest stable release and commit timestamp, and opens a pull request. The workflow dispatches the Formula test matrix and automatically squash-merges the pull request after the macOS and Linux jobs pass.

Pull requests created by GitHub Actions must be enabled in the repository's Actions settings. The regular Formula test workflow validates automated update pull requests on macOS and Linux.

For a manual update, run:

```bash
python3 scripts/update_formula.py
brew audit --strict hust-open-atom-club/tap/atomgit-cli
brew test hust-open-atom-club/tap/atomgit-cli
```
