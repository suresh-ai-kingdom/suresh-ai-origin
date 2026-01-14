#!/usr/bin/env python3
"""
Automated Backup System - SURESH AI ORIGIN
Scheduled backups with retention policy and restore verification
"""

import os
import shutil
import time
import sqlite3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class BackupManager:
    def __init__(self):
        self.db_path = 'data.db'
        self.backup_dir = 'backups'
        self.retention_days = 30  # Keep backups for 30 days
        self.daily_backups = 7    # Keep 7 daily backups
        self.weekly_backups = 4   # Keep 4 weekly backups
        
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, backup_type='manual'):
        """Create a database backup."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{backup_type}_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy database file
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                size_mb = os.path.getsize(backup_path) / (1024 * 1024)
                
                logging.info(f"✅ Backup created: {backup_name} ({size_mb:.2f} MB)")
                
                # Verify backup integrity
                if self.verify_backup(backup_path):
                    logging.info(f"✅ Backup verified: {backup_name}")
                    return backup_path
                else:
                    logging.error(f"❌ Backup verification failed: {backup_name}")
                    os.remove(backup_path)
                    return None
            else:
                logging.error(f"❌ Database not found: {self.db_path}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Backup failed: {e}")
            return None
    
    def verify_backup(self, backup_path):
        """Verify backup file integrity."""
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check if main tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['orders', 'payments', 'subscriptions', 'customers']
            missing = [t for t in required_tables if t not in tables]
            
            if missing:
                logging.warning(f"⚠️  Missing tables in backup: {missing}")
                # Don't fail - might be a new database
            
            # Try a simple query
            cursor.execute("SELECT COUNT(*) FROM orders")
            count = cursor.fetchone()[0]
            logging.info(f"   Orders in backup: {count}")
            
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ Verification failed: {e}")
            return False
    
    def restore_backup(self, backup_path):
        """Restore database from backup."""
        try:
            if not os.path.exists(backup_path):
                logging.error(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Verify backup before restoring
            if not self.verify_backup(backup_path):
                logging.error(f"❌ Cannot restore corrupted backup: {backup_path}")
                return False
            
            # Create backup of current database
            if os.path.exists(self.db_path):
                pre_restore_backup = self.db_path + '.pre_restore'
                shutil.copy2(self.db_path, pre_restore_backup)
                logging.info(f"💾 Current DB backed up to: {pre_restore_backup}")
            
            # Restore
            shutil.copy2(backup_path, self.db_path)
            logging.info(f"✅ Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Restore failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period."""
        try:
            now = datetime.now()
            cutoff = now - timedelta(days=self.retention_days)
            removed = 0
            
            for filename in os.listdir(self.backup_dir):
                if not filename.startswith('backup_'):
                    continue
                
                filepath = os.path.join(self.backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff:
                    os.remove(filepath)
                    removed += 1
                    logging.info(f"🗑️  Removed old backup: {filename}")
            
            if removed > 0:
                logging.info(f"✅ Cleaned up {removed} old backup(s)")
            else:
                logging.info(f"✅ No old backups to remove")
                
        except Exception as e:
            logging.error(f"❌ Cleanup failed: {e}")
    
    def list_backups(self):
        """List all available backups."""
        try:
            backups = []
            for filename in sorted(os.listdir(self.backup_dir), reverse=True):
                if filename.startswith('backup_') and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    backups.append({
                        'name': filename,
                        'path': filepath,
                        'size_mb': size_mb,
                        'created': mtime
                    })
            
            return backups
            
        except Exception as e:
            logging.error(f"❌ Failed to list backups: {e}")
            return []
    
    def get_latest_backup(self):
        """Get the most recent backup."""
        backups = self.list_backups()
        return backups[0] if backups else None

def main():
    import sys
    
    manager = BackupManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_manager.py create [type]  - Create backup (type: manual/hourly/daily/weekly)")
        print("  python backup_manager.py restore <file> - Restore from backup")
        print("  python backup_manager.py list           - List all backups")
        print("  python backup_manager.py cleanup        - Remove old backups")
        print("  python backup_manager.py auto           - Run automatic backup")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        backup_type = sys.argv[2] if len(sys.argv) > 2 else 'manual'
        result = manager.create_backup(backup_type)
        sys.exit(0 if result else 1)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Error: Backup file required")
            sys.exit(1)
        backup_file = sys.argv[2]
        result = manager.restore_backup(backup_file)
        sys.exit(0 if result else 1)
    
    elif command == 'list':
        backups = manager.list_backups()
        if backups:
            print(f"\n{'='*80}")
            print(f"Available Backups ({len(backups)} total)")
            print(f"{'='*80}")
            for i, backup in enumerate(backups, 1):
                print(f"\n{i}. {backup['name']}")
                print(f"   Size: {backup['size_mb']:.2f} MB")
                print(f"   Created: {backup['created']}")
                print(f"   Path: {backup['path']}")
            print()
        else:
            print("No backups found")
    
    elif command == 'cleanup':
        manager.cleanup_old_backups()
    
    elif command == 'auto':
        # Automatic backup with cleanup
        logging.info("🔄 Starting automatic backup...")
        result = manager.create_backup('auto')
        if result:
            manager.cleanup_old_backups()
            logging.info("✅ Automatic backup complete")
            sys.exit(0)
        else:
            logging.error("❌ Automatic backup failed")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
