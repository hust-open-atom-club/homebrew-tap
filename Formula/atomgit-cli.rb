class AtomgitCli < Formula
  desc "Command-line interface for AtomGit"
  homepage "https://atomgit.com/hust-open-atom-club/atomgit-cli"
  url "https://atomgit.com/hust-open-atom-club/atomgit-cli.git",
      revision: "996fd25284d2ff7c53c56bc572a28e3506508fa2"
  version "0.7.4-0.20260905095204-996fd25284d2"
  license "MulanPSL-2.0"

  depends_on "go" => :build

  def install
    ldflags = %W[
      -X atomgit.com/hust-open-atom-club/atomgit-cli/internal/version.Version=#{version}
      -X atomgit.com/hust-open-atom-club/atomgit-cli/internal/version.Commit=#{stable.specs[:revision]}
    ]
    system "go", "build", *std_go_args(ldflags:, output: bin/"ag"), "./cmd/ag"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/ag version")

    system bin/"ag", "alias", "set", "rv", "repo", "view"
    aliases = shell_output("#{bin}/ag alias list")
    assert_match "rv", aliases
    assert_match "repo view", aliases
  end
end
