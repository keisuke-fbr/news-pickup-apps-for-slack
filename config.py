import importlib
import os
import sys

_name = os.getenv("PROFILE", "tech")
for _i, _a in enumerate(sys.argv):
    if _a == "--profile" and _i + 1 < len(sys.argv):
        _name = sys.argv[_i + 1]
    elif _a.startswith("--profile="):
        _name = _a.split("=", 1)[1]

_mod = importlib.import_module(f"profiles.{_name}")
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("_")})
