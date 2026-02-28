#!/usr/bin/env python
"""
Quick setup script for RetroNetwork development environment.
Run this after cloning the repository.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e}")
        return False


def main():
    """Run all setup steps."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           RetroNetwork Development Setup                   ║
    ║                                                            ║
    ║  This script will set up your development environment     ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    base_dir = Path(__file__).parent
    
    # Check if virtual environment exists
    venv_path = base_dir / 'venv'
    if not venv_path.exists():
        print("\n⚠️  Virtual environment not found.")
        print("Create one with: python -m venv venv")
        print("Then activate it before running this script.")
        sys.exit(1)
    
    print("✅ Virtual environment found\n")
    
    # Determine pip executable
    if sys.platform == "win32":
        pip_cmd = [str(venv_path / "Scripts" / "pip")]
        python_cmd = [str(venv_path / "Scripts" / "python")]
    else:
        pip_cmd = [str(venv_path / "bin" / "pip")]
        python_cmd = [str(venv_path / "bin" / "python")]
    
    steps = [
        (pip_cmd + ["install", "--upgrade", "pip"], "Upgrading pip"),
        (pip_cmd + ["install", "-r", "requirements.txt"], "Installing dependencies"),
        (python_cmd + ["manage.py", "migrate"], "Running migrations"),
        (python_cmd + ["manage.py", "collectstatic", "--noinput"], "Collecting static files"),
    ]
    
    failed_steps = []
    for cmd, description in steps:
        if not run_command(cmd, description):
            failed_steps.append(description)
    
    # Setup environment if needed
    env_file = base_dir / ".env"
    if not env_file.exists():
        print("\n📝 Creating .env file from .env.example...")
        with open(base_dir / ".env.example") as src:
            with open(env_file, "w") as dst:
                dst.write(src.read())
        print("✅ .env created - please review and customize")
    
    # Create logs directory
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Logs directory created: {logs_dir}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Setup Summary")
    print("="*60)
    
    if failed_steps:
        print(f"\n❌ Failed steps ({len(failed_steps)}):")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease fix these issues manually.")
        sys.exit(1)
    
    print("\n✅ All setup steps completed successfully!\n")
    
    print("📋 Next steps:")
    print("  1. Review and edit .env file with your settings")
    print("  2. Generate SECRET_KEY:")
    print("     python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"")
    print("  3. Create superuser: python manage.py createsuperuser")
    print("  4. Start development server: python manage.py runserver")
    print("  5. Visit http://localhost:8000 in your browser\n")
    
    print("📚 Documentation:")
    print("  - README.md - Project overview and features")
    print("  - SECURITY.md - Security configuration and guidelines")
    print("  - DEPLOYMENT.md - Production deployment checklist")
    print("  - FIXES_APPLIED.md - Summary of improvements\n")
    
    print("💡 Tips:")
    print("  - Run 'python manage.py --help' for Django commands")
    print("  - Run tests with: python manage.py test")
    print("  - Check logs in: logs/django.log\n")


if __name__ == "__main__":
    main()
