#!/usr/bin/env python3
"""Database backup utility - creates timestamped backups of the SQLite database."""
import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path


def get_db_path():
    """Get the database path from environment or default."""
    return os.getenv('DATA_DB', 'data.db')


def get_backup_dir():
    """Get or create the backups directory."""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def create_backup(db_path=None, backup_dir=None):
    """Create a timestamped backup of the database.
    
    Args:
        db_path: Path to database file (default: from env or data.db)
        backup_dir: Directory to store backups (default: ./backups/)
    
    Returns:
        Path to the backup file
    """
    if db_path is None:
        db_path = get_db_path()
    
    if backup_dir is None:
        backup_dir = get_backup_dir()
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"data_backup_{timestamp}.db"
    backup_path = backup_dir / backup_name
    
    # Copy database file
    shutil.copy2(db_path, backup_path)
    
    # Get file size for reporting
    size_mb = backup_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ Backup created: {backup_path}")
    print(f"   Size: {size_mb:.2f} MB")
    
    return backup_path


def list_backups(backup_dir=None):
    """List all available backups.
    
    Args:
        backup_dir: Directory containing backups (default: ./backups/)
    
    Returns:
        List of backup file paths sorted by date (newest first)
    """
    if backup_dir is None:
        backup_dir = get_backup_dir()
    
    backups = sorted(
        backup_dir.glob('data_backup_*.db'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not backups:
        print("No backups found.")
        return []
    
    print(f"\n📦 Available backups in {backup_dir}:")
    print("-" * 70)
    
    for i, backup in enumerate(backups, 1):
        stat = backup.stat()
        size_mb = stat.st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        age = datetime.now() - mtime
        
        age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds // 3600}h"
        
        print(f"{i:2}. {backup.name:30} {size_mb:6.2f} MB  {age_str:>5} ago  {mtime:%Y-%m-%d %H:%M}")
    
    print("-" * 70)
    return backups


def cleanup_old_backups(keep_count=10, backup_dir=None):
    """Remove old backups, keeping only the most recent ones.
    
    Args:
        keep_count: Number of recent backups to keep
        backup_dir: Directory containing backups (default: ./backups/)
    
    Returns:
        Number of backups deleted
    """
    if backup_dir is None:
        backup_dir = get_backup_dir()
    
    backups = sorted(
        backup_dir.glob('data_backup_*.db'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if len(backups) <= keep_count:
        print(f"✅ Only {len(backups)} backups exist, nothing to clean up.")
        return 0
    
    old_backups = backups[keep_count:]
    
    for backup in old_backups:
        backup.unlink()
        print(f"🗑️  Deleted old backup: {backup.name}")
    
    print(f"✅ Cleaned up {len(old_backups)} old backup(s), kept {keep_count} most recent.")
    return len(old_backups)


def restore_backup(backup_name=None, db_path=None, backup_dir=None, force=False):
    """Restore database from a backup file.
    
    Args:
        backup_name: Name of backup file to restore (default: most recent)
        db_path: Target database path (default: from env or data.db)
        backup_dir: Directory containing backups (default: ./backups/)
        force: Skip confirmation prompt
    
    Returns:
        True if restored successfully
    """
    if db_path is None:
        db_path = get_db_path()
    
    if backup_dir is None:
        backup_dir = get_backup_dir()
    
    db_path = Path(db_path)
    
    # Find backup to restore
    if backup_name is None:
        # Get most recent backup
        backups = sorted(
            backup_dir.glob('data_backup_*.db'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if not backups:
            print("❌ No backups found.")
            return False
        backup_path = backups[0]
        print(f"📦 Using most recent backup: {backup_path.name}")
    else:
        backup_path = backup_dir / backup_name
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False
    
    # Confirm before overwriting
    if not force and db_path.exists():
        print(f"\n⚠️  WARNING: This will overwrite {db_path}")
        print(f"   Current size: {db_path.stat().st_size / (1024 * 1024):.2f} MB")
        print(f"   Backup size:  {backup_path.stat().st_size / (1024 * 1024):.2f} MB")
        response = input("\nContinue? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("❌ Restore cancelled.")
            return False
    
    # Create a safety backup of current database
    if db_path.exists():
        safety_backup = db_path.parent / f"{db_path.stem}_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, safety_backup)
        print(f"🔒 Safety backup created: {safety_backup.name}")
    
    # Restore the backup
    shutil.copy2(backup_path, db_path)
    print(f"✅ Database restored from: {backup_path.name}")
    print(f"   Restored to: {db_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Database backup utility')
    parser.add_argument('action', choices=['create', 'list', 'cleanup', 'restore'], 
                       help='Action to perform')
    parser.add_argument('--keep', type=int, default=10,
                       help='Number of backups to keep during cleanup (default: 10)')
    parser.add_argument('--backup', type=str,
                       help='Backup file name to restore (default: most recent)')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'create':
            create_backup()
        elif args.action == 'list':
            list_backups()
        elif args.action == 'cleanup':
            cleanup_old_backups(keep_count=args.keep)
        elif args.action == 'restore':
            restore_backup(backup_name=args.backup, force=args.force)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
