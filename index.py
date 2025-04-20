#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import argparse
import hashlib
from datetime import datetime

# File type categorization
FILE_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".xlsx", ".pptx", ".odt", ".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".php", ".sh", ".json", ".xml"],
    "Torrents": [".torrent"],
    "DiskImages": [".iso", ".img"],
}

def get_file_category(extension):
    """Determine the category for a file based on its extension"""
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "Other"

def calculate_file_hash(filepath):
    """Calculate MD5 hash of a file for duplicate detection"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def organize_files(source_dir, dry_run=False, remove_duplicates=False):
    """Main function to organize files"""
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
    
    stats = {
        "total_files": 0,
        "moved": 0,
        "duplicates": 0,
        "errors": 0,
        "categories": {category: 0 for category in FILE_CATEGORIES.keys()}
    }
    stats["categories"]["Other"] = 0
    
    seen_hashes = set()
    
    for item in source_path.glob("*"):
        if item.is_dir():
            continue  # Skip directories
            
        stats["total_files"] += 1
        file_ext = item.suffix
        category = get_file_category(file_ext)
        
        try:
            file_hash = calculate_file_hash(item) if remove_duplicates else None
            
            if remove_duplicates and file_hash in seen_hashes:
                stats["duplicates"] += 1
                if not dry_run:
                    item.unlink()
                print(f"Duplicate removed: {item.name}")
                continue
                
            seen_hashes.add(file_hash) if remove_duplicates else None
            
            dest_dir = source_path / category
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
                
            new_path = dest_dir / item.name
            
            if dry_run:
                print(f"[Dry Run] Would move: {item.name} -> {category}/{item.name}")
            else:
                shutil.move(str(item), str(new_path))
                print(f"Moved: {item.name} -> {category}/{item.name}")
                
            stats["moved"] += 1
            stats["categories"][category] += 1
            
        except Exception as e:
            stats["errors"] += 1
            print(f"Error processing {item.name}: {str(e)}")
    
    # Generate report
    print("\n=== Organization Complete ===")
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files moved: {stats['moved']}")
    print(f"Duplicates removed: {stats['duplicates']}")
    print(f"Errors encountered: {stats['errors']}")
    print("\nFile distribution by category:")
    for category, count in stats["categories"].items():
        if count > 0:
            print(f"- {category}: {count} files")

def main():
    parser = argparse.ArgumentParser(
        description="File Organizer Pro - Automatically organize your files into categories.",
        epilog="Example: file_organizer.py ~/Downloads --remove-duplicates"
    )
    parser.add_argument(
        "directory",
        help="Directory to organize (default: current directory)",
        nargs="?",
        default=os.getcwd()
    )
    parser.add_argument(
        "--dry-run",
        help="Simulate organization without actually moving files",
        action="store_true"
    )
    parser.add_argument(
        "--remove-duplicates",
        help="Detect and remove duplicate files",
        action="store_true"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="File Organizer Pro 2.0"
    )
    
    args = parser.parse_args()
    
    print(f"\nFile Organizer Pro - Organizing: {args.directory}")
    if args.dry_run:
        print("Running in dry-run mode (no changes will be made)")
    if args.remove_duplicates:
        print("Duplicate detection enabled")
    
    organize_files(args.directory, args.dry_run, args.remove_duplicates)

if __name__ == "__main__":
    main()
