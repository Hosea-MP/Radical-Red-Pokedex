import ast
import sys


def remove_sprites(obj):
    """Recursively remove any 'sprites' keys from dictionaries."""
    if isinstance(obj, dict):
        obj = {k: remove_sprites(v) for k, v in obj.items() if k != 'sprites'}
    elif isinstance(obj, list):
        obj = [remove_sprites(v) for v in obj]
    return obj


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data.js'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'parsed_data.js'

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    data = ast.literal_eval(content)

    cleaned = remove_sprites(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(repr(cleaned))


if __name__ == '__main__':
    main()
