#!/usr/bin/env python3
"""Run ChanceRAG application."""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from chancerag.main import main

if __name__ == "__main__":
    main()
