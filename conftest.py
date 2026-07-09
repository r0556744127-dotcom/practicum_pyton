import sys
import os

# מוסיף אוטומטית את תיקיית השורש של הפרויקט לנתיבי החיפוש של פייתון
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))