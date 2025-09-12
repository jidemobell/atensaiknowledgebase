#!/usr/bin/env python3
"""
Test script for Enhanced AI-Powered Support System
Tests the API endpoints without needing frontend
"""

import sys
import requests
import json
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

BASE_URL = "http://localhost:8000"

def test_health():
    """Test basic health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False

def test_status():
    """Test system status endpoint"""
    print("\n🔍 Testing system status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ System status retrieved")
            print(f"   Embeddings available: {status.get('embeddings_available', False)}")
            print(f"   Vector store: {status.get('vector_store_status', {}).get('status', 'unknown')}")
            print(f"   Knowledge base cases: {status.get('knowledge_base_cases', 0)}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status test error: {e}")
        return False

def test_load_samples():
    """Load sample cases"""
    print("\n🔍 Loading sample cases...")
    try:
        response = requests.post(f"{BASE_URL}/cases/load_samples")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sample cases loaded: {result.get('message', 'Unknown result')}")
            return True
        else:
            print(f"❌ Sample loading failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Sample loading error: {e}")
        return False

def test_diagnostic_query():
    """Test diagnostic query"""
    print("\n🔍 Testing diagnostic queries...")
    
    test_queries = [
        "topology-merge service is timing out after 30 seconds",
        "cassandra database connection failed",
        "high cpu usage in observer services",
        "kafka consumer lag detected"
    ]
    
    success_count = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence', 0)
                hypotheses_count = len(result.get('hypotheses', []))
                similar_cases_count = len(result.get('similar_cases', []))
                similar_docs_count = len(result.get('similar_documents', []))
                
                print(f"   ✅ Confidence: {confidence:.2%}")
                print(f"      Hypotheses: {hypotheses_count}")
                print(f"      Similar cases: {similar_cases_count}")
                print(f"      Similar documents: {similar_docs_count}")
                print(f"      Data sources: {result.get('data_sources', {})}")
                
                success_count += 1
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                print(f"      Error: {response.text}")
        
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    print(f"\n📊 Query test results: {success_count}/{len(test_queries)} successful")
    return success_count == len(test_queries)

def test_case_management():
    """Test case management endpoints"""
    print("\n🔍 Testing case management...")
    
    try:
        # List cases
        response = requests.get(f"{BASE_URL}/cases/list")
        if response.status_code == 200:
            cases = response.json()
            case_count = cases.get('count', 0)
            print(f"✅ Cases listed: {case_count} total cases")
            
            # Test getting a specific case if any exist
            if case_count > 0 and cases.get('cases'):
                first_case_id = cases['cases'][0].get('id')
                if first_case_id:
                    case_response = requests.get(f"{BASE_URL}/cases/{first_case_id}")
                    if case_response.status_code == 200:
                        case_data = case_response.json()
                        doc_count = case_data.get('document_count', 0)
                        print(f"✅ Retrieved case {first_case_id} with {doc_count} documents")
                    else:
                        print(f"❌ Failed to retrieve case {first_case_id}")
            
            return True
        else:
            print(f"❌ Case listing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Case management error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced AI-Powered Support System - Test Suite")
    print("=" * 60)
    
    # Check if server is running
    if not test_health():
        print("\n❌ Server is not running. Please start it first with:")
        print("   ./start.sh")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_status,
        test_load_samples,
        test_case_management,
        test_diagnostic_query
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your enhanced system is working correctly.")
        print("\n🌟 Try these next steps:")
        print("   1. Open http://localhost:8000/docs to explore the API")
        print("   2. Upload documents via /documents/ingest")
        print("   3. Try semantic search with /documents/search")
        print("   4. Build a React frontend to interact with the API")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
