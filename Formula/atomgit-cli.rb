class AtomgitCli < Formula
  desc "Command-line interface for AtomGit"
  homepage "https://atomgit.com/hust-open-atom-club/atomgit-cli"
  version "0.7.2"
  license "MulanPSL-2.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.2/ag_darwin_arm64.tar.gz"
      sha256 "7c3313d853a51031eb0cf7c0f7c5a61809689fac29b3ba2ac578d63036e901b5"
    else
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.2/ag_darwin_amd64.tar.gz"
      sha256 "601983b23c5f99f89a8a7735e86ed4bee8a74dbd11e1c78d038ecfef85e1d30c"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.2/ag_linux_arm64.tar.gz"
      sha256 "8933a84d566fc523c4aaf8ec69bc46b6a9edcc020fd027040ec249274ad470b0"
    else
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.2/ag_linux_amd64.tar.gz"
      sha256 "065ade926a8ff44547f78eb48389b18c054edc624fbd533db71e0207f3a9a6f7"
    end
  end

  def install
    bin.install "ag"
  end

  test do
    assert_match "v#{version}", shell_output("#{bin}/ag version")
  end
end
