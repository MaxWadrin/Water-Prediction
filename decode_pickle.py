import base64
import sys

try:
    with open('temp.b64', 'r') as f:
        data = f.read().strip()
    
    decoded = base64.b64decode(data)
    
    sys.stdout.buffer.write(decoded)
except Exception as e:
    # print(f"Error: {e}", file=sys.stderr) # Print error to stderr
    sys.exit(1)
