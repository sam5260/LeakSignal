import sys
import os

# Add backend/ to Python path so all internal imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from main import app  # noqa: F402, E402
