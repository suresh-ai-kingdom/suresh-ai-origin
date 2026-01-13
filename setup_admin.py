#!/usr/bin/env python3
"""
Setup Admin Credentials with Secure Hashing
Run this to generate secure admin password hash
"""
import os
import bcrypt
import secrets

def generate_secure_credentials():
    """Generate secure admin credentials."""
    print("\n" + "="*60)
    print("🔐 ADMIN CREDENTIALS SETUP")
    print("="*60)
    
    # Generate random username and password
    username = input("\nEnter admin username (or press Enter for 'admin'): ").strip() or "admin"
    
    print("\n📝 Password options:")
    print("1. Generate strong random password (recommended)")
    print("2. Enter your own password")
    choice = input("\nChoice (1 or 2): ").strip()
    
    if choice == "1":
        # Generate strong random password
        password = secrets.token_urlsafe(16)
        print(f"\n✅ Generated password: {password}")
        print("⚠️  SAVE THIS PASSWORD! You won't see it again.")
    else:
        password = input("\nEnter password: ").strip()
        if len(password) < 8:
            print("❌ Password must be at least 8 characters!")
            return
    
    # Hash password with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    hash_string = password_hash.decode('utf-8')
    
    print("\n" + "="*60)
    print("✅ CREDENTIALS GENERATED!")
    print("="*60)
    print("\n📋 Add these to Render Environment Variables:")
    print("\n" + "-"*60)
    print(f"ADMIN_USERNAME={username}")
    print(f"ADMIN_PASSWORD_HASH={hash_string}")
    print("-"*60)
    
    print("\n💡 For local testing, add to .env file:")
    print("-"*60)
    print(f"ADMIN_USERNAME={username}")
    print(f"ADMIN_PASSWORD={password}")
    print("-"*60)
    
    # Optionally write to .env
    update_env = input("\n❓ Update .env file? (y/n): ").lower()
    if update_env == 'y':
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Read existing .env
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = [line for line in f.readlines() 
                            if not line.startswith('ADMIN_USERNAME=') 
                            and not line.startswith('ADMIN_PASSWORD=')
                            and not line.startswith('ADMIN_PASSWORD_HASH=')]
        
        # Add new credentials
        env_lines.append(f"\n# Admin Credentials (generated {os.popen('date /t').read().strip()})\n")
        env_lines.append(f"ADMIN_USERNAME={username}\n")
        env_lines.append(f"ADMIN_PASSWORD={password}\n")
        env_lines.append(f"ADMIN_PASSWORD_HASH={hash_string}\n")
        
        with open(env_path, 'w') as f:
            f.writelines(env_lines)
        
        print(f"✅ Updated {env_path}")
    
    print("\n🚀 Next steps:")
    print("1. Add variables to Render Dashboard → Environment")
    print("2. Restart app on Render")
    print("3. Test login at /admin/login")
    print("="*60)

if __name__ == "__main__":
    generate_secure_credentials()
