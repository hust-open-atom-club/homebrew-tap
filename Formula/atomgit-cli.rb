class AtomgitCli < Formula
  desc "Command-line interface for AtomGit"
  homepage "https://atomgit.com/hust-open-atom-club/atomgit-cli"
  version "0.6.0"
  license "MulanPSL-2.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.6.0/ag_darwin_arm64.tar.gz"
      sha256 "9810381a0a6ab7d7f277d2be114f79d5d98c42478121f7a057fac093f3e45f99"
    else
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.6.0/ag_darwin_amd64.tar.gz"
      sha256 "f26d386cc79a298592d2fc32142d2d5b409fd96e700266d34dcfc1acbc97d0c6"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.6.0/ag_linux_arm64.tar.gz"
      sha256 "6300f78df686d612a564551dfa48341a9e893bba1ccd6faab2eea13c017dbdfd"
    else
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.6.0/ag_linux_amd64.tar.gz"
      sha256 "4c36f57c74bd8e0d5aca0a9dc90e7840c069482078d13bd8c13c72ca2a1b5865"
    end
  end

  def install
    bin.install "ag"
  end

  test do
    assert_match "v#{version}", shell_output("#{bin}/ag version")
  end
end
