# Homebrew Tap for atomgit-cli

Homebrew Formulae for the [`atomgit-cli`](https://github.com/hust-open-atom-club/atomgit-cli) binary, powered by [@hust-open-atom-club](https://github.com/hust-open-atom-club).

## Install

```bash
brew tap hust-open-atom-club/tap
brew install atomgit-cli
```

Or install directly:

```bash
brew install hust-open-atom-club/tap/atomgit-cli
```

The installed executable is named `ag`:

```bash
ag version
ag --help
```

## Upgrade

```bash
brew update
brew upgrade atomgit-cli
```

## Uninstall

```bash
brew uninstall atomgit-cli
brew untap hust-open-atom-club/tap
```

## Supported platforms

- macOS on Apple Silicon and Intel
- Linux on ARM64 and x86-64

The Formula installs checksum-verified binaries from the official [AtomGit releases](https://atomgit.com/hust-open-atom-club/atomgit-cli/releases).

## Maintainers

The [`Update atomgit-cli Formula`](.github/workflows/update-formula.yml) workflow checks the latest stable AtomGit release every four hours and can also be run manually. It downloads all four platform archives, recalculates their SHA-256 values, updates [`Formula/atomgit-cli.rb`](Formula/atomgit-cli.rb), and opens a pull request. The workflow dispatches the Formula test matrix and automatically squash-merges the pull request after the macOS and Linux jobs pass.

Pull requests created by GitHub Actions must be enabled in the repository's Actions settings. The regular Formula test workflow validates automated update pull requests on macOS and Linux.

For a manual update, run:

```bash
python3 scripts/update_formula.py
brew audit --strict atomgit-cli
brew test atomgit-cli
```
