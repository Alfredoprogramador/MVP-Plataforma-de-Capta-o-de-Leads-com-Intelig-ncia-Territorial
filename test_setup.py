#!/usr/bin/env python3
"""
Test script to verify the MVP setup
"""

import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from app.config import settings
        print("  ✓ Config imported")
        
        from app.database import Base, engine
        print("  ✓ Database imported")
        
        from app import models
        print("  ✓ Models imported")
        
        from app import schemas
        print("  ✓ Schemas imported")
        
        from app.services import whatsapp_service, ai_agent_service, proposal_service
        print("  ✓ Services imported")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_database():
    """Test database setup"""
    print("\nTesting database...")
    try:
        from app.database import Base, engine
        from app import models
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("  ✓ Database tables created")
        
        # Count tables
        table_count = len(Base.metadata.tables)
        print(f"  ✓ Found {table_count} tables")
        
        return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        return False


def test_models():
    """Test model definitions"""
    print("\nTesting models...")
    try:
        from app.database import Base
        from app import models
        
        model_classes = []
        for attr_name in dir(models):
            attr = getattr(models, attr_name)
            if isinstance(attr, type) and issubclass(attr, Base) and attr is not Base:
                model_classes.append(attr_name)
        
        print(f"  ✓ Found {len(model_classes)} models:")
        for model in sorted(model_classes):
            print(f"    - {model}")
        
        return True
    except Exception as e:
        print(f"  ✗ Model test failed: {e}")
        return False


def test_api():
    """Test API setup"""
    print("\nTesting API...")
    try:
        from app.main import app
        
        print(f"  ✓ App: {app.title}")
        print(f"  ✓ Version: {app.version}")
        
        # Count routes
        route_count = len([r for r in app.routes if hasattr(r, 'methods')])
        print(f"  ✓ Routes: {route_count}")
        
        return True
    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from app.config import settings
        
        print(f"  ✓ Database URL: {settings.DATABASE_URL[:50]}...")
        print(f"  ✓ Host: {settings.HOST}")
        print(f"  ✓ Port: {settings.PORT}")
        print(f"  ✓ Base URL: {settings.BASE_URL}")
        
        return True
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("MVP Lead Capture Platform - Setup Verification")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Models", test_models),
        ("API", test_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The MVP is ready to use.")
        print("\nNext steps:")
        print("  1. Configure API keys in .env file")
        print("  2. Run: docker-compose up -d")
        print("  3. Access: http://localhost:8000")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
