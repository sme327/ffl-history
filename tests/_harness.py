"""Run utils.data outside Streamlit and serialize its output deterministically.

The derivations in utils/data.py are pure functions over the CSVs in data/ —
Streamlit is only involved via @st.cache_data. Stubbing the module out lets the
test suite import them with no Streamlit runtime, no ScriptRunContext warnings,
and no dependency on Streamlit being installed at all.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# Frames at or below this many rows are stored in full, so a failing test shows
# a readable diff. Larger ones store a digest plus head/tail, which still
# detects any change but keeps the repo from carrying megabytes of JSON.
FULL_CAPTURE_MAX_ROWS = 800
SAMPLE_ROWS = 20

# Guards against float noise across platforms and pandas versions without
# hiding real changes: league scores carry two decimals, ratios a handful more.
FLOAT_PRECISION = 6


def install_streamlit_stub() -> None:
    """Replace `streamlit` with a no-op module before utils.data imports it."""
    if getattr(sys.modules.get("streamlit"), "_fixture_stub", False):
        return

    stub = types.ModuleType("streamlit")
    stub._fixture_stub = True

    def cache_data(func=None, **_kwargs):
        # Supports both @st.cache_data and @st.cache_data(...)
        if func is None:
            return lambda f: f
        return func

    stub.cache_data = cache_data
    stub.cache_resource = cache_data
    sys.modules["streamlit"] = stub

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def _scalar(value):
    """Normalize numpy/pandas scalars into plain JSON-safe Python."""
    if value is None:
        return None

    # pandas NA/NaT/NaN — checked before anything else, since NaN is a float.
    try:
        import pandas as pd

        if value is pd.NaT or (not isinstance(value, (list, tuple, dict)) and pd.isna(value)):
            return None
    except (TypeError, ValueError):
        pass  # pd.isna raises on array-likes; fall through

    if isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return round(value, FLOAT_PRECISION)

    # numpy scalars expose .item()
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return _scalar(item())
        except (ValueError, AttributeError):
            pass

    if isinstance(value, (list, tuple)):
        return [_scalar(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _scalar(v) for k, v in value.items()}

    return str(value)


def _digest(payload) -> str:
    blob = json.dumps(payload, sort_keys=False, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def normalize(obj):
    """Turn a DataFrame / Series / dict / list into a stable JSON structure.

    Row order is preserved rather than sorted — these frames are frequently
    already ranked, so a change in order is itself a change worth failing on.
    """
    import pandas as pd

    if isinstance(obj, pd.DataFrame):
        rows = [{str(k): _scalar(v) for k, v in rec.items()} for rec in obj.to_dict("records")]
        out = {
            "type": "dataframe",
            "shape": [len(obj), len(obj.columns)],
            "columns": [str(c) for c in obj.columns],
            "digest": _digest(rows),
        }
        if len(rows) <= FULL_CAPTURE_MAX_ROWS:
            out["rows"] = rows
        else:
            out["head"] = rows[:SAMPLE_ROWS]
            out["tail"] = rows[-SAMPLE_ROWS:]
        return out

    if isinstance(obj, pd.Series):
        return {
            "type": "series",
            "length": len(obj),
            "values": {str(k): _scalar(v) for k, v in obj.items()},
        }

    if isinstance(obj, dict):
        return {"type": "dict", "value": {str(k): normalize(v) for k, v in obj.items()}}

    if isinstance(obj, (list, tuple)):
        return {"type": "list", "length": len(obj), "value": [normalize(v) for v in obj]}

    return {"type": "scalar", "value": _scalar(obj)}


def dump(name: str, payload) -> Path:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    path = FIXTURES / f"{name}.json"
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path


def load(name: str):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
