import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mtg_pipeline.run_pipeline import main

if __name__ == '__main__':
    main()
