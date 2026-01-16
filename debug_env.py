import os
import sys

print(f"CWD: {os.getcwd()}")
print(f"Python: {sys.executable}")

try:
    import networkx
    print(f"NetworkX version: {networkx.__version__}")
except ImportError as e:
    print(f"ImportError: {e}")

try:
    with open("test_write.txt", "w") as f:
        f.write("Hello")
    print("Write success")
except Exception as e:
    print(f"Write error: {e}")
