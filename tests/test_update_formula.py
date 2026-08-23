from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "update_formula.py"
SPEC = importlib.util.spec_from_file_location("update_formula", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
update_formula = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update_formula)


class UpdateFormulaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.revision = "db67692448b416e86ffadd33e59b333c6909447e"
        self.version = "0.7.3-0.20260821123630-db67692448b4"
        self.formula = (
            'class AtomgitCli < Formula\n'
            '  url "https://atomgit.com/example.git",\n'
            f'      revision: "{self.revision}"\n'
            f'  version "{self.version}"\n'
            "end\n"
        )

    def test_snapshot_version_uses_next_patch_and_utc_timestamp(self) -> None:
        committed_at = datetime(
            2026, 8, 21, 20, 36, 30, tzinfo=timezone.utc
        )

        version = update_formula.snapshot_version(
            (0, 7, 2), self.revision, committed_at
        )

        self.assertEqual("0.7.3-0.20260821203630-db67692448b4", version)

    def test_current_snapshot_validates_revision(self) -> None:
        version, revision, release, timestamp = update_formula.current_snapshot(
            self.formula
        )

        self.assertEqual(self.version, version)
        self.assertEqual(self.revision, revision)
        self.assertEqual((0, 7, 2), release)
        self.assertEqual(
            datetime(2026, 8, 21, 12, 36, 30, tzinfo=timezone.utc),
            timestamp,
        )

    def test_validate_update_rejects_release_downgrade(self) -> None:
        old_timestamp = datetime(2026, 8, 21, tzinfo=timezone.utc)
        newer_timestamp = datetime(2026, 8, 22, tzinfo=timezone.utc)
        newer_revision = "0123456789abcdef0123456789abcdef01234567"

        with self.assertRaisesRegex(
            update_formula.UpdateError,
            "latest release from v0.7.2 back to v0.7.1",
        ):
            update_formula.validate_update(
                (0, 7, 2),
                self.revision,
                old_timestamp,
                (0, 7, 1),
                newer_revision,
                newer_timestamp,
            )

    def test_validate_update_allows_new_release_on_same_commit(self) -> None:
        timestamp = datetime(2026, 8, 21, tzinfo=timezone.utc)

        update_formula.validate_update(
            (0, 7, 2),
            self.revision,
            timestamp,
            (0, 8, 0),
            self.revision,
            timestamp,
        )

    def test_update_formula_replaces_version_and_revision(self) -> None:
        revision = "0123456789abcdef0123456789abcdef01234567"
        version = "0.7.3-0.20260822112233-0123456789ab"

        updated = update_formula.update_formula(self.formula, version, revision)

        self.assertIn(f'version "{version}"', updated)
        self.assertIn(f'revision: "{revision}"', updated)
        self.assertNotIn(self.version, updated)
        self.assertNotIn(self.revision, updated)

    def test_current_snapshot_rejects_mismatched_short_commit(self) -> None:
        formula = self.formula.replace("db67692448b4", "0123456789ab", 1)

        with self.assertRaisesRegex(
            update_formula.UpdateError,
            "version and Git revision do not match",
        ):
            update_formula.current_snapshot(formula)


if __name__ == "__main__":
    unittest.main()
