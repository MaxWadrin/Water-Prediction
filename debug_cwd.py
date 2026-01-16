import os
print(f"CWD: {os.getcwd()}")
try:
    print(f"List dir .: {os.listdir('.')}")
except Exception as e:
    print(f"Error listing .: {e}")

try:
    print(f"List dir data: {os.listdir('data')}")
except Exception as e:
    print(f"Error listing data: {e}")

try:
    print(f"List dir data/v2: {os.listdir('data/v2')}")
except Exception as e:
    print(f"Error listing data/v2: {e}")
