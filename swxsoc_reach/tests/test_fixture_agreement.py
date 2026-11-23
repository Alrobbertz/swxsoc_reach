"""
Check that the committed test CDFs agree with freshly processing their source CSVs.

The CDFs under ``swxsoc_reach/data/test/`` are generated from the CSVs in the
same directory. When the processing code changes (new variables, attributes,
dtypes, shapes, ...), these tests fail until the fixture CDFs are regenerated.

"Agreement" means matching global attributes, variable names, variable CDF
types (and string widths), variable shapes, and variable attributes. Data
values are not compared.

Regenerating the fixtures:

- UDL L1C: ``calibration.process_file`` on
  ``REACH-TEST_20250904T000000_20250904T010000.csv``
- Legacy L1/L2: ``legacy.process_legacy_day`` for 2026-08-01
"""

from pathlib import Path

import numpy as np
import pytest
from astropy.time import Time
from spacepy import pycdf

import swxsoc_reach.calibration.calibration as calib
from swxsoc_reach import _test_files_directory
from swxsoc_reach.calibration.legacy import process_legacy_day

UDL_CSV = _test_files_directory / "REACH-TEST_20250904T000000_20250904T010000.csv"
UDL_L1C_CDF = _test_files_directory / "reach_all_l1c_prelim_20250904T000000_v1.0.0.cdf"
LEGACY_DAY = Time("2026-08-01")
LEGACY_L1_CDF = _test_files_directory / "reach_all_l1_5s_20260801_v1.0.0.cdf"
LEGACY_L2_CDF = _test_files_directory / "reach_all_l2_5s_20260801_v1.0.0.cdf"

# Global attributes that depend on when / where the file was generated.
VOLATILE_GLOBAL_ATTRIBUTES = {"Generation_date", "REACH_version", "SWxSOC_version"}


def _normalize(value):
    """Return a plain-Python value so attribute values compare by content."""
    if isinstance(value, (str, bytes)):
        return value
    return np.asarray(value).tolist()


def _summarize_cdf(path: Path) -> dict:
    """Return the global attributes and per-variable type, shape, and attributes of a CDF."""
    with pycdf.CDF(str(path)) as cdf:
        global_attrs = {
            name: [_normalize(v) for v in cdf.attrs[name]]
            for name in cdf.attrs
            if name not in VOLATILE_GLOBAL_ATTRIBUTES
        }
        variables = {
            name: {
                "type": pycdf.lib.cdftypenames.get(var.type(), var.type()),
                "nelems": var.nelems(),  # string width for CDF_CHAR variables
                "shape": tuple(var.shape),
                "attrs": {k: _normalize(v) for k, v in var.attrs.items()},
            }
            for name, var in cdf.items()
        }
    return {"global_attrs": global_attrs, "variables": variables}


def _compare_cdfs(new_path: Path, ref_path: Path) -> list[str]:
    """Return a list of human-readable differences between two CDFs (empty if they agree)."""
    new = _summarize_cdf(new_path)
    ref = _summarize_cdf(ref_path)
    diffs = []

    new_g, ref_g = new["global_attrs"], ref["global_attrs"]
    for name in sorted(set(new_g) | set(ref_g)):
        if new_g.get(name) != ref_g.get(name):
            diffs.append(
                f"global attr {name!r}: processed={new_g.get(name)!r} "
                f"fixture={ref_g.get(name)!r}"
            )

    new_v, ref_v = new["variables"], ref["variables"]
    for name in sorted(set(new_v) - set(ref_v)):
        diffs.append(f"variable {name!r} only in processed output")
    for name in sorted(set(ref_v) - set(new_v)):
        diffs.append(f"variable {name!r} only in fixture")

    for name in sorted(set(new_v) & set(ref_v)):
        nv, rv = new_v[name], ref_v[name]
        for key in ("type", "nelems", "shape"):
            if nv[key] != rv[key]:
                diffs.append(
                    f"variable {name!r} {key}: processed={nv[key]!r} "
                    f"fixture={rv[key]!r}"
                )
        na, ra = nv["attrs"], rv["attrs"]
        for attr in sorted(set(na) | set(ra)):
            if na.get(attr) != ra.get(attr):
                diffs.append(
                    f"variable {name!r} attr {attr!r}: processed={na.get(attr)!r} "
                    f"fixture={ra.get(attr)!r}"
                )

    return diffs


def _assert_cdfs_agree(new_path: Path, ref_path: Path):
    diffs = _compare_cdfs(new_path, ref_path)
    assert not diffs, (
        f"{ref_path.name} is out of date with the processing code "
        f"({len(diffs)} difference(s)); regenerate the fixture:\n  "
        + "\n  ".join(diffs)
    )


@pytest.fixture(scope="module")
def udl_output_files(tmp_path_factory):
    """Process the UDL test CSV once (``process_file`` writes to the cwd)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(tmp_path_factory.mktemp("udl"))
        return calib.process_file(UDL_CSV)


@pytest.fixture(scope="module")
def legacy_output_files(tmp_path_factory):
    """Process the Legacy test CSV once."""
    return process_legacy_day(
        LEGACY_DAY, _test_files_directory, output_dir=tmp_path_factory.mktemp("legacy")
    )


def _find_output(output_files, fixture_path):
    matches = [Path(p) for p in output_files if Path(p).name == fixture_path.name]
    assert matches, (
        f"Processing did not produce {fixture_path.name}; got "
        f"{[Path(p).name for p in output_files]}"
    )
    return matches[0]


def test_udl_l1c_fixture_agrees_with_processing(udl_output_files):
    _assert_cdfs_agree(_find_output(udl_output_files, UDL_L1C_CDF), UDL_L1C_CDF)


@pytest.mark.parametrize(
    "fixture_path", [LEGACY_L1_CDF, LEGACY_L2_CDF], ids=["l1", "l2"]
)
def test_legacy_fixture_agrees_with_processing(legacy_output_files, fixture_path):
    _assert_cdfs_agree(_find_output(legacy_output_files, fixture_path), fixture_path)


def test_compare_cdfs_detects_differences(tmp_path):
    """The comparison should flag attribute, shape, and variable differences."""
    a = tmp_path / "a.cdf"
    b = tmp_path / "b.cdf"
    for path, n, units, extra in ((a, 3, "km", False), (b, 4, "m", True)):
        with pycdf.CDF(str(path), "") as cdf:
            cdf.attrs["Project"] = "REACH"
            cdf.attrs["Generation_date"] = str(path)  # volatile; ignored
            cdf["x"] = np.zeros(n)
            cdf["x"].attrs["UNITS"] = units
            if extra:
                cdf["y"] = np.zeros(n)

    diffs = _compare_cdfs(a, b)
    assert any("'x' shape" in d for d in diffs)
    assert any("'x' attr 'UNITS'" in d for d in diffs)
    assert any("'y' only in fixture" in d for d in diffs)
    assert not any("Generation_date" in d for d in diffs)
    assert _compare_cdfs(a, a) == []
