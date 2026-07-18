import sys
import os

# מוסיף אוטומטית את תיקיית השורש של הפרויקט + תיקיית core לנתיבי החיפוש של פייתון
_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))
