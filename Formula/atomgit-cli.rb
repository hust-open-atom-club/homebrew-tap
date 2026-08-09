class AtomgitCli < Formula
  desc "Command-line interface for AtomGit"
  homepage "https://atomgit.com/hust-open-atom-club/atomgit-cli"
  version "0.7.1"
  license "MulanPSL-2.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.1/ag_darwin_arm64.tar.gz"
      sha256 "3bd43232bc6bce6069fc25795a7fd12a6ab6a6f5bb067381fe908486bd68cddd"
    else
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.1/ag_darwin_amd64.tar.gz"
      sha256 "e18a4597fbd9f792c701b64d7e3220cfbf004904ad5db8cc08f6aa2d0228b2df"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.1/ag_linux_arm64.tar.gz"
      sha256 "af13a9637e814f17e306a637073202d4b27460f6c2f0aa7b0eb41be8153a5dc6"
    else
      url "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download/v0.7.1/ag_linux_amd64.tar.gz"
      sha256 "357190d45e3c13cfaa49ac0bff96f6c2d71bc60cfd6702a26a3308a630bac83a"
    end
  end

  def install
    bin.install "ag"
  end

  test do
    assert_match "v#{version}", shell_output("#{bin}/ag version")
  end
end
