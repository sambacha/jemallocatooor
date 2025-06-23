#!/usr/bin/env python3
"""
Comprehensive TiKV to 'jemallocatooor' Migration Script

This script safely migrates the TiKV jemalloc project to use 'jemallocatooor' naming
and removes all TiKV branding, replacing it with 'sambacha/jemallocatooor'.
It performs extensive validation before making any changes and uses git mv for renames.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import shutil

class MigrationValidator:
    """Handles all validation and pre-flight checks"""
    
    def __init__(self, root_path: str, ignore_dirty: bool = False):
        self.root = Path(root_path).resolve()
        self.ignore_dirty = ignore_dirty
        self.found_patterns: Dict[str, List[Tuple[str, str]]] = {}
        self.expected_directories = [
            'jemallocator',
            'jemallocator-global', 
            'jemalloc-ctl',
            'jemalloc-sys'
        ]
        
    def validate_git_repo(self) -> None:
        """Ensure we're in a git repository and optionally check if it's clean"""
        if not (self.root / '.git').exists():
            raise RuntimeError(f"Not a git repository: {self.root}")
            
        if self.ignore_dirty:
            print("⚠️  Skipping git status check (--ignore-dirty flag)")
            return
            
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              cwd=self.root, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("Failed to check git status")
            
        # Allow only the CLAUDE.md file to be untracked (from gitStatus)
        lines = [line for line in result.stdout.strip().split('\n') if line]
        allowed_untracked = ['?? jemalloc-sys/CLAUDE.md']
        
        dirty_files = []
        for line in lines:
            if line not in allowed_untracked:
                dirty_files.append(line)
        
        if dirty_files:
            print("⚠️  Git working directory has uncommitted changes:")
            for line in dirty_files:
                print(f"    {line}")
            print("\nUse --ignore-dirty to proceed anyway, or commit/stash changes first.")
            raise RuntimeError("Git working directory not clean")
        
        print("✓ Git repository validation passed")
    
    def validate_directory_structure(self) -> None:
        """Verify expected directory structure exists"""
        missing_dirs = []
        for dirname in self.expected_directories:
            dir_path = self.root / dirname
            if not dir_path.exists() or not dir_path.is_dir():
                missing_dirs.append(dirname)
        
        if missing_dirs:
            raise RuntimeError(f"Missing expected directories: {missing_dirs}")
            
        print(f"✓ Directory structure validation passed ({len(self.expected_directories)} dirs)")
    
    def scan_for_patterns(self) -> None:
        """Scan entire codebase for TiKV naming patterns"""
        patterns = {
            'tikv-jemallocator-global': r'\btikv-jemallocator-global\b',
            'tikv-jemallocator': r'\btikv-jemallocator\b',
            'tikv-jemalloc-ctl': r'\btikv-jemalloc-ctl\b', 
            'tikv-jemalloc-sys': r'\btikv-jemalloc-sys\b',
            'tikv/jemallocator': r'\btikv/jemallocator\b',
            'TiKV Project Developers': r'The TiKV Project Developers',
            'tikv': r'\btikv\b',
            'TiKV': r'\bTiKV\b',
            'jemallocator_docs': r'\bjemallocator_docs\b'
        }
        
        # File extensions to scan
        extensions = {'.toml', '.rs', '.md', '.yml', '.yaml', '.sh'}
        
        for pattern_name, pattern_regex in patterns.items():
            self.found_patterns[pattern_name] = []
            compiled_pattern = re.compile(pattern_regex)
            
            for file_path in self.root.rglob('*'):
                # Skip .git directory and jemalloc submodule internals
                if '.git' in file_path.parts or 'jemalloc/jemalloc' in str(file_path):
                    continue
                    
                if file_path.is_file() and file_path.suffix in extensions:
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        matches = compiled_pattern.findall(content)
                        if matches:
                            rel_path = file_path.relative_to(self.root)
                            self.found_patterns[pattern_name].append((str(rel_path), content))
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        # Print summary
        total_files = sum(len(files) for files in self.found_patterns.values())
        print(f"✓ Pattern scanning complete - found {total_files} files with TiKV patterns")
        
        for pattern, files in self.found_patterns.items():
            if files:
                print(f"  - {pattern}: {len(files)} files")


class JemallocatooorMigrator:
    """Handles the actual migration process"""
    
    def __init__(self, root_path: str, validator: MigrationValidator):
        self.root = Path(root_path).resolve()
        self.validator = validator
        
        # Define migration mappings
        self.dir_mappings = {
            'jemallocator': 'jemallocatooor',
            'jemallocator-global': 'jemallocatooor-global',
            'jemalloc-ctl': 'jemallocatooor-ctl', 
            'jemalloc-sys': 'jemallocatooor-sys'
        }
        
        self.content_mappings = {
            'tikv-jemallocator-global': 'jemallocatooor-global',
            'tikv-jemallocator': 'jemallocatooor',
            'tikv-jemalloc-ctl': 'jemallocatooor-ctl',
            'tikv-jemalloc-sys': 'jemallocatooor-sys',
            'tikv/jemallocator': 'sambacha/jemallocatooor',
            'The TiKV Project Developers': 'sambacha',
            'TiKV': 'jemallocatooor',
            'tikv': 'jemallocatooor',
            # Keep jemallocator_docs as is - it's a feature flag
        }
        
    def execute_git_mv(self, old_path: str, new_path: str) -> None:
        """Execute git mv command with validation"""
        old_full = self.root / old_path
        new_full = self.root / new_path
        
        # Pre-conditions
        assert old_full.exists(), f"Source path does not exist: {old_path}"
        assert not new_full.exists(), f"Destination already exists: {new_path}"
        
        # Execute git mv
        result = subprocess.run(['git', 'mv', old_path, new_path], 
                              cwd=self.root, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"git mv failed: {result.stderr}")
            
        # Post-conditions
        assert not old_full.exists(), f"Source still exists after mv: {old_path}"
        assert new_full.exists(), f"Destination not created: {new_path}" 
        
        print(f"✓ Moved: {old_path} → {new_path}")
    
    def rename_directories(self) -> None:
        """Rename all main directories using git mv"""
        print("\n=== Phase 1: Directory Renaming ===")
        
        # Rename in specific order to avoid conflicts
        rename_order = ['jemallocator-global', 'jemalloc-ctl', 'jemalloc-sys', 'jemallocator']
        
        for old_name in rename_order:
            if old_name in self.dir_mappings:
                new_name = self.dir_mappings[old_name]
                self.execute_git_mv(old_name, new_name)
        
        # Update workspace members in root Cargo.toml
        root_cargo = self.root / 'Cargo.toml'
        content = root_cargo.read_text()
        
        # Update the members array
        new_content = content.replace(
            'members = ["jemallocator", "jemallocator-global", "jemalloc-ctl", "jemalloc-sys"]',
            'members = ["jemallocatooor", "jemallocatooor-global", "jemallocatooor-ctl", "jemallocatooor-sys"]'
        )
        
        assert new_content != content, "Root Cargo.toml members not updated"
        root_cargo.write_text(new_content)
        print("✓ Updated root Cargo.toml workspace members")
    
    def update_file_contents(self) -> None:
        """Update all file contents with new naming"""
        print("\n=== Phase 2: Content Updates ===")
        
        files_updated = 0
        processed_files = set()
        
        # Collect all files that need updates
        all_files_to_update = set()
        for pattern_files in self.validator.found_patterns.values():
            for rel_path_str, _ in pattern_files:
                all_files_to_update.add(rel_path_str)
        
        # Process each file only once, applying all necessary replacements
        for rel_path_str in all_files_to_update:
            file_path = self.root / rel_path_str
            
            # Skip if file was moved (update path)
            if not file_path.exists():
                # Try to find moved file
                for old_dir, new_dir in self.dir_mappings.items():
                    if rel_path_str.startswith(old_dir + '/'):
                        new_rel_path = rel_path_str.replace(old_dir + '/', new_dir + '/', 1)
                        file_path = self.root / new_rel_path
                        break
            
            if not file_path.exists():
                print(f"Warning: Cannot find file {rel_path_str} (may have been moved)")
                continue
            
            if str(file_path) in processed_files:
                continue
                
            processed_files.add(str(file_path))
            
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                # Apply replacements in order of specificity (longest first to avoid conflicts)
                ordered_replacements = [
                    ('tikv-jemallocator-global', 'jemallocatooor-global'),
                    ('tikv-jemallocator', 'jemallocatooor'),
                    ('tikv-jemalloc-ctl', 'jemallocatooor-ctl'),
                    ('tikv-jemalloc-sys', 'jemallocatooor-sys'),
                    ('tikv/jemallocator', 'sambacha/jemallocatooor'),
                    ('The TiKV Project Developers', 'sambacha'),
                    ('TiKV', 'jemallocatooor'),
                    ('tikv', 'jemallocatooor'),
                ]
                
                for old_pattern, new_pattern in ordered_replacements:
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                
                # Special handling for path references after directory moves
                for old_dir, new_dir in self.dir_mappings.items():
                    # Update relative path references like "../jemallocator"
                    content = content.replace(f'path = "../{old_dir}"', f'path = "../{new_dir}"')
                    content = content.replace(f'"../{old_dir}"', f'"../{new_dir}"')
                
                if content != original_content:
                    # Validate that the replacement actually improved things
                    tikv_count_before = len(re.findall(r'\b[Tt]ikv\b', original_content)) + \
                                       len(re.findall(r'\btikv-jemalloc\w*\b', original_content))
                    tikv_count_after = len(re.findall(r'\b[Tt]ikv\b', content)) + \
                                      len(re.findall(r'\btikv-jemalloc\w*\b', content))
                    
                    # Should have fewer TiKV references after replacement
                    assert tikv_count_after < tikv_count_before, \
                        f"Content replacement didn't reduce TiKV references in {file_path}"
                    
                    file_path.write_text(content, encoding='utf-8')
                    files_updated += 1
                    print(f"✓ Updated: {file_path.relative_to(self.root)} ({tikv_count_before}→{tikv_count_after} tikv refs)")
                    
            except (UnicodeDecodeError, PermissionError) as e:
                print(f"Warning: Could not update {file_path}: {e}")
        
        print(f"✓ Updated {files_updated} files")
    
    def validate_migration(self) -> None:
        """Validate the migration was successful"""
        print("\n=== Phase 3: Migration Validation ===")
        
        # Check that new directories exist
        for new_name in self.dir_mappings.values():
            new_path = self.root / new_name
            assert new_path.exists(), f"New directory not found: {new_name}"
            assert new_path.is_dir(), f"New path is not a directory: {new_name}"
        
        # Check that old directories don't exist
        for old_name in self.dir_mappings.keys():
            old_path = self.root / old_name
            assert not old_path.exists(), f"Old directory still exists: {old_name}"
        
        print("✓ Directory structure validation passed")
        
        # Scan for remaining TiKV patterns (should be minimal)
        remaining_patterns = {}
        extensions = {'.toml', '.rs', '.md', '.yml', '.yaml', '.sh'}
        
        # Look for any remaining TiKV references
        tikv_patterns = [
            re.compile(r'\btikv-jemalloc\w*\b'),
            re.compile(r'\b[Tt]ikv\b'),
            re.compile(r'TiKV'),
        ]
        
        for file_path in self.root.rglob('*'):
            if '.git' in file_path.parts or 'jemalloc/jemalloc' in str(file_path):
                continue
                
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    all_matches = []
                    for pattern in tikv_patterns:
                        matches = pattern.findall(content)
                        all_matches.extend(matches)
                    
                    if all_matches:
                        rel_path = file_path.relative_to(self.root)
                        remaining_patterns[str(rel_path)] = all_matches
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        if remaining_patterns:
            print("Warning: Some TiKV patterns may remain:")
            for file_path, patterns in remaining_patterns.items():
                print(f"  {file_path}: {patterns}")
        else:
            print("✓ No remaining TiKV patterns found")
        
        # Validate Cargo.toml files can be parsed
        cargo_files = list(self.root.rglob('Cargo.toml'))
        cargo_files = [f for f in cargo_files if 'jemalloc/jemalloc' not in str(f)]
        
        for cargo_file in cargo_files:
            try:
                # Basic validation - file should be readable and contain [package]
                content = cargo_file.read_text()
                if '[package]' in content or '[workspace]' in content:
                    continue
                else:
                    print(f"Warning: {cargo_file} may be malformed")
            except Exception as e:
                print(f"Warning: Could not validate {cargo_file}: {e}")
        
        print(f"✓ Validated {len(cargo_files)} Cargo.toml files")


def main():
    """Main migration orchestrator"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Migrate TiKV jemalloc project to jemallocatooor naming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./migrate_to_jemallocatooor.py                    # Standard migration
  ./migrate_to_jemallocatooor.py --ignore-dirty     # Ignore uncommitted changes
  ./migrate_to_jemallocatooor.py --help             # Show this help
        """
    )
    
    parser.add_argument(
        '--ignore-dirty',
        action='store_true',
        help='Ignore uncommitted changes in git working directory'
    )
    
    parser.add_argument(
        '--root-dir',
        type=str,
        help='Root directory of the project (default: script directory)'
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting TiKV to 'jemallocatooor' Migration")
    print("   Removing all TiKV branding → sambacha/jemallocatooor")
    if args.ignore_dirty:
        print("   ⚠️  Git dirty check disabled")
    print("=" * 55)
    
    # Determine root directory
    if args.root_dir:
        root_dir = Path(args.root_dir).resolve()
    else:
        script_dir = Path(__file__).parent
        root_dir = script_dir
    
    try:
        # Phase 0: Pre-flight validation
        print("\n=== Pre-flight Validation ===")
        validator = MigrationValidator(str(root_dir), ignore_dirty=args.ignore_dirty)
        validator.validate_git_repo()
        validator.validate_directory_structure()
        validator.scan_for_patterns()
        
        # Confirm with user
        print(f"\n📋 Migration Summary:")
        print(f"Root directory: {root_dir}")
        print(f"Directories to rename: {len(validator.expected_directories)}")
        print(f"Git dirty check: {'DISABLED' if args.ignore_dirty else 'ENABLED'}")
        
        total_pattern_files = sum(len(files) for files in validator.found_patterns.values())
        print(f"Files with TiKV patterns: {total_pattern_files}")
        
        response = input("\n⚠️  Proceed with migration? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration cancelled by user")
            return
        
        # Execute migration
        migrator = JemallocatooorMigrator(str(root_dir), validator)
        migrator.rename_directories()
        migrator.update_file_contents()
        migrator.validate_migration()
        
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Review changes: git status")
        print("2. Test build: cargo build")
        print("3. Run tests: cargo test")
        print("4. Commit changes: git add -A && git commit -m 'Rename to jemallocatooor'")
        
        if args.ignore_dirty:
            print("\n⚠️  Note: Git dirty check was disabled. Review all changes carefully.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nThe repository may be in an inconsistent state.")
        print("Consider running: git reset --hard HEAD")
        sys.exit(1)


if __name__ == '__main__':
    main()