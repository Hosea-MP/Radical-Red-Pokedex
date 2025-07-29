import ast
import sys

def traverse(obj, prefix=""):
    if isinstance(obj, dict):
        keys = list(obj.keys())
        # If all keys look numeric, treat as list-like and only use first key
        if all(isinstance(k, (int, float)) or str(k).isdigit() for k in keys):
            if keys:
                first = keys[0]
                new_prefix = f"{prefix}.[item]" if prefix else "[item]"
                try:
                    print(new_prefix)
                except BrokenPipeError:
                    sys.exit(0)
                traverse(obj[first], new_prefix)
            return
        for key, val in obj.items():
            new_prefix = f"{prefix}.{key}" if prefix else str(key)
            try:
                print(new_prefix)
            except BrokenPipeError:
                sys.exit(0)
            traverse(val, new_prefix)
    elif isinstance(obj, list) and obj:
        new_prefix = prefix + "[]"
        try:
            print(new_prefix)
        except BrokenPipeError:
            sys.exit(0)
        traverse(obj[0], new_prefix)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_structure.py <file>")
        return
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = f.read()
    obj = ast.literal_eval(data)
    try:
        traverse(obj)
    except BrokenPipeError:
        pass

if __name__ == '__main__':
    main()
