import os
import sys
import runpy
import xml.etree.ElementTree as ET
import pya

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

print("=== Phase 3E-7.8C-3 GUI TEG ===")

pcell_macro = os.path.join(
    ROOT, "pymacros", "photonics_pdk_v4.lym"
)

# KLayout LYMからPythonコードを抽出
tree = ET.parse(pcell_macro)
root = tree.getroot()

script = root.findtext("text")

if not script:
    raise RuntimeError(
        "Python code not found in PCell LYM"
    )

print("Loading PCell Library v4...")

# PCell定義を実行してライブラリを登録
namespace = {
    "__name__": "__main__",
    "__file__": pcell_macro,
}

exec(compile(script, pcell_macro, "exec"), namespace)

print("Registered libraries:")
for name in pya.Library.library_names():
    print(" ", name)

# GDS生成
generator = os.path.join(
    ROOT, "tools", "generate_auto_quality_gui_teg.py"
)

runpy.run_path(generator, run_name="__main__")
