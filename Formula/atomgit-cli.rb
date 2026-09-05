class AtomgitCli < Formula
  desc "Command-line interface for AtomGit"
  homepage "https://atomgit.com/hust-open-atom-club/atomgit-cli"
  url "https://atomgit.com/hust-open-atom-club/atomgit-cli.git",
      revision: "84b6de8b69652ad14660d728b91ebdae52ef5811"
  version "0.7.3-0.20260905003238-84b6de8b6965"
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
