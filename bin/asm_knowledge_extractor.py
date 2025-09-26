#!/usr/bin/env python3
"""
ASM Knowledge Extractor
Analyzes local ASM repositories for architecture patterns and knowledge extraction
"""

import os
import json
import yaml
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

class ASMKnowledgeExtractor:
    def __init__(self, repos_dir: str, output_dir: str):
        self.repos_dir = Path(repos_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load ASM knowledge domains configuration
        self.load_knowledge_domains()
        
        # Initialize analysis results
        self.analysis_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "repositories_analyzed": 0,
            "patterns_found": {},
            "architecture_insights": {},
            "code_patterns": {},
            "recommendations": []
        }

    def load_knowledge_domains(self):
        """Load ASM knowledge domain configuration"""
        config_path = Path(__file__).parent.parent / "asm_knowledge_domains.yml"
        try:
            with open(config_path) as f:
                self.knowledge_domains = yaml.safe_load(f)
            print("✅ Loaded ASM knowledge domains configuration")
        except FileNotFoundError:
            print("⚠️  ASM knowledge domains config not found, using defaults")
            self.knowledge_domains = {"asm_knowledge_domains": {}}

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze a single repository for ASM patterns"""
        repo_name = repo_path.name
        print(f"📂 Analyzing repository: {repo_name}")
        
        analysis = {
            "name": repo_name,
            "path": str(repo_path),
            "file_counts": self.count_files(repo_path),
            "kafka_patterns": self.find_kafka_patterns(repo_path),
            "database_patterns": self.find_database_patterns(repo_path),
            "service_patterns": self.find_service_patterns(repo_path),
            "observer_patterns": self.find_observer_patterns(repo_path),
            "ui_patterns": self.find_ui_patterns(repo_path),
            "configuration_files": self.find_configuration_files(repo_path)
        }
        
        return analysis

    def count_files(self, repo_path: Path) -> Dict[str, int]:
        """Count different types of files in the repository"""
        file_counts = {
            "java": 0, "javascript": 0, "typescript": 0, "python": 0,
            "yaml": 0, "json": 0, "dockerfile": 0, "shell": 0,
            "properties": 0, "xml": 0
        }
        
        extensions = {
            ".java": "java",
            ".js": "javascript", 
            ".ts": "typescript",
            ".py": "python",
            ".yaml": "yaml", ".yml": "yaml",
            ".json": "json",
            ".sh": "shell", ".bash": "shell",
            ".properties": "properties",
            ".xml": "xml"
        }
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                if file_path.name.startswith("Dockerfile"):
                    file_counts["dockerfile"] += 1
                else:
                    suffix = file_path.suffix.lower()
                    if suffix in extensions:
                        file_counts[extensions[suffix]] += 1
        
        return file_counts

    def find_kafka_patterns(self, repo_path: Path) -> Dict[str, Any]:
        """Find Kafka-related patterns and topics"""
        patterns = {
            "topic_references": [],
            "producer_patterns": [],
            "consumer_patterns": [],
            "config_files": []
        }
        
        # Common ASM Kafka topic patterns
        topic_patterns = [
            r"\.topology\.input\.resources",
            r"\.topology\.output\.(edges|groups|merges|resources|metadata|status)",
            r"\.lifecycle\.(input|output)\.(events|alerts)",
            r"\.topology\.output\.rebroadcast"
        ]
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".java", ".py", ".properties", ".yaml", ".yml"]:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Find topic references
                    for pattern in topic_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            patterns["topic_references"].append({
                                "file": str(file_path.relative_to(repo_path)),
                                "pattern": pattern,
                                "matches": matches
                            })
                    
                    # Find producer/consumer patterns
                    if "KafkaProducer" in content or "producer" in content.lower():
                        patterns["producer_patterns"].append(str(file_path.relative_to(repo_path)))
                    
                    if "KafkaConsumer" in content or "@Consumer" in content:
                        patterns["consumer_patterns"].append(str(file_path.relative_to(repo_path)))
                        
                except Exception as e:
                    continue
        
        return patterns

    def find_database_patterns(self, repo_path: Path) -> Dict[str, Any]:
        """Find database-related patterns (Cassandra, PostgreSQL)"""
        patterns = {
            "cassandra_patterns": [],
            "postgresql_patterns": [],
            "graph_patterns": [],
            "sql_queries": []
        }
        
        database_keywords = {
            "cassandra": ["cassandra", "CassandraSession", "GraphTraversal", "vertex", "edge"],
            "postgresql": ["postgresql", "postgres", "jdbc", "JdbcTemplate", "SELECT", "INSERT"],
            "graph": ["vertex", "edge", "traversal", "gremlin", "graph"]
        }
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".java", ".py", ".sql", ".properties"]:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    for db_type, keywords in database_keywords.items():
                        for keyword in keywords:
                            if keyword.lower() in content.lower():
                                patterns[f"{db_type}_patterns"].append({
                                    "file": str(file_path.relative_to(repo_path)),
                                    "keyword": keyword
                                })
                                break
                except Exception:
                    continue
        
        return patterns

    def find_service_patterns(self, repo_path: Path) -> Dict[str, Any]:
        """Find microservice patterns and REST API definitions"""
        patterns = {
            "rest_endpoints": [],
            "service_definitions": [],
            "api_annotations": [],
            "health_checks": []
        }
        
        # REST endpoint patterns
        rest_patterns = [
            r"@RequestMapping\([\"']([^\"']+)[\"']\)",
            r"@GetMapping\([\"']([^\"']+)[\"']\)",
            r"@PostMapping\([\"']([^\"']+)[\"']\)",
            r"@PutMapping\([\"']([^\"']+)[\"']\)",
            r"@DeleteMapping\([\"']([^\"']+)[\"']\)"
        ]
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".java", ".py", ".js", ".ts"]:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Find REST endpoints
                    for pattern in rest_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            patterns["rest_endpoints"].extend([{
                                "file": str(file_path.relative_to(repo_path)),
                                "endpoint": match,
                                "type": pattern.split("@")[1].split("Mapping")[0]
                            } for match in matches])
                    
                    # Find service definitions
                    if "@Service" in content or "@Component" in content:
                        patterns["service_definitions"].append(str(file_path.relative_to(repo_path)))
                    
                    # Find health check endpoints
                    if "/health" in content or "health-check" in content:
                        patterns["health_checks"].append(str(file_path.relative_to(repo_path)))
                        
                except Exception:
                    continue
        
        return patterns

    def find_observer_patterns(self, repo_path: Path) -> Dict[str, Any]:
        """Find ASM observer-specific patterns"""
        patterns = {
            "observer_types": [],
            "configuration_patterns": [],
            "integration_patterns": []
        }
        
        # ASM observer types from the documentation
        observer_types = [
            "AppDynamics", "AWS", "Azure", "Datadog", "Dynatrace", 
            "GoogleCloud", "Kubernetes", "NewRelic", "ServiceNow",
            "VMware", "OpenStack", "Instana", "TADDM"
        ]
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Find observer type references
                    for observer_type in observer_types:
                        if observer_type.lower() in content.lower():
                            patterns["observer_types"].append({
                                "file": str(file_path.relative_to(repo_path)),
                                "observer_type": observer_type
                            })
                    
                    # Find observer configuration patterns
                    if "observer" in content.lower() and ("config" in content.lower() or "properties" in content.lower()):
                        patterns["configuration_patterns"].append(str(file_path.relative_to(repo_path)))
                        
                except Exception:
                    continue
        
        return patterns

    def find_ui_patterns(self, repo_path: Path) -> Dict[str, Any]:
        """Find UI-related patterns"""
        patterns = {
            "react_components": [],
            "api_calls": [],
            "ui_routes": []
        }
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".js", ".jsx", ".ts", ".tsx"]:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Find React components
                    if "React.Component" in content or "function " in content and "return (" in content:
                        patterns["react_components"].append(str(file_path.relative_to(repo_path)))
                    
                    # Find API calls
                    api_patterns = [r"fetch\([\"']([^\"']+)[\"']\)", r"axios\.get\([\"']([^\"']+)[\"']\)"]
                    for pattern in api_patterns:
                        matches = re.findall(pattern, content)
                        patterns["api_calls"].extend(matches)
                        
                except Exception:
                    continue
        
        return patterns

    def find_configuration_files(self, repo_path: Path) -> List[str]:
        """Find configuration files"""
        config_files = []
        config_patterns = [
            "*.properties", "*.yaml", "*.yml", "*.json",
            "Dockerfile*", "docker-compose*", "*.env",
            "helm/**/*.yaml", "k8s/**/*.yaml"
        ]
        
        for pattern in config_patterns:
            config_files.extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern)])
        
        return config_files

    def analyze_all_repositories(self):
        """Analyze all repositories in the ASM directory"""
        print(f"🔍 Starting ASM repository analysis in: {self.repos_dir}")
        
        categories = ["core", "observers", "ui", "services", "infrastructure", "documentation"]
        
        for category in categories:
            category_path = self.repos_dir / category
            if category_path.exists():
                print(f"\n📁 Analyzing {category} repositories...")
                
                for repo_path in category_path.iterdir():
                    if repo_path.is_dir() and (repo_path / ".git").exists():
                        analysis = self.analyze_repository(repo_path)
                        self.analysis_results["patterns_found"][f"{category}_{repo_path.name}"] = analysis
                        self.analysis_results["repositories_analyzed"] += 1

    def generate_insights(self):
        """Generate architectural insights from analysis"""
        insights = {
            "kafka_usage": self.analyze_kafka_usage(),
            "database_architecture": self.analyze_database_architecture(),
            "service_architecture": self.analyze_service_architecture(),
            "observer_ecosystem": self.analyze_observer_ecosystem()
        }
        
        self.analysis_results["architecture_insights"] = insights

    def analyze_kafka_usage(self) -> Dict[str, Any]:
        """Analyze Kafka usage patterns across repositories"""
        all_topics = []
        producers = []
        consumers = []
        
        for repo_analysis in self.analysis_results["patterns_found"].values():
            kafka_patterns = repo_analysis.get("kafka_patterns", {})
            all_topics.extend(kafka_patterns.get("topic_references", []))
            producers.extend(kafka_patterns.get("producer_patterns", []))
            consumers.extend(kafka_patterns.get("consumer_patterns", []))
        
        return {
            "total_topics": len(all_topics),
            "producer_services": len(producers),
            "consumer_services": len(consumers),
            "common_topics": self.find_common_patterns(all_topics)
        }

    def analyze_database_architecture(self) -> Dict[str, Any]:
        """Analyze database usage patterns"""
        cassandra_usage = []
        postgresql_usage = []
        
        for repo_analysis in self.analysis_results["patterns_found"].values():
            db_patterns = repo_analysis.get("database_patterns", {})
            cassandra_usage.extend(db_patterns.get("cassandra_patterns", []))
            postgresql_usage.extend(db_patterns.get("postgresql_patterns", []))
        
        return {
            "cassandra_repositories": len([r for r in cassandra_usage if r]),
            "postgresql_repositories": len([r for r in postgresql_usage if r]),
            "dual_database_pattern": len(cassandra_usage) > 0 and len(postgresql_usage) > 0
        }

    def analyze_service_architecture(self) -> Dict[str, Any]:
        """Analyze microservice architecture patterns"""
        all_endpoints = []
        services = []
        
        for repo_analysis in self.analysis_results["patterns_found"].values():
            service_patterns = repo_analysis.get("service_patterns", {})
            all_endpoints.extend(service_patterns.get("rest_endpoints", []))
            services.extend(service_patterns.get("service_definitions", []))
        
        return {
            "total_endpoints": len(all_endpoints),
            "service_count": len(services),
            "api_patterns": self.find_common_patterns([e.get("endpoint", "") for e in all_endpoints])
        }

    def analyze_observer_ecosystem(self) -> Dict[str, Any]:
        """Analyze observer ecosystem"""
        observer_types = []
        
        for repo_analysis in self.analysis_results["patterns_found"].values():
            observer_patterns = repo_analysis.get("observer_patterns", {})
            observer_types.extend([o.get("observer_type") for o in observer_patterns.get("observer_types", [])])
        
        return {
            "supported_platforms": len(set(observer_types)),
            "platform_distribution": {platform: observer_types.count(platform) for platform in set(observer_types)}
        }

    def find_common_patterns(self, items: List[str]) -> List[str]:
        """Find common patterns in a list of items"""
        from collections import Counter
        counter = Counter(items)
        return [item for item, count in counter.most_common(10)]

    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed analysis
        detailed_file = self.output_dir / f"asm_analysis_detailed_{timestamp}.json"
        with open(detailed_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        # Save summary report
        summary = {
            "analysis_summary": {
                "timestamp": self.analysis_results["timestamp"],
                "repositories_analyzed": self.analysis_results["repositories_analyzed"],
                "insights": self.analysis_results["architecture_insights"]
            }
        }
        
        summary_file = self.output_dir / f"asm_analysis_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Detailed results: {detailed_file}")
        print(f"📊 Summary report: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description="ASM Knowledge Extractor")
    parser.add_argument("--repos-dir", default="data/asm_repositories", 
                       help="Directory containing ASM repositories")
    parser.add_argument("--output-dir", default="data/analysis_results",
                       help="Output directory for analysis results")
    
    args = parser.parse_args()
    
    # Create extractor and run analysis
    extractor = ASMKnowledgeExtractor(args.repos_dir, args.output_dir)
    extractor.analyze_all_repositories()
    extractor.generate_insights()
    extractor.save_results()

if __name__ == "__main__":
    main()