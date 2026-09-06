class AtomgitCli < Formula
  desc "Command-line interface for AtomGit"
  homepage "https://atomgit.com/hust-open-atom-club/atomgit-cli"
  url "https://atomgit.com/hust-open-atom-club/atomgit-cli.git",
      revision: "f7fd24c0195b67db70d4465bafa95c5af7806ab7"
  version "0.7.4-0.20260906123538-f7fd24c0195b"
  license "MulanPSL-2.0"

  depends_on "go" => :build

  def build_date
    timestamp = version.to_s[/\A\d+\.\d+\.\d+-0\.(\d{14})(?:\.\d+)?-[0-9a-f]{12}\z/, 1]
    odie "Cannot derive build date from snapshot version #{version}" if timestamp.nil?

    Time.utc(
      timestamp[0, 4].to_i,
      timestamp[4, 2].to_i,
      timestamp[6, 2].to_i,
      timestamp[8, 2].to_i,
      timestamp[10, 2].to_i,
      timestamp[12, 2].to_i,
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
  end

  def install
    ldflags = %W[
      -X atomgit.com/hust-open-atom-club/atomgit-cli/internal/version.Version=#{version}
      -X atomgit.com/hust-open-atom-club/atomgit-cli/internal/version.Commit=#{stable.specs[:revision]}
      -X atomgit.com/hust-open-atom-club/atomgit-cli/internal/version.BuildDate=#{build_date}
    ]
    system "go", "build", *std_go_args(ldflags:, output: bin/"ag"), "./cmd/ag"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/ag version")
    assert_match(/"buildDate":\s*"#{Regexp.escape(build_date)}"/, shell_output("#{bin}/ag version --json"))

    system bin/"ag", "alias", "set", "rv", "repo", "view"
    aliases = shell_output("#{bin}/ag alias list")
    assert_match "rv", aliases
    assert_match "repo view", aliases
  end
end
