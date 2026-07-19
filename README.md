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

When publishing a new `atomgit-cli` release, update the version, platform URLs, and SHA-256 values in [`Formula/atomgit-cli.rb`](Formula/atomgit-cli.rb), then run:

```bash
brew audit --strict atomgit-cli
brew test atomgit-cli
```
