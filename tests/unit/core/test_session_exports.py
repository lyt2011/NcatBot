"""Session 便利导出的独立进程回归测试。"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "imports",
    [
        "import ncatbot.plugin; import ncatbot.core",
        "import ncatbot.core; import ncatbot.plugin",
        "from ncatbot.core import SessionCancelled, SessionResult",
        "from ncatbot.core import *",
    ],
)
def test_session_export_import_order(imports):
    """CSE-01: 导入顺序不影响 Session 类型身份，不产生循环导入。"""
    code = (
        imports
        + """
from ncatbot.core import SessionCancelled, SessionResult
import ncatbot.plugin as plugin
assert SessionCancelled is plugin.SessionCancelled
assert SessionResult is plugin.SessionResult
"""
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_session_exports_discoverable_without_loading_plugin():
    """CSE-02: dir 枚举 Session 类型但不触发 plugin 初始化。"""
    code = """
import sys
import ncatbot.core as core
assert "ncatbot.plugin" not in sys.modules
assert {"SessionCancelled", "SessionResult", "AsyncEventDispatcher", "__name__"} <= set(dir(core))
assert "ncatbot.plugin" not in sys.modules
core.SessionResult
assert {"SessionCancelled", "SessionResult"} <= set(dir(core))
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
