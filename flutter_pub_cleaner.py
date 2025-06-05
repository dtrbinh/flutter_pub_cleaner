#!/usr/bin/env python3
import os
import subprocess
import sys

def get_folder_size(folder_path):
    """
    Calculate the total size of a folder and all its contents in bytes
    """
    total_size = 0
    try:
        # Walk through all files and subdirectories
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    # Get file size and add to total
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue
    except (OSError, PermissionError):
        # Return 0 if we can't access the folder
        pass
    
    return total_size

def format_size(size_bytes):
    """
    Convert bytes to human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    # Define size units
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    # Convert to appropriate unit
    while size >= 1024.0 and unit_index < len(size_units) - 1:
        size /= 1024.0
        unit_index += 1
    
    # Format with appropriate decimal places
    if unit_index == 0:  # Bytes
        return f"{int(size)} {size_units[unit_index]}"
    else:
        return f"{size:.2f} {size_units[unit_index]}"

def is_flutter_project(folder_path):
    """
    Check if a folder is a Flutter project by looking for pubspec.yaml
    """
    pubspec_path = os.path.join(folder_path, "pubspec.yaml")
    return os.path.exists(pubspec_path)

def clean_flutter_project(project_path, use_fvm=True):
    """
    Execute Flutter clean command in the given Flutter project directory
    and return size information before and after cleaning
    """
    project_name = os.path.basename(project_path)
    command_name = "fvm flutter clean" if use_fvm else "flutter clean"
    
    try:
        print(f"🧹 Cleaning Flutter project: {project_name}")
        
        # Calculate size before cleaning
        print("  📏 Calculating folder size before cleaning...")
        size_before = get_folder_size(project_path)
        print(f"  📊 Size before: {format_size(size_before)}")
        
        # Prepare command based on FVM preference
        if use_fvm:
            command = ["fvm", "flutter", "clean"]
        else:
            command = ["flutter", "clean"]
        
        # Execute flutter clean
        print(f"  🔧 Running: {command_name}")
        result = subprocess.run(
            command,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Calculate size after cleaning
        print("  📏 Calculating folder size after cleaning...")
        size_after = get_folder_size(project_path)
        size_saved = size_before - size_after
        
        print(f"  📊 Size after: {format_size(size_after)}")
        print(f"  💾 Space saved: {format_size(size_saved)}")
        
        if result.stdout.strip():
            print(f"  📝 Flutter output: {result.stdout.strip()}")
        
        print(f"  ✅ Successfully cleaned: {project_name}")
        
        return {
            'success': True,
            'size_before': size_before,
            'size_after': size_after,
            'size_saved': size_saved
        }
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error cleaning {project_name}: {e}")
        if e.stderr:
            print(f"  Error details: {e.stderr.strip()}")
        return {
            'success': False,
            'size_before': 0,
            'size_after': 0,
            'size_saved': 0
        }
    except FileNotFoundError:
        if use_fvm:
            print("  ❌ 'fvm' command not found. Please make sure FVM is installed and in your PATH.")
        else:
            print("  ❌ 'flutter' command not found. Please make sure Flutter SDK is installed and in your PATH.")
        return {
            'success': False,
            'size_before': 0,
            'size_after': 0,
            'size_saved': 0
        }

def ask_fvm_preference():
    """
    Ask user if they want to use FVM or regular Flutter
    """
    print("🔧 Flutter Version Management")
    print("-" * 40)
    print("Do you want to use FVM (Flutter Version Management) or regular Flutter?")
    print("1. Use FVM (fvm flutter clean)")
    print("2. Use regular Flutter (flutter clean)")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            print("✅ Using FVM for Flutter commands")
            return True
        elif choice == "2":
            print("✅ Using regular Flutter commands")
            return False
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

def scan_and_clean_flutter_projects():
    """
    Prompts user for a parent folder path, scans all subdirectories for Flutter projects,
    and executes Flutter clean on each Flutter project found with size tracking.
    """
    try:
        # Ask about FVM preference first
        use_fvm = ask_fvm_preference()
        print()
        
        # Get folder path from user input
        parent_folder = input("Enter the parent folder path containing Flutter projects: ").strip()
        
        # Handle empty input
        if not parent_folder:
            print("❌ No folder path provided.")
            return
        
        # Expand user path (~ symbol) and resolve absolute path
        parent_folder = os.path.expanduser(parent_folder)
        parent_folder = os.path.abspath(parent_folder)
        
        # Check if the parent folder exists
        if not os.path.exists(parent_folder):
            print(f"❌ Folder does not exist: {parent_folder}")
            return
        
        if not os.path.isdir(parent_folder):
            print(f"❌ Path is not a directory: {parent_folder}")
            return
        
        print(f"🔍 Scanning for Flutter projects in: {parent_folder}")
        print("-" * 60)
        
        flutter_projects = []
        
        try:
            # Get all items in the parent folder
            items = os.listdir(parent_folder)
            
            # Check each item to see if it's a directory and contains pubspec.yaml
            for item in items:
                item_path = os.path.join(parent_folder, item)
                
                # Skip if it's not a directory
                if not os.path.isdir(item_path):
                    continue
                
                # Skip hidden directories (starting with .)
                if item.startswith('.'):
                    continue
                
                # Check if it's a Flutter project
                if is_flutter_project(item_path):
                    flutter_projects.append(item_path)
                    print(f"📱 Found Flutter project: {item}")
        
        except PermissionError:
            print(f"❌ Permission denied accessing: {parent_folder}")
            return
        
        if not flutter_projects:
            print("❌ No Flutter projects found in the specified folder.")
            return
        
        print(f"\n🎯 Found {len(flutter_projects)} Flutter project(s)")
        print("-" * 60)
        
        # Show which command will be used
        command_description = "fvm flutter clean" if use_fvm else "flutter clean"
        print(f"📋 Command to execute: {command_description}")
        
        # Ask for confirmation
        response = input(f"Do you want to run '{command_description}' on all {len(flutter_projects)} project(s)? (y/N): ").strip().lower()
        
        if response not in ['y', 'yes']:
            print("⏹️  Operation cancelled.")
            return
        
        print("\n🚀 Starting cleanup process...")
        print("-" * 60)
        
        # Track statistics
        successful_cleans = 0
        failed_cleans = 0
        total_size_before = 0
        total_size_after = 0
        total_size_saved = 0
        
        # Clean each Flutter project
        for i, project_path in enumerate(flutter_projects, 1):
            print(f"\n[{i}/{len(flutter_projects)}] Processing project...")
            result = clean_flutter_project(project_path, use_fvm)
            
            if result['success']:
                successful_cleans += 1
            else:
                failed_cleans += 1
            
            # Add to totals
            total_size_before += result['size_before']
            total_size_after += result['size_after']
            total_size_saved += result['size_saved']
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📊 CLEANUP SUMMARY")
        print("=" * 80)
        print(f"🔧 Command used: {command_description}")
        print(f"✅ Successfully cleaned: {successful_cleans} project(s)")
        if failed_cleans > 0:
            print(f"❌ Failed to clean: {failed_cleans} project(s)")
        print(f"📱 Total Flutter projects: {len(flutter_projects)}")
        print("-" * 80)
        print("💾 SPACE USAGE SUMMARY")
        print("-" * 80)
        print(f"📏 Total size before cleaning: {format_size(total_size_before)}")
        print(f"📏 Total size after cleaning:  {format_size(total_size_after)}")
        print(f"🎉 Total space saved:          {format_size(total_size_saved)}")
        
        if total_size_before > 0:
            percentage_saved = (total_size_saved / total_size_before) * 100
            print(f"📈 Space reduction:            {percentage_saved:.1f}%")
        
        print("=" * 80)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("🎯 Flutter Projects Batch Cleaner with Size Tracking")
    print("This script will scan a folder for Flutter projects, run Flutter clean on each one,")
    print("and show you how much space is saved!")
    print("=" * 90)
    scan_and_clean_flutter_projects()
