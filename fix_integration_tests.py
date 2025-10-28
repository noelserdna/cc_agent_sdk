"""
Script to fix AsyncClient syntax in integration tests.

Replaces old httpx syntax:
    async with AsyncClient(app=app, base_url="http://test") as client:

With fixture usage:
    # Uses async_client fixture from conftest.py
    # (add async_client parameter to test function)
"""
import re
from pathlib import Path


def fix_test_file(file_path: Path) -> bool:
    """
    Fix AsyncClient usage in a test file.

    Returns:
        bool: True if file was modified, False otherwise
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # Pattern 1: async with AsyncClient(app=app, base_url="...") as client:
    pattern1 = r'async with AsyncClient\(app=app,\s*base_url=["\']http://test["\']\)\s*as\s+(client|ac):'

    if re.search(pattern1, content):
        # Add async_client parameter to test functions that don't have it
        # Find all test functions
        test_func_pattern = r'async def (test_\w+)\(self(?:, (\w+(?:, \w+)*))?\):'

        def add_async_client_param(match):
            func_name = match.group(1)
            existing_params = match.group(2)

            if existing_params:
                # Check if async_client already in params
                if 'async_client' in existing_params:
                    return match.group(0)
                else:
                    return f'async def {func_name}(self, async_client, {existing_params}):'
            else:
                return f'async def {func_name}(self, async_client):'

        content = re.sub(test_func_pattern, add_async_client_param, content)

        # Replace AsyncClient usage with fixture
        content = re.sub(
            pattern1,
            r'# Using async_client fixture\n        async with async_client as \1:',
            content
        )

        # Remove unused imports
        if 'AsyncClient(' not in content and 'app=app' not in content:
            # Remove "from src.main import app"
            content = re.sub(r'from src\.main import app\n?', '', content)
            # Remove AsyncClient from httpx import
            content = re.sub(r'from httpx import AsyncClient\n?', '', content)
            content = re.sub(r',\s*AsyncClient', '', content)

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
        if fix_test_file(file_path):
            print(f'[OK] Modified: {file_path.name}')
            modified_count += 1
        else:
            print(f'  Skipped: {file_path.name} (no changes needed)')

    print(f'\nTotal files: {len(test_files)}')
    print(f'Modified: {modified_count}')
    print(f'Unchanged: {len(test_files) - modified_count}')


if __name__ == '__main__':
    main()
