#!/usr/bin/env python3
"""PostgreSQL migration script - migrates data from SQLite to PostgreSQL."""

import sys
import os
import argparse
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Base
from utils import init_db


def migrate_data(source_url: str, target_url: str, dry_run: bool = False):
    """Migrate all data from source to target database."""
    print(f"{'🔍 DRY RUN - ' if dry_run else ''}Migrating data...")
    print(f"  Source: {source_url[:50]}...")
    print(f"  Target: {target_url[:50]}...\n")
    
    # Connect to both databases
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    # Create all tables in target
    if not dry_run:
        Base.metadata.create_all(target_engine)
        print("✅ Created target schema\n")
    
    # Get sessions
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    source_session = SourceSession()
    target_session = TargetSession()
    
    # Get all tables
    inspector = inspect(source_engine)
    tables = inspector.get_table_names()
    
    total_rows = 0
    
    for table_name in tables:
        if table_name.startswith('alembic_'):
            # Skip Alembic internal tables
            continue
        
        # Count rows in source
        result = source_session.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = result.scalar()
        
        print(f"📦 {table_name}: {row_count} rows", end='')
        
        if dry_run:
            print(" (skipped - dry run)")
            total_rows += row_count
            continue
        
        # Get table object
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=source_engine)
        
        # Copy rows
        rows = source_session.execute(table.select()).fetchall()
        
        if rows:
            # Insert into target
            target_session.execute(table.insert(), [dict(row._mapping) for row in rows])
            target_session.commit()
            print(" ✅")
        else:
            print(" (empty)")
        
        total_rows += row_count
    
    source_session.close()
    target_session.close()
    
    print(f"\n{'Would migrate' if dry_run else 'Migrated'} {total_rows} total rows across {len(tables)} tables")
    
    return total_rows


def verify_migration(source_url: str, target_url: str):
    """Verify that migration completed successfully."""
    print("🔍 Verifying migration...\n")
    
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    source_session = SourceSession()
    target_session = TargetSession()
    
    inspector = inspect(source_engine)
    tables = [t for t in inspector.get_table_names() if not t.startswith('alembic_')]
    
    all_match = True
    
    for table_name in tables:
        source_count = source_session.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
        target_count = target_session.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
        
        match = source_count == target_count
        icon = "✅" if match else "❌"
        
        print(f"{icon} {table_name}: {source_count} → {target_count}")
        
        if not match:
            all_match = False
    
    source_session.close()
    target_session.close()
    
    if all_match:
        print("\n✅ Migration verified successfully!")
    else:
        print("\n❌ Migration verification failed - row counts don't match")
    
    return all_match


def main():
    parser = argparse.ArgumentParser(description='Migrate from SQLite to PostgreSQL')
    parser.add_argument('--source', default='sqlite:///data.db', help='Source database URL')
    parser.add_argument('--target', help='Target database URL (required for migration)')
    parser.add_argument('--dry-run', action='store_true', help='Test migration without changes')
    parser.add_argument('--verify', action='store_true', help='Verify existing migration')
    
    args = parser.parse_args()
    
    if args.verify:
        if not args.target:
            print("❌ --target required for verification")
            return 1
        success = verify_migration(args.source, args.target)
        return 0 if success else 1
    
    if not args.target:
        print("❌ --target required for migration")
        print("Usage: python migrate_to_postgresql.py --target postgresql://user:pass@host:5432/db")
        return 1
    
    # Confirm before migrating
    if not args.dry_run:
        print("⚠️  WARNING: This will copy all data to the target database.")
        print("   Existing data in target will NOT be deleted first.")
        print("\nContinue? (yes/no): ", end='')
        response = input().lower()
        if response not in ('yes', 'y'):
            print("❌ Migration cancelled")
            return 0
    
    try:
        migrate_data(args.source, args.target, dry_run=args.dry_run)
        
        if not args.dry_run:
            print("\n🔍 Running verification...")
            verify_migration(args.source, args.target)
        
        return 0
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
