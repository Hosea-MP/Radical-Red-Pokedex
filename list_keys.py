import ast
import sys
from collections import deque

def collect_keys(obj):
    unique = set()
    queue = deque([obj])
    while queue:
        item = queue.popleft()
        if isinstance(item, dict):
            for k, v in item.items():
                # only record non-numeric keys
                if not (isinstance(k, int) or str(k).isdigit()):
                    unique.add(str(k))
                queue.append(v)
        elif isinstance(item, list):
            queue.extend(item)
    return unique


def main():
    if len(sys.argv) < 2:
        print("Usage: python list_keys.py <file>")
        return
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = ast.literal_eval(f.read())
    keys = collect_keys(data)
    for key in sorted(keys):
        try:
            print(key)
        except BrokenPipeError:
            return

if __name__ == '__main__':
    main()
