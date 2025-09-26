#!/usr/bin/env python3
"""
Specialized Knowledge Agents - Phase 2 Implementation
Domain-specific agents with expertise in ASM Topology, Support Cases, GitHub Sources, etc.
"""

import asyncio
import json
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import httpx
import yaml

from multi_agent_foundation import (
    BaseKnowledgeAgent, AgentRole, KnowledgeFragment, AgentQuery, AgentResponse,
    KnowledgeConfidence
)

class TopologyAgent(BaseKnowledgeAgent):
    """Specialized agent for ASM Topology knowledge"""
    
    def __init__(self):
        super().__init__(
            agent_id="asm_topology_expert",
            role=AgentRole.TOPOLOGY_EXPERT,
            knowledge_domains=[
                "topology", "asm", "nasm-topology", "merge-service", 
                "ui-content", "observer", "kubernetes", "rest-observer",
                "file-observer", "service-mesh", "istio"
            ]
        )
        self.topology_patterns = self._load_topology_patterns()
        self.service_configurations = self._load_service_configs()
        
    def _load_topology_patterns(self) -> Dict[str, Any]:
        """Load ASM topology patterns and configurations"""
        patterns = {
            "service_dependencies": {
                "nasm-topology": ["merge-service", "observer-services"],
                "merge-service": ["ui-content", "analytics"],
                "observer-services": ["kubernetes-observer", "rest-observer", "file-observer"]
            },
            "common_issues": {
                "data_ingestion": ["observer connectivity", "data source validation", "merge conflicts"],
                "service_health": ["pod status", "resource limits", "network connectivity"],
                "topology_rendering": ["ui service", "data synchronization", "cache issues"]
            },
            "resolution_patterns": {
                "connectivity_issues": [
                    "verify service endpoints",
                    "check network policies",
                    "validate certificates",
                    "review firewall rules"
                ],
                "data_inconsistency": [
                    "check observer status",
                    "verify merge configuration",
                    "validate data sources",
                    "review deduplication settings"
                ]
            }
        }
        return patterns
    
    def _load_service_configs(self) -> Dict[str, Any]:
        """Load service configuration templates"""
        return {
            "topology_config": {
                "merge": {
                    "enabled": True,
                    "sources": ["file", "rest", "kubernetes"],
                    "deduplication": True,
                    "validation": "strict"
                },
                "processing": {
                    "batch_size": 100,
                    "timeout": 30,
                    "retry_attempts": 3
                }
            },
            "observer_configs": {
                "kubernetes": {
                    "namespace_filter": "asm-*",
                    "resource_types": ["pods", "services", "deployments"],
                    "polling_interval": 30
                },
                "rest": {
                    "endpoints": [],
                    "auth_type": "bearer",
                    "timeout": 15
                }
            }
        }
    
    async def process_query(self, query: AgentQuery) -> AgentResponse:
        """Process topology-related queries"""
        start_time = datetime.now()
        knowledge_fragments = []
        
        query_lower = query.content.lower()
        
        # Analyze query for topology-specific patterns
        service_matches = self._identify_services(query_lower)
        issue_patterns = self._identify_issues(query_lower)
        config_requests = self._identify_config_needs(query_lower)
        
        # Generate service analysis
        if service_matches:
            service_fragment = await self._generate_service_analysis(service_matches, query.context)
            knowledge_fragments.append(service_fragment)
        
        # Generate issue resolution
        if issue_patterns:
            resolution_fragment = await self._generate_resolution_guidance(issue_patterns, query.context)
            knowledge_fragments.append(resolution_fragment)
        
        # Generate configuration guidance
        if config_requests:
            config_fragment = await self._generate_config_guidance(config_requests, query.context)
            knowledge_fragments.append(config_fragment)
        
        # Generate general topology insight if no specific patterns matched
        if not knowledge_fragments:
            general_fragment = await self._generate_general_topology_insight(query.content, query.context)
            knowledge_fragments.append(general_fragment)
        
        # Calculate overall confidence
        avg_confidence = sum(f.confidence for f in knowledge_fragments) / len(knowledge_fragments) if knowledge_fragments else 0.5
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            query_id=query.query_id,
            agent_id=self.agent_id,
            knowledge_fragments=knowledge_fragments,
            confidence=avg_confidence,
            processing_time=processing_time,
            metadata={
                "services_identified": service_matches,
                "issues_identified": issue_patterns,
                "config_areas": config_requests
            }
        )
    
    def _identify_services(self, query: str) -> List[str]:
        """Identify ASM services mentioned in query"""
        services = []
        for domain in self.knowledge_domains:
            if domain in query:
                services.append(domain)
        return services
    
    def _identify_issues(self, query: str) -> List[str]:
        """Identify potential issues mentioned in query"""
        issue_keywords = {
            "connectivity": ["connect", "network", "endpoint", "unreachable"],
            "performance": ["slow", "timeout", "latency", "performance"],
            "data": ["missing", "incomplete", "inconsistent", "duplicate"],
            "service": ["down", "failing", "error", "crash", "restart"]
        }
        
        identified_issues = []
        for issue_type, keywords in issue_keywords.items():
            if any(keyword in query for keyword in keywords):
                identified_issues.append(issue_type)
        
        return identified_issues
    
    def _identify_config_needs(self, query: str) -> List[str]:
        """Identify configuration-related requests"""
        config_keywords = {
            "setup": ["configure", "setup", "install", "deploy"],
            "troubleshoot": ["debug", "diagnose", "troubleshoot", "fix"],
            "optimize": ["optimize", "tune", "improve", "enhance"]
        }
        
        config_needs = []
        for need_type, keywords in config_keywords.items():
            if any(keyword in query for keyword in keywords):
                config_needs.append(need_type)
        
        return config_needs
    
    async def _generate_service_analysis(self, services: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate analysis of identified services"""
        
        analysis_parts = []
        analysis_parts.append("🔧 **ASM Topology Services Analysis**\n")
        
        # Primary services
        primary_services = [s for s in services if s in ["nasm-topology", "merge-service", "ui-content"]]
        if primary_services:
            analysis_parts.append(f"**Primary Services:** {', '.join(primary_services)}\n")
        
        # Service functions
        analysis_parts.append("**Service Functions:**")
        for service in services[:5]:  # Limit to avoid too much text
            if service in self.topology_patterns["service_dependencies"]:
                deps = self.topology_patterns["service_dependencies"][service]
                analysis_parts.append(f"• **{service}**: Core topology data processing and management")
                analysis_parts.append(f"  Dependencies: {', '.join(deps)}")
        
        # Data flow
        analysis_parts.append("\n**Data Flow:**")
        analysis_parts.append("Raw Data → Observers → Topology Processing → Merge Service → Analytics → UI Dashboard")
        
        # Common resolution patterns
        analysis_parts.append("\n**Common Resolution Patterns:**")
        analysis_parts.append("• verify data sources")
        analysis_parts.append("• check service status") 
        analysis_parts.append("• review merge configuration")
        
        content = "\n".join(analysis_parts)
        
        return KnowledgeFragment(
            content=content,
            source="asm_topology_expert",
            confidence=KnowledgeConfidence.HIGH.value,
            agent_id=self.agent_id,
            tags=["topology", "service-analysis"] + services
        )
    
    async def _generate_resolution_guidance(self, issues: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate resolution guidance for identified issues"""
        
        guidance_parts = []
        guidance_parts.append("🛠️ **Troubleshooting Steps:**\n")
        
        for issue in issues:
            if issue in self.topology_patterns["resolution_patterns"]:
                steps = self.topology_patterns["resolution_patterns"][issue]
                guidance_parts.append(f"**{issue.title()} Issues:**")
                for i, step in enumerate(steps, 1):
                    guidance_parts.append(f"{i}. {step}")
                guidance_parts.append("")
        
        # Add general troubleshooting
        guidance_parts.append("**General Diagnostics:**")
        guidance_parts.append("1. Verify topology service health: `oc get pods -n asm-topology`")
        guidance_parts.append("2. Check data ingestion logs for observer services")
        guidance_parts.append("3. Review merge service configuration and conflicts")
        guidance_parts.append("4. Validate UI dashboard connectivity")
        
        content = "\n".join(guidance_parts)
        
        return KnowledgeFragment(
            content=content,
            source="asm_topology_expert",
            confidence=KnowledgeConfidence.HIGH.value,
            agent_id=self.agent_id,
            tags=["troubleshooting", "resolution"] + issues
        )
    
    async def _generate_config_guidance(self, config_needs: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate configuration guidance"""
        
        config_parts = []
        config_parts.append("⚙️ **Configuration Example:**\n")
        config_parts.append("```yaml")
        config_parts.append("topology:")
        config_parts.append("  merge:")
        config_parts.append("    enabled: true")
        config_parts.append("    sources: [\"file\", \"rest\", \"kubernetes\"]")
        config_parts.append("  processing:")
        config_parts.append("    deduplication: true")
        config_parts.append("    validation: strict")
        config_parts.append("```")
        
        content = "\n".join(config_parts)
        
        return KnowledgeFragment(
            content=content,
            source="asm_topology_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["configuration", "yaml"] + config_needs
        )
    
    async def _generate_general_topology_insight(self, query: str, context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate general topology insights"""
        
        insight_parts = []
        insight_parts.append("🌐 **ASM Topology Overview:**\n")
        insight_parts.append("ASM topology management involves multiple interconnected services:")
        insight_parts.append("")
        insight_parts.append("• **Data Collection**: Observer services gather topology data")
        insight_parts.append("• **Processing**: nasm-topology processes and validates data")
        insight_parts.append("• **Integration**: merge-service combines multiple sources")
        insight_parts.append("• **Visualization**: ui-content provides dashboard interface")
        insight_parts.append("")
        insight_parts.append("**Key Monitoring Points:**")
        insight_parts.append("- Observer connectivity and data quality")
        insight_parts.append("- Service health and resource utilization")
        insight_parts.append("- Data consistency across sources")
        
        content = "\n".join(insight_parts)
        
        return KnowledgeFragment(
            content=content,
            source="asm_topology_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["overview", "general", "topology"]
        )
    
    async def validate_knowledge(self, fragment: KnowledgeFragment) -> bool:
        """Validate topology-related knowledge"""
        # Check if fragment contains valid topology concepts
        topology_concepts = ["observer", "merge", "topology", "service", "kubernetes", "ui-content"]
        content_lower = fragment.content.lower()
        
        concept_matches = sum(1 for concept in topology_concepts if concept in content_lower)
        return concept_matches >= 2  # Require at least 2 topology concepts

class CaseAnalysisAgent(BaseKnowledgeAgent):
    """Specialized agent for support case analysis"""
    
    def __init__(self):
        super().__init__(
            agent_id="case_analysis_expert",
            role=AgentRole.CASE_ANALYST,
            knowledge_domains=[
                "support", "case", "incident", "problem", "resolution",
                "symptoms", "diagnosis", "troubleshooting", "customer"
            ]
        )
        self.case_patterns = self._load_case_patterns()
        self.resolution_library = self._load_resolution_library()
    
    def _load_case_patterns(self) -> Dict[str, Any]:
        """Load common case patterns and classifications"""
        return {
            "urgency_indicators": {
                "high": ["production down", "outage", "critical", "urgent", "emergency"],
                "medium": ["degraded performance", "intermittent", "affecting users"],
                "low": ["question", "how to", "best practice", "documentation"]
            },
            "category_patterns": {
                "connectivity": ["connection", "network", "timeout", "unreachable"],
                "performance": ["slow", "latency", "response time", "throughput"],
                "configuration": ["setup", "config", "parameter", "setting"],
                "data": ["missing data", "inconsistent", "synchronization", "backup"]
            },
            "symptom_clusters": {
                "service_unavailable": ["503", "service unavailable", "cannot connect"],
                "authentication": ["401", "unauthorized", "login", "credentials"],
                "resource_exhaustion": ["memory", "cpu", "disk space", "quota exceeded"]
            }
        }
    
    def _load_resolution_library(self) -> Dict[str, Any]:
        """Load resolution patterns and templates"""
        return {
            "connectivity_resolutions": [
                "Verify network connectivity between services",
                "Check firewall rules and security groups",
                "Validate DNS resolution",
                "Review proxy and load balancer configuration"
            ],
            "performance_resolutions": [
                "Analyze resource utilization metrics",
                "Review application logs for bottlenecks",
                "Check database query performance",
                "Validate caching configuration"
            ],
            "configuration_resolutions": [
                "Review configuration files for syntax errors",
                "Validate parameter values against documentation",
                "Check environment-specific settings",
                "Verify service restart after configuration changes"
            ]
        }
    
    async def process_query(self, query: AgentQuery) -> AgentResponse:
        """Process case analysis queries"""
        start_time = datetime.now()
        knowledge_fragments = []
        
        # Analyze case characteristics
        urgency = self._assess_urgency(query.content)
        categories = self._categorize_issue(query.content)
        symptoms = self._identify_symptoms(query.content)
        
        # Generate case analysis
        analysis_fragment = await self._generate_case_analysis(
            query.content, urgency, categories, symptoms, query.context
        )
        knowledge_fragments.append(analysis_fragment)
        
        # Generate resolution recommendations
        if categories:
            resolution_fragment = await self._generate_resolution_recommendations(
                categories, symptoms, query.context
            )
            knowledge_fragments.append(resolution_fragment)
        
        # Load similar historical cases if available
        similar_cases = await self._find_similar_cases(query.content, query.context)
        if similar_cases:
            historical_fragment = await self._generate_historical_insights(similar_cases)
            knowledge_fragments.append(historical_fragment)
        
        avg_confidence = sum(f.confidence for f in knowledge_fragments) / len(knowledge_fragments)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            query_id=query.query_id,
            agent_id=self.agent_id,
            knowledge_fragments=knowledge_fragments,
            confidence=avg_confidence,
            processing_time=processing_time,
            metadata={
                "urgency": urgency,
                "categories": categories,
                "symptoms": symptoms,
                "similar_cases_found": len(similar_cases) if similar_cases else 0
            }
        )
    
    def _assess_urgency(self, content: str) -> str:
        """Assess case urgency based on content"""
        content_lower = content.lower()
        
        for urgency, indicators in self.case_patterns["urgency_indicators"].items():
            if any(indicator in content_lower for indicator in indicators):
                return urgency
        
        return "medium"  # Default urgency
    
    def _categorize_issue(self, content: str) -> List[str]:
        """Categorize the issue type"""
        content_lower = content.lower()
        categories = []
        
        for category, patterns in self.case_patterns["category_patterns"].items():
            if any(pattern in content_lower for pattern in patterns):
                categories.append(category)
        
        return categories
    
    def _identify_symptoms(self, content: str) -> List[str]:
        """Identify symptoms from case content"""
        content_lower = content.lower()
        symptoms = []
        
        for symptom_type, indicators in self.case_patterns["symptom_clusters"].items():
            if any(indicator in content_lower for indicator in indicators):
                symptoms.append(symptom_type)
        
        return symptoms
    
    async def _generate_case_analysis(self, content: str, urgency: str, categories: List[str], 
                                    symptoms: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate comprehensive case analysis"""
        
        analysis_parts = []
        analysis_parts.append("📋 **Case Analysis Summary:**\n")
        analysis_parts.append(f"**Urgency Level:** {urgency.upper()}")
        
        if categories:
            analysis_parts.append(f"**Issue Categories:** {', '.join(categories)}")
        
        if symptoms:
            analysis_parts.append(f"**Identified Symptoms:** {', '.join(symptoms)}")
        
        # Add contextual analysis
        if context.get('services'):
            services = context['services']
            analysis_parts.append(f"**Affected Services:** {', '.join(services[:3])}")
        
        if context.get('case_number'):
            analysis_parts.append(f"**Case Reference:** {context['case_number']}")
        
        analysis_parts.append("\n**Preliminary Assessment:**")
        
        if urgency == "high":
            analysis_parts.append("• High priority issue requiring immediate attention")
            analysis_parts.append("• Consider engaging escalation procedures")
        elif "connectivity" in categories:
            analysis_parts.append("• Network or service connectivity issue detected")
            analysis_parts.append("• Focus on infrastructure and communication paths")
        elif "performance" in categories:
            analysis_parts.append("• Performance degradation identified")
            analysis_parts.append("• Analyze resource utilization and bottlenecks")
        
        content = "\n".join(analysis_parts)
        
        return KnowledgeFragment(
            content=content,
            source="case_analysis_expert",
            confidence=KnowledgeConfidence.HIGH.value,
            agent_id=self.agent_id,
            tags=["case-analysis", "assessment", urgency] + categories
        )
    
    async def _generate_resolution_recommendations(self, categories: List[str], symptoms: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate resolution recommendations"""
        
        resolution_parts = []
        resolution_parts.append("💡 **Resolution Recommendations:**\n")
        
        for category in categories[:3]:  # Limit to top 3 categories
            if category in self.resolution_library:
                key = f"{category}_resolutions"
                if key in self.resolution_library:
                    resolution_parts.append(f"**{category.title()} Issues:**")
                    for i, step in enumerate(self.resolution_library[key][:3], 1):
                        resolution_parts.append(f"{i}. {step}")
                    resolution_parts.append("")
        
        # Add symptom-specific guidance
        if "service_unavailable" in symptoms:
            resolution_parts.append("**Service Unavailable Troubleshooting:**")
            resolution_parts.append("• Check service health and pod status")
            resolution_parts.append("• Verify load balancer and ingress configuration")
            resolution_parts.append("• Review service logs for error patterns")
        
        content = "\n".join(resolution_parts)
        
        return KnowledgeFragment(
            content=content,
            source="case_analysis_expert", 
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["resolution", "recommendations"] + categories
        )
    
    async def _find_similar_cases(self, content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical cases"""
        # This would integrate with the existing case clustering system
        similar_cases = context.get('similar_cases', [])
        return similar_cases[:3]  # Return top 3 similar cases
    
    async def _generate_historical_insights(self, similar_cases: List[Dict[str, Any]]) -> KnowledgeFragment:
        """Generate insights from similar historical cases"""
        
        insight_parts = []
        insight_parts.append("📚 **Historical Case Insights:**\n")
        insight_parts.append(f"Found {len(similar_cases)} similar cases with relevant patterns:\n")
        
        for i, case in enumerate(similar_cases, 1):
            case_number = case.get('case_number', f'Case {i}')
            similarity = case.get('similarity_score', 0)
            insight_parts.append(f"**{case_number}** (Similarity: {similarity:.2f})")
            
            if case.get('services'):
                insight_parts.append(f"  Services: {', '.join(case['services'][:2])}")
            
            if case.get('resolution_patterns'):
                patterns = case['resolution_patterns'][:2]
                insight_parts.append(f"  Patterns: {', '.join(patterns)}")
            
            insight_parts.append("")
        
        content = "\n".join(insight_parts)
        
        return KnowledgeFragment(
            content=content,
            source="case_analysis_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["historical", "similar-cases", "patterns"]
        )
    
    async def validate_knowledge(self, fragment: KnowledgeFragment) -> bool:
        """Validate case analysis knowledge"""
        content_lower = fragment.content.lower()
        case_concepts = ["case", "issue", "problem", "resolution", "symptom", "troubleshoot"]
        
        concept_matches = sum(1 for concept in case_concepts if concept in content_lower)
        return concept_matches >= 2

class GitHubSourceAgent(BaseKnowledgeAgent):
    """Specialized agent for GitHub repository knowledge"""
    
    def __init__(self):
        super().__init__(
            agent_id="github_source_expert",
            role=AgentRole.GITHUB_SPECIALIST,
            knowledge_domains=[
                "github", "repository", "code", "documentation", "issues",
                "pull requests", "commits", "releases", "readme", "wiki"
            ]
        )
        self.github_patterns = self._load_github_patterns()
    
    def _load_github_patterns(self) -> Dict[str, Any]:
        """Load GitHub repository patterns and analysis rules"""
        return {
            "repo_types": {
                "documentation": ["docs", "wiki", "readme", "guide"],
                "configuration": ["config", "yaml", "json", "settings"],
                "scripts": ["script", "automation", "tool", "utility"],
                "source_code": ["src", "lib", "api", "service"]
            },
            "issue_patterns": {
                "bug": ["bug", "error", "issue", "problem", "fix"],
                "enhancement": ["feature", "enhancement", "improvement", "request"],
                "question": ["question", "help", "how to", "clarification"]
            }
        }
    
    async def process_query(self, query: AgentQuery) -> AgentResponse:
        """Process GitHub-related queries"""
        start_time = datetime.now()
        knowledge_fragments = []
        
        # Analyze query for GitHub-specific patterns
        repo_references = self._identify_repositories(query.content)
        doc_requests = self._identify_documentation_needs(query.content)
        code_requests = self._identify_code_requests(query.content)
        
        # Generate repository analysis
        if repo_references:
            repo_fragment = await self._generate_repository_analysis(repo_references, query.context)
            knowledge_fragments.append(repo_fragment)
        
        # Generate documentation guidance
        if doc_requests:
            doc_fragment = await self._generate_documentation_guidance(doc_requests, query.context)
            knowledge_fragments.append(doc_fragment)
        
        # Generate code insights
        if code_requests:
            code_fragment = await self._generate_code_insights(code_requests, query.context)
            knowledge_fragments.append(code_fragment)
        
        # Generate general GitHub insight if no specific patterns
        if not knowledge_fragments:
            general_fragment = await self._generate_general_github_insight(query.content, query.context)
            knowledge_fragments.append(general_fragment)
        
        avg_confidence = sum(f.confidence for f in knowledge_fragments) / len(knowledge_fragments) if knowledge_fragments else 0.5
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            query_id=query.query_id,
            agent_id=self.agent_id,
            knowledge_fragments=knowledge_fragments,
            confidence=avg_confidence,
            processing_time=processing_time,
            metadata={
                "repositories_identified": repo_references,
                "documentation_requests": doc_requests,
                "code_requests": code_requests
            }
        )
    
    def _identify_repositories(self, content: str) -> List[str]:
        """Identify repository references in query"""
        # Look for GitHub URL patterns or repo names
        github_pattern = r'github\.com[/:]([^/\s]+)/([^/\s]+)'
        matches = re.findall(github_pattern, content)
        
        repos = []
        for owner, repo in matches:
            repos.append(f"{owner}/{repo}")
        
        return repos
    
    def _identify_documentation_needs(self, content: str) -> List[str]:
        """Identify documentation-related requests"""
        content_lower = content.lower()
        doc_keywords = ["documentation", "readme", "guide", "tutorial", "example", "how to"]
        
        return [keyword for keyword in doc_keywords if keyword in content_lower]
    
    def _identify_code_requests(self, content: str) -> List[str]:
        """Identify code-related requests"""
        content_lower = content.lower()
        code_keywords = ["code", "implementation", "function", "class", "method", "api"]
        
        return [keyword for keyword in code_keywords if keyword in content_lower]
    
    async def _generate_repository_analysis(self, repos: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate analysis of identified repositories"""
        
        analysis_parts = []
        analysis_parts.append("📁 **GitHub Repository Analysis:**\n")
        
        for repo in repos:
            analysis_parts.append(f"**Repository:** {repo}")
            analysis_parts.append("• Repository structure and organization")
            analysis_parts.append("• Documentation quality and completeness")
            analysis_parts.append("• Recent activity and maintenance status")
            analysis_parts.append("• Issue and pull request patterns")
            analysis_parts.append("")
        
        analysis_parts.append("**Recommended Actions:**")
        analysis_parts.append("• Review README and documentation files")
        analysis_parts.append("• Check recent commits and releases")
        analysis_parts.append("• Examine open issues for known problems")
        analysis_parts.append("• Validate configuration examples")
        
        content = "\n".join(analysis_parts)
        
        return KnowledgeFragment(
            content=content,
            source="github_source_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["github", "repository-analysis"] + repos
        )
    
    async def _generate_documentation_guidance(self, doc_requests: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate documentation guidance"""
        
        doc_parts = []
        doc_parts.append("📖 **Documentation Guidance:**\n")
        doc_parts.append("**Key Documentation Sources:**")
        doc_parts.append("• README.md files for project overview and setup")
        doc_parts.append("• docs/ directories for detailed guides")
        doc_parts.append("• Wiki pages for community contributions")
        doc_parts.append("• CODE_OF_CONDUCT.md and CONTRIBUTING.md")
        doc_parts.append("")
        doc_parts.append("**Documentation Best Practices:**")
        doc_parts.append("• Start with README for project introduction")
        doc_parts.append("• Look for examples/ or samples/ directories")
        doc_parts.append("• Check for API documentation or OpenAPI specs")
        doc_parts.append("• Review issue templates and PR guidelines")
        
        content = "\n".join(doc_parts)
        
        return KnowledgeFragment(
            content=content,
            source="github_source_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["documentation", "guidance"] + doc_requests
        )
    
    async def _generate_code_insights(self, code_requests: List[str], context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate code-related insights"""
        
        code_parts = []
        code_parts.append("💻 **Code Analysis Insights:**\n")
        code_parts.append("**Code Structure Analysis:**")
        code_parts.append("• Examine src/ or lib/ directories for main code")
        code_parts.append("• Check package.json, requirements.txt, or similar for dependencies")
        code_parts.append("• Review Dockerfile or deployment configurations")
        code_parts.append("• Look for test/ directories for testing patterns")
        code_parts.append("")
        code_parts.append("**Code Quality Indicators:**")
        code_parts.append("• Presence of automated tests and CI/CD")
        code_parts.append("• Code formatting and linting configurations")
        code_parts.append("• Dependency management and security updates")
        code_parts.append("• Documentation coverage and inline comments")
        
        content = "\n".join(code_parts)
        
        return KnowledgeFragment(
            content=content,
            source="github_source_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["code-analysis", "insights"] + code_requests
        )
    
    async def _generate_general_github_insight(self, query: str, context: Dict[str, Any]) -> KnowledgeFragment:
        """Generate general GitHub insights"""
        
        insight_parts = []
        insight_parts.append("🔍 **GitHub Knowledge Sources:**\n")
        insight_parts.append("GitHub repositories provide valuable knowledge through:")
        insight_parts.append("")
        insight_parts.append("• **Documentation**: README files, wiki pages, docs directories")
        insight_parts.append("• **Code Examples**: Sample implementations and configurations")
        insight_parts.append("• **Issue Tracking**: Known problems and solutions")
        insight_parts.append("• **Discussions**: Community Q&A and best practices")
        insight_parts.append("• **Releases**: Version history and change logs")
        insight_parts.append("")
        insight_parts.append("**Effective Repository Navigation:**")
        insight_parts.append("- Start with README for project overview")
        insight_parts.append("- Browse recent issues for current problems")
        insight_parts.append("- Check discussions for community insights")
        insight_parts.append("- Review pull requests for ongoing development")
        
        content = "\n".join(insight_parts)
        
        return KnowledgeFragment(
            content=content,
            source="github_source_expert",
            confidence=KnowledgeConfidence.MEDIUM.value,
            agent_id=self.agent_id,
            tags=["github", "general", "navigation"]
        )
    
    async def validate_knowledge(self, fragment: KnowledgeFragment) -> bool:
        """Validate GitHub-related knowledge"""
        content_lower = fragment.content.lower()
        github_concepts = ["github", "repository", "code", "documentation", "readme", "wiki"]
        
        concept_matches = sum(1 for concept in github_concepts if concept in content_lower)
        return concept_matches >= 2

# Export specialized agents
__all__ = ['TopologyAgent', 'CaseAnalysisAgent', 'GitHubSourceAgent']