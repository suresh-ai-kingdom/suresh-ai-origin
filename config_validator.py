"""Environment configuration validator - ensures critical settings are present."""
import os
import sys


class ConfigValidator:
    """Validates environment configuration at startup."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def check_required(self, var_name, description):
        """Check if a required environment variable is set."""
        value = os.getenv(var_name)
        if not value:
            self.errors.append(f"Missing required: {var_name} ({description})")
        return value
    
    def check_optional(self, var_name, description, recommend=True):
        """Check if an optional environment variable is set."""
        value = os.getenv(var_name)
        if not value and recommend:
            self.warnings.append(f"Optional but recommended: {var_name} ({description})")
        return value
    
    def validate_production(self):
        """Validate production-critical settings."""
        flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true')
        
        if not flask_debug:
            # Production mode - enforce strict checks
            self.check_required('FLASK_SECRET_KEY', 'Flask session encryption key')
            self.check_optional('RAZORPAY_KEY_ID', 'Razorpay payment integration', recommend=True)
            self.check_optional('RAZORPAY_KEY_SECRET', 'Razorpay API secret', recommend=True)
            self.check_optional('RAZORPAY_WEBHOOK_SECRET', 'Razorpay webhook verification', recommend=True)
            self.check_optional('EMAIL_USER', 'SMTP email sender', recommend=True)
            self.check_optional('EMAIL_PASS', 'SMTP email password', recommend=True)
            
            # Session security
            secure = os.getenv('SESSION_COOKIE_SECURE', 'True').lower()
            if secure not in ('1', 'true', 'yes'):
                self.errors.append(
                    "SESSION_COOKIE_SECURE must be True in production (requires HTTPS)"
                )
    
    def validate_development(self):
        """Validate development settings."""
        flask_secret = os.getenv('FLASK_SECRET_KEY')
        if flask_secret == 'dev-secret':
            self.warnings.append(
                "Using default dev-secret - set FLASK_SECRET_KEY in production"
            )
    
    def validate(self, mode='auto'):
        """Run validation and return True if config is valid."""
        flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true')
        
        if mode == 'auto':
            mode = 'development' if flask_debug else 'production'
        
        if mode == 'production':
            self.validate_production()
        else:
            self.validate_development()
        
        # Report results
        if self.errors:
            print("❌ Configuration Errors:", file=sys.stderr)
            for error in self.errors:
                print(f"  - {error}", file=sys.stderr)
        
        if self.warnings:
            print("⚠️  Configuration Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Configuration validated successfully")
        
        return len(self.errors) == 0


def validate_config(strict=False):
    """Validate configuration and optionally exit on errors.
    
    Args:
        strict: If True, exit(1) when errors are found
    
    Returns:
        True if valid, False otherwise
    """
    validator = ConfigValidator()
    is_valid = validator.validate()
    
    if not is_valid and strict:
        print("\n❌ Fix configuration errors before starting the app.", file=sys.stderr)
        sys.exit(1)
    
    return is_valid


if __name__ == '__main__':
    # Allow running as standalone script
    strict_mode = '--strict' in sys.argv
    validate_config(strict=strict_mode)
