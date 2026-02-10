import os, sys
sys.path.insert(0, os.path.dirname(__file__))  # ensure this folder is importable

from FAIROS import FAIROS

if __name__ == "__main__":
    model = FAIROS()
    model.execute_algorithm("test")