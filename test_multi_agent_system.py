#!/usr/bin/env python3
"""
Multi-Agent System Test Script - Phase 2 Validation
Test agent coordination, cross-validation, and dynamic source selection
"""

import asyncio
import json
import time
from typing import Dict, Any, List

# Test queries with different complexity levels
TEST_QUERIES = [
    {
        "name": "Simple Topology Query",
        "query": "What is nasm-topology service?",
        "expected_agents": ["asm_topology_expert"],
        "complexity": "low"
    },
    {
        "name": "Multi-Domain Query", 
        "query": "How do I troubleshoot connectivity issues between nasm-topology and merge-service, and are there similar cases in the support database?",
        "expected_agents": ["asm_topology_expert", "case_analysis_expert"],
        "complexity": "high"
    },
    {
        "name": "Case Analysis Query",
        "query": "I have a production outage with service unavailable errors",
        "expected_agents": ["case_analysis_expert", "asm_topology_expert"],
        "complexity": "medium"
    },
    {
        "name": "GitHub Repository Query",
        "query": "Show me configuration examples and documentation for ASM topology setup",
        "expected_agents": ["github_source_expert", "asm_topology_expert"],
        "complexity": "medium"
    },
    {
        "name": "Cross-Validation Query",
        "query": "Compare topology configuration best practices from multiple sources and validate consistency",
        "expected_agents": ["asm_topology_expert", "github_source_expert", "case_analysis_expert"],
        "complexity": "high"
    }
]

class MultiAgentTester:
    """Test harness for multi-agent system validation"""
    
    def __init__(self):
        self.results = []
        self.orchestrator = None
        
    async def initialize_system(self):
        """Initialize the multi-agent system"""
        try:
            from multi_agent_orchestrator import create_multi_agent_system
            self.orchestrator = create_multi_agent_system()
            print("✅ Multi-Agent System initialized for testing")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Multi-Agent System: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all test queries"""
        print("🧪 Starting Multi-Agent System Validation Tests\n")
        
        if not await self.initialize_system():
            return False
        
        for i, test_case in enumerate(TEST_QUERIES, 1):
            print(f"Test {i}/{len(TEST_QUERIES)}: {test_case['name']}")
            print(f"Query: {test_case['query']}")
            print(f"Expected Complexity: {test_case['complexity']}")
            print("-" * 80)
            
            result = await self.run_single_test(test_case)
            self.results.append(result)
            
            print(f"✅ Test completed in {result['processing_time']:.2f}s")
            print(f"Confidence: {result['confidence']:.1%}")
            print(f"Agents Used: {', '.join(result['agents_used'])}")
            print("\n")
        
        self.print_summary()
        return True
    
    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        
        start_time = time.time()
        
        # Create test context
        context = {
            "test_mode": True,
            "expected_agents": test_case["expected_agents"],
            "complexity": test_case["complexity"]
        }
        
        try:
            # Process query through multi-agent system
            result = await self.orchestrator.process_query(
                test_case["query"], 
                context, 
                f"test_session_{int(start_time)}"
            )
            
            processing_time = time.time() - start_time
            
            # Validate results
            validation_results = self.validate_test_result(test_case, result)
            
            return {
                "test_name": test_case["name"],
                "query": test_case["query"],
                "processing_time": processing_time,
                "confidence": result["confidence"],
                "agents_used": [source["agent_id"] for source in result["sources"]],
                "response_length": len(result["response"]),
                "validation_results": validation_results,
                "raw_result": result
            }
            
        except Exception as e:
            return {
                "test_name": test_case["name"],
                "query": test_case["query"],
                "processing_time": time.time() - start_time,
                "error": str(e),
                "agents_used": [],
                "confidence": 0.0,
                "validation_results": {"error": True}
            }
    
    def validate_test_result(self, test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test results against expectations"""
        
        validation = {
            "agent_selection_correct": False,
            "confidence_adequate": False,
            "response_quality": False,
            "cross_validation_performed": False
        }
        
        # Check agent selection
        agents_used = [source["agent_id"] for source in result["sources"]]
        expected_agents = test_case["expected_agents"]
        
        # At least one expected agent should be used
        validation["agent_selection_correct"] = any(
            expected_agent in agents_used for expected_agent in expected_agents
        )
        
        # Check confidence level
        validation["confidence_adequate"] = result["confidence"] >= 0.5
        
        # Check response quality (basic metrics)
        response = result.get("response", "")
        validation["response_quality"] = (
            len(response) > 100 and  # Substantial response
            any(keyword in response.lower() for keyword in ["analysis", "recommendation", "service", "configuration"])
        )
        
        # Check if cross-validation was performed
        validation_results = result.get("validation_results", {})
        validation["cross_validation_performed"] = (
            "consistency_score" in validation_results or 
            len(result["sources"]) > 1
        )
        
        return validation
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("🎯 MULTI-AGENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if "error" not in r])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {successful_tests/total_tests:.1%}")
        
        if successful_tests > 0:
            avg_processing_time = sum(r["processing_time"] for r in self.results if "error" not in r) / successful_tests
            avg_confidence = sum(r["confidence"] for r in self.results if "error" not in r) / successful_tests
            
            print(f"Average Processing Time: {avg_processing_time:.2f}s")
            print(f"Average Confidence: {avg_confidence:.1%}")
        
        # Validation summary
        print("\n📊 VALIDATION RESULTS:")
        
        validation_metrics = ["agent_selection_correct", "confidence_adequate", "response_quality", "cross_validation_performed"]
        
        for metric in validation_metrics:
            passed = sum(1 for r in self.results 
                        if r.get("validation_results", {}).get(metric, False))
            percentage = (passed / total_tests) * 100
            print(f"  {metric.replace('_', ' ').title()}: {passed}/{total_tests} ({percentage:.1f}%)")
        
        # Agent usage statistics
        print("\n🤖 AGENT USAGE STATISTICS:")
        agent_usage = {}
        for result in self.results:
            for agent in result.get("agents_used", []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        for agent, count in sorted(agent_usage.items(), key=lambda x: x[1], reverse=True):
            agent_name = agent.replace("_", " ").title()
            print(f"  {agent_name}: {count} queries")
        
        print("\n✅ Multi-Agent System validation completed!")

async def main():
    """Main test execution"""
    tester = MultiAgentTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        
        # Save detailed results
        with open("multi_agent_test_results.json", "w") as f:
            json.dump(tester.results, f, indent=2, default=str)
        print("📁 Detailed results saved to 'multi_agent_test_results.json'")
    else:
        print("\n❌ Test execution failed!")

if __name__ == "__main__":
    asyncio.run(main())