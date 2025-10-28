"""
Script v2 to fix AsyncClient usage in integration tests.

Fixes:
1. Remove 'async with async_client as client:' (fixture already opens client)
2. Use async_client directly
3. Update indentation accordingly
"""
import re
from pathlib import Path


def fix_test_file_v2(file_path: Path) -> bool:
    """
    Fix AsyncClient usage in a test file.

    Changes:
    - Remove 'async with async_client as client:' lines
    - Dedent the code inside that was indented for the context manager
    - Replace 'client' references with 'async_client'

    Returns:
        bool: True if file was modified, False otherwise
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    lines = content.split('\n')

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line is 'async with async_client as client:'
        if re.search(r'^\s+async with async_client as (client|ac):\s*$', line):
            # Skip this line (don't add it)
            # Also add a comment
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + '# Using async_client fixture from conftest.py')
            i += 1

            # Now dedent all following lines until we reach the same indentation level
            # The lines inside 'async with' are indented 4 more spaces
            base_indent = indent

            # Process the block that was inside 'async with'
            while i < len(lines):
                inner_line = lines[i]

                # If empty line, keep it
                if not inner_line.strip():
                    new_lines.append(inner_line)
                    i += 1
                    continue

                # Check current indentation
                current_indent = len(inner_line) - len(inner_line.lstrip())

                # If we've reached a line at or less indented than base, we're done with this block
                if current_indent <= base_indent and inner_line.strip():
                    break

                # Dedent by 4 spaces (or 8 if it was double-indented)
                # The content was indented 4 extra spaces for the 'async with'
                if current_indent > base_indent:
                    dedented_line = ' ' * (current_indent - 4) + inner_line.lstrip()
                    new_lines.append(dedented_line)
                else:
                    new_lines.append(inner_line)

                i += 1
        else:
            new_lines.append(line)
            i += 1

    content = '\n'.join(new_lines)

    # Now replace 'client' variable references with 'async_client'
    # But be careful not to replace strings or comments
    # Replace patterns like: client.post, client.get, etc.
    content = re.sub(r'\bclient\.', 'async_client.', content)

    # Fix any remaining AsyncClient(app=app, base_url="...") patterns
    content = re.sub(
        r'async with AsyncClient\(app=app,\s*base_url=["\']http://test["\']\)\s*as\s+(client|ac):',
        r'# Using async_client fixture from conftest.py',
        content
    )

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    """Fix all integration test files."""
    test_dir = Path('tests/integration')

    if not test_dir.exists():
        print(f"Directory {test_dir} not found")
        return

    test_files = list(test_dir.glob('test_*.py'))
    modified_count = 0

    for file_path in test_files:
        if fix_test_file_v2(file_path):
            print(f'[OK] Modified: {file_path.name}')
            modified_count += 1
        else:
            print(f'  Skipped: {file_path.name} (no changes needed)')

    print(f'\nTotal files: {len(test_files)}')
    print(f'Modified: {modified_count}')
    print(f'Unchanged: {len(test_files) - modified_count}')


if __name__ == '__main__':
    main()
