"""
GitHub Repository Analyzer for IBM Knowledge Fusion Platform
Analyzes external GitHub repositories to extract patterns, architectures, and knowledge
Integrates with the novel temporal knowledge synthesis system
"""

import asyncio
import aiohttp
import yaml
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import base64
import re
from dataclasses import dataclass, asdict
import ast
import hashlib
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RepositoryAnalysis:
    """Structured repository analysis results"""
    repository_url: str
    repository_name: str
    analysis_timestamp: datetime
    patterns_extracted: List[Dict[str, Any]]
    architectural_insights: Dict[str, Any]
    temporal_evolution: Dict[str, Any]
    knowledge_domains: List[str]
    confidence_metrics: Dict[str, float]
    integration_points: List[Dict[str, Any]]

@dataclass
class CodePattern:
    """Extracted code pattern representation"""
    pattern_type: str
    pattern_name: str
    file_path: str
    code_snippet: str
    description: str
    complexity_score: float
    usage_frequency: int
    temporal_stability: float

class GitHubAPIClient:
    """GitHub API client with rate limiting and error handling"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = datetime.now()
        
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with aiohttp.ClientSession() as session:
            headers = self._get_headers()
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get repo info: {response.status}")
                    return {}
    
    async def get_repository_contents(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """Get repository contents"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        async with aiohttp.ClientSession() as session:
            headers = self._get_headers()
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get contents for {path}: {response.status}")
                    return []
    
    async def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get content of a specific file"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        async with aiohttp.ClientSession() as session:
            headers = self._get_headers()
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    file_data = await response.json()
                    if file_data.get('encoding') == 'base64':
                        content = base64.b64decode(file_data['content']).decode('utf-8')
                        return content
                return None
    
    async def get_commits(self, owner: str, repo: str, since: Optional[datetime] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get repository commits"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        if since:
            params["since"] = since.isoformat()
            
        async with aiohttp.ClientSession() as session:
            headers = self._get_headers()
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get commits: {response.status}")
                    return []
    
    async def get_issues(self, owner: str, repo: str, state: str = "all", limit: int = 100) -> List[Dict[str, Any]]:
        """Get repository issues"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": limit}
        
        async with aiohttp.ClientSession() as session:
            headers = self._get_headers()
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get issues: {response.status}")
                    return []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if available"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "IBM-Knowledge-Fusion-Analyzer/1.0"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

class CodePatternExtractor:
    """Extract architectural and design patterns from code"""
    
    def __init__(self):
        self.pattern_detectors = {
            "singleton": self._detect_singleton_pattern,
            "factory": self._detect_factory_pattern,
            "observer": self._detect_observer_pattern,
            "decorator": self._detect_decorator_pattern,
            "async_patterns": self._detect_async_patterns,
            "error_handling": self._detect_error_handling_patterns,
            "api_patterns": self._detect_api_patterns,
            "configuration_patterns": self._detect_configuration_patterns
        }
    
    async def extract_patterns_from_file(self, file_path: str, content: str) -> List[CodePattern]:
        """Extract patterns from a single file"""
        patterns = []
        
        for pattern_type, detector in self.pattern_detectors.items():
            try:
                detected_patterns = await detector(file_path, content)
                patterns.extend(detected_patterns)
            except Exception as e:
                logger.warning(f"Error detecting {pattern_type} in {file_path}: {str(e)}")
        
        return patterns
    
    async def _detect_singleton_pattern(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect Singleton pattern implementations"""
        patterns = []
        
        # Python singleton patterns
        singleton_indicators = [
            r"class\s+\w+.*:\s*\n\s*_instance\s*=\s*None",
            r"def\s+__new__\s*\(",
            r"@singleton",
            r"_instances\s*=\s*{}"
        ]
        
        for i, indicator in enumerate(singleton_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="singleton",
                    pattern_name=f"singleton_implementation_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 200),
                    description="Singleton pattern implementation",
                    complexity_score=0.6,
                    usage_frequency=1,
                    temporal_stability=0.8
                ))
        
        return patterns
    
    async def _detect_factory_pattern(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect Factory pattern implementations"""
        patterns = []
        
        factory_indicators = [
            r"class\s+\w*Factory\w*",
            r"def\s+create_\w+\(",
            r"def\s+make_\w+\(",
            r"@factory\w*"
        ]
        
        for i, indicator in enumerate(factory_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="factory",
                    pattern_name=f"factory_pattern_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 300),
                    description="Factory pattern implementation",
                    complexity_score=0.7,
                    usage_frequency=1,
                    temporal_stability=0.9
                ))
        
        return patterns
    
    async def _detect_observer_pattern(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect Observer pattern implementations"""
        patterns = []
        
        observer_indicators = [
            r"class\s+\w*Observer\w*",
            r"def\s+notify\s*\(",
            r"def\s+subscribe\s*\(",
            r"def\s+unsubscribe\s*\(",
            r"observers\s*=\s*\[\]"
        ]
        
        for i, indicator in enumerate(observer_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="observer",
                    pattern_name=f"observer_pattern_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 250),
                    description="Observer pattern implementation",
                    complexity_score=0.8,
                    usage_frequency=1,
                    temporal_stability=0.7
                ))
        
        return patterns
    
    async def _detect_decorator_pattern(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect Decorator pattern implementations"""
        patterns = []
        
        decorator_indicators = [
            r"@\w+\s*\n\s*def",
            r"def\s+\w*decorator\w*\(",
            r"functools\.wraps",
            r"__call__\s*\("
        ]
        
        for i, indicator in enumerate(decorator_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="decorator",
                    pattern_name=f"decorator_pattern_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 200),
                    description="Decorator pattern implementation",
                    complexity_score=0.6,
                    usage_frequency=1,
                    temporal_stability=0.9
                ))
        
        return patterns
    
    async def _detect_async_patterns(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect asynchronous programming patterns"""
        patterns = []
        
        async_indicators = [
            r"async\s+def\s+\w+",
            r"await\s+\w+",
            r"asyncio\.\w+",
            r"aiohttp\.\w+",
            r"async\s+with\s+"
        ]
        
        for i, indicator in enumerate(async_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="async_patterns",
                    pattern_name=f"async_implementation_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 150),
                    description="Asynchronous programming pattern",
                    complexity_score=0.7,
                    usage_frequency=1,
                    temporal_stability=0.8
                ))
        
        return patterns
    
    async def _detect_error_handling_patterns(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect error handling patterns"""
        patterns = []
        
        error_indicators = [
            r"try:\s*\n.*except",
            r"raise\s+\w+",
            r"logging\.\w+",
            r"logger\.\w+",
            r"@retry",
            r"except\s+\w+Error"
        ]
        
        for i, indicator in enumerate(error_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="error_handling",
                    pattern_name=f"error_handling_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 200),
                    description="Error handling pattern",
                    complexity_score=0.5,
                    usage_frequency=1,
                    temporal_stability=0.9
                ))
        
        return patterns
    
    async def _detect_api_patterns(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect API design patterns"""
        patterns = []
        
        api_indicators = [
            r"@app\.\w+\(",
            r"@router\.\w+\(",
            r"@api\.\w+\(",
            r"FastAPI\(",
            r"@endpoint",
            r"request:\s*Request",
            r"response:\s*Response"
        ]
        
        for i, indicator in enumerate(api_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="api_patterns",
                    pattern_name=f"api_design_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 300),
                    description="API design pattern",
                    complexity_score=0.6,
                    usage_frequency=1,
                    temporal_stability=0.8
                ))
        
        return patterns
    
    async def _detect_configuration_patterns(self, file_path: str, content: str) -> List[CodePattern]:
        """Detect configuration management patterns"""
        patterns = []
        
        config_indicators = [
            r"class\s+\w*Config\w*",
            r"from\s+config\s+import",
            r"os\.environ\.",
            r"getenv\(",
            r"@dataclass",
            r"pydantic\.\w+",
            r"settings\.\w+"
        ]
        
        for i, indicator in enumerate(config_indicators):
            matches = re.finditer(indicator, content, re.MULTILINE)
            for match in matches:
                patterns.append(CodePattern(
                    pattern_type="configuration_patterns",
                    pattern_name=f"config_pattern_{i}",
                    file_path=file_path,
                    code_snippet=self._extract_context(content, match.start(), 200),
                    description="Configuration management pattern",
                    complexity_score=0.4,
                    usage_frequency=1,
                    temporal_stability=0.9
                ))
        
        return patterns
    
    def _extract_context(self, content: str, position: int, context_size: int = 200) -> str:
        """Extract code context around a position"""
        start = max(0, position - context_size // 2)
        end = min(len(content), position + context_size // 2)
        return content[start:end].strip()

class RepositoryAnalyzer:
    """Main repository analyzer that orchestrates all analysis components"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_client = GitHubAPIClient(github_token)
        self.pattern_extractor = CodePatternExtractor()
        self.analysis_cache: Dict[str, RepositoryAnalysis] = {}
        
    async def analyze_repository(self, repository_url: str, config: Dict[str, Any]) -> RepositoryAnalysis:
        """Analyze a complete repository"""
        logger.info(f"Starting analysis of repository: {repository_url}")
        
        # Parse repository URL
        owner, repo = self._parse_github_url(repository_url)
        if not owner or not repo:
            raise ValueError(f"Invalid GitHub URL: {repository_url}")
        
        # Check cache
        cache_key = f"{owner}/{repo}"
        if cache_key in self.analysis_cache:
            cached_analysis = self.analysis_cache[cache_key]
            if self._is_analysis_fresh(cached_analysis, config.get('cache_duration_hours', 24)):
                logger.info(f"Using cached analysis for {cache_key}")
                return cached_analysis
        
        # Get repository information
        repo_info = await self.github_client.get_repository_info(owner, repo)
        if not repo_info:
            raise ValueError(f"Could not fetch repository information for {repository_url}")
        
        # Initialize analysis
        analysis = RepositoryAnalysis(
            repository_url=repository_url,
            repository_name=f"{owner}/{repo}",
            analysis_timestamp=datetime.now(),
            patterns_extracted=[],
            architectural_insights={},
            temporal_evolution={},
            knowledge_domains=config.get('knowledge_domains', []),
            confidence_metrics={},
            integration_points=[]
        )
        
        # Analyze repository contents
        await self._analyze_code_structure(analysis, owner, repo, config)
        await self._analyze_documentation(analysis, owner, repo, config)
        await self._analyze_temporal_evolution(analysis, owner, repo, config)
        await self._analyze_community_patterns(analysis, owner, repo, config)
        
        # Calculate confidence metrics
        analysis.confidence_metrics = self._calculate_confidence_metrics(analysis)
        
        # Generate integration points
        analysis.integration_points = self._generate_integration_points(analysis)
        
        # Cache analysis
        self.analysis_cache[cache_key] = analysis
        
        logger.info(f"Completed analysis of {repository_url} - {len(analysis.patterns_extracted)} patterns extracted")
        return analysis
    
    async def _analyze_code_structure(self, analysis: RepositoryAnalysis, owner: str, repo: str, config: Dict[str, Any]):
        """Analyze code structure and extract patterns"""
        logger.info(f"Analyzing code structure for {owner}/{repo}")
        
        # Get repository contents
        contents = await self.github_client.get_repository_contents(owner, repo)
        
        # Filter for code files
        code_files = self._filter_code_files(contents)
        
        # Limit analysis based on priority
        max_files = config.get('max_files_to_analyze', 50)
        code_files = code_files[:max_files]
        
        # Analyze each code file
        all_patterns = []
        for file_info in code_files:
            if file_info['type'] == 'file':
                file_content = await self.github_client.get_file_content(owner, repo, file_info['path'])
                if file_content:
                    patterns = await self.pattern_extractor.extract_patterns_from_file(
                        file_info['path'], file_content
                    )
                    all_patterns.extend(patterns)
        
        # Convert patterns to dictionaries for storage
        analysis.patterns_extracted = [asdict(pattern) for pattern in all_patterns]
        
        # Generate architectural insights
        analysis.architectural_insights = self._generate_architectural_insights(all_patterns)
    
    async def _analyze_documentation(self, analysis: RepositoryAnalysis, owner: str, repo: str, config: Dict[str, Any]):
        """Analyze documentation for patterns and insights"""
        logger.info(f"Analyzing documentation for {owner}/{repo}")
        
        # Get README and other documentation files
        doc_files = ['README.md', 'ARCHITECTURE.md', 'docs/README.md', 'documentation/README.md']
        
        documentation_insights = {
            "architecture_descriptions": [],
            "api_documentation_quality": 0.0,
            "setup_complexity": 0.0,
            "maintenance_indicators": []
        }
        
        for doc_file in doc_files:
            content = await self.github_client.get_file_content(owner, repo, doc_file)
            if content:
                # Analyze documentation content
                doc_analysis = self._analyze_documentation_content(content)
                documentation_insights["architecture_descriptions"].extend(
                    doc_analysis.get("architecture_mentions", [])
                )
        
        analysis.architectural_insights["documentation"] = documentation_insights
    
    async def _analyze_temporal_evolution(self, analysis: RepositoryAnalysis, owner: str, repo: str, config: Dict[str, Any]):
        """Analyze temporal evolution patterns"""
        logger.info(f"Analyzing temporal evolution for {owner}/{repo}")
        
        # Get commits from last 6 months
        since_date = datetime.now() - timedelta(days=180)
        commits = await self.github_client.get_commits(owner, repo, since=since_date, limit=200)
        
        temporal_analysis = {
            "development_velocity": 0.0,
            "code_stability": 0.0,
            "feature_evolution_patterns": [],
            "deprecation_indicators": [],
            "growth_trends": {}
        }
        
        if commits:
            # Analyze commit patterns
            temporal_analysis["development_velocity"] = len(commits) / 180  # commits per day
            
            # Analyze commit messages for patterns
            commit_messages = [commit['commit']['message'] for commit in commits]
            temporal_analysis["feature_evolution_patterns"] = self._analyze_commit_patterns(commit_messages)
        
        analysis.temporal_evolution = temporal_analysis
    
    async def _analyze_community_patterns(self, analysis: RepositoryAnalysis, owner: str, repo: str, config: Dict[str, Any]):
        """Analyze community and usage patterns"""
        logger.info(f"Analyzing community patterns for {owner}/{repo}")
        
        # Get issues for pattern analysis
        issues = await self.github_client.get_issues(owner, repo, limit=100)
        
        community_insights = {
            "common_issues": [],
            "solution_patterns": [],
            "community_engagement": 0.0,
            "support_quality": 0.0
        }
        
        if issues:
            # Analyze issue patterns
            issue_titles = [issue['title'] for issue in issues]
            community_insights["common_issues"] = self._extract_common_issues(issue_titles)
            
            # Calculate community engagement
            open_issues = len([i for i in issues if i['state'] == 'open'])
            total_issues = len(issues)
            community_insights["community_engagement"] = 1 - (open_issues / total_issues) if total_issues > 0 else 0.5
        
        analysis.architectural_insights["community"] = community_insights
    
    def _filter_code_files(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter for relevant code files"""
        code_extensions = {'.py', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.rs', '.rb', '.php'}
        
        code_files = []
        for item in contents:
            if item['type'] == 'file':
                file_path = item['path']
                file_ext = Path(file_path).suffix.lower()
                if file_ext in code_extensions:
                    code_files.append(item)
        
        # Sort by relevance (main files first)
        priority_files = ['main.py', 'app.py', 'server.py', 'index.js', 'main.go']
        code_files.sort(key=lambda x: 0 if x['name'] in priority_files else 1)
        
        return code_files
    
    def _generate_architectural_insights(self, patterns: List[CodePattern]) -> Dict[str, Any]:
        """Generate architectural insights from extracted patterns"""
        
        # Group patterns by type
        pattern_groups = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in pattern_groups:
                pattern_groups[pattern_type] = []
            pattern_groups[pattern_type].append(pattern)
        
        insights = {
            "pattern_distribution": {pt: len(patterns) for pt, patterns in pattern_groups.items()},
            "complexity_assessment": {
                "average_complexity": sum(p.complexity_score for p in patterns) / len(patterns) if patterns else 0.0,
                "high_complexity_areas": [p.file_path for p in patterns if p.complexity_score > 0.8]
            },
            "architectural_style": self._determine_architectural_style(pattern_groups),
            "quality_indicators": {
                "pattern_usage_diversity": len(pattern_groups),
                "code_organization_score": self._calculate_organization_score(patterns)
            }
        }
        
        return insights
    
    def _determine_architectural_style(self, pattern_groups: Dict[str, List[CodePattern]]) -> str:
        """Determine predominant architectural style"""
        
        # Simple heuristics for architectural style detection
        if 'factory' in pattern_groups and 'singleton' in pattern_groups:
            return "object_oriented_with_patterns"
        elif 'async_patterns' in pattern_groups and len(pattern_groups.get('async_patterns', [])) > 10:
            return "async_event_driven"
        elif 'api_patterns' in pattern_groups:
            return "service_oriented"
        elif 'decorator' in pattern_groups:
            return "functional_with_decorators"
        else:
            return "procedural_or_mixed"
    
    def _calculate_organization_score(self, patterns: List[CodePattern]) -> float:
        """Calculate code organization score"""
        if not patterns:
            return 0.5
        
        # Score based on pattern distribution and file organization
        unique_files = len(set(p.file_path for p in patterns))
        total_patterns = len(patterns)
        
        # Higher score for well-distributed patterns across files
        distribution_score = min(1.0, unique_files / (total_patterns * 0.5))
        
        # Score based on temporal stability
        stability_score = sum(p.temporal_stability for p in patterns) / len(patterns)
        
        return (distribution_score * 0.6 + stability_score * 0.4)
    
    def _analyze_documentation_content(self, content: str) -> Dict[str, Any]:
        """Analyze documentation content for patterns"""
        
        architecture_keywords = [
            'microservices', 'monolithic', 'distributed', 'api', 'rest', 'graphql',
            'database', 'architecture', 'design', 'pattern', 'framework'
        ]
        
        doc_analysis = {
            "architecture_mentions": [],
            "api_documentation_present": False,
            "setup_instructions_present": False
        }
        
        content_lower = content.lower()
        
        # Find architecture mentions
        for keyword in architecture_keywords:
            if keyword in content_lower:
                doc_analysis["architecture_mentions"].append(keyword)
        
        # Check for API documentation
        api_indicators = ['api', 'endpoint', 'swagger', 'openapi']
        doc_analysis["api_documentation_present"] = any(indicator in content_lower for indicator in api_indicators)
        
        # Check for setup instructions
        setup_indicators = ['install', 'setup', 'getting started', 'quick start']
        doc_analysis["setup_instructions_present"] = any(indicator in content_lower for indicator in setup_indicators)
        
        return doc_analysis
    
    def _analyze_commit_patterns(self, commit_messages: List[str]) -> List[str]:
        """Analyze commit patterns for feature evolution"""
        
        # Common commit patterns
        patterns = {
            'feature_additions': r'(add|feat|feature)',
            'bug_fixes': r'(fix|bug|patch)',
            'refactoring': r'(refactor|cleanup|improve)',
            'documentation': r'(doc|readme|comment)',
            'performance': r'(perf|optimize|speed)',
            'security': r'(security|auth|secure)'
        }
        
        detected_patterns = []
        for pattern_name, pattern_regex in patterns.items():
            matches = sum(1 for msg in commit_messages if re.search(pattern_regex, msg.lower()))
            if matches > len(commit_messages) * 0.1:  # If >10% of commits match
                detected_patterns.append(f"{pattern_name}: {matches} occurrences")
        
        return detected_patterns
    
    def _extract_common_issues(self, issue_titles: List[str]) -> List[str]:
        """Extract common issue patterns"""
        
        # Common issue keywords
        issue_patterns = {
            'performance': r'(slow|performance|speed|lag)',
            'installation': r'(install|setup|dependency)',
            'configuration': r'(config|setting|environment)',
            'compatibility': r'(compatible|version|support)',
            'documentation': r'(doc|documentation|example)',
            'bug': r'(bug|error|crash|fail)'
        }
        
        common_issues = []
        for pattern_name, pattern_regex in issue_patterns.items():
            matches = sum(1 for title in issue_titles if re.search(pattern_regex, title.lower()))
            if matches > 2:  # If pattern appears in multiple issues
                common_issues.append(f"{pattern_name}: {matches} issues")
        
        return common_issues
    
    def _calculate_confidence_metrics(self, analysis: RepositoryAnalysis) -> Dict[str, float]:
        """Calculate confidence metrics for the analysis"""
        
        metrics = {
            "pattern_extraction_confidence": 0.0,
            "architectural_insight_confidence": 0.0,
            "temporal_analysis_confidence": 0.0,
            "overall_confidence": 0.0
        }
        
        # Pattern extraction confidence
        if analysis.patterns_extracted:
            pattern_count = len(analysis.patterns_extracted)
            pattern_diversity = len(set(p['pattern_type'] for p in analysis.patterns_extracted))
            metrics["pattern_extraction_confidence"] = min(1.0, (pattern_count * 0.1 + pattern_diversity * 0.2))
        
        # Architectural insight confidence
        architectural_completeness = 0.0
        if analysis.architectural_insights:
            components = ['pattern_distribution', 'complexity_assessment', 'architectural_style']
            present_components = sum(1 for comp in components if comp in analysis.architectural_insights)
            architectural_completeness = present_components / len(components)
        metrics["architectural_insight_confidence"] = architectural_completeness
        
        # Temporal analysis confidence
        if analysis.temporal_evolution:
            temporal_completeness = len(analysis.temporal_evolution) / 5  # Expected 5 components
            metrics["temporal_analysis_confidence"] = min(1.0, temporal_completeness)
        
        # Overall confidence
        metrics["overall_confidence"] = (
            metrics["pattern_extraction_confidence"] * 0.4 +
            metrics["architectural_insight_confidence"] * 0.3 +
            metrics["temporal_analysis_confidence"] * 0.3
        )
        
        return metrics
    
    def _generate_integration_points(self, analysis: RepositoryAnalysis) -> List[Dict[str, Any]]:
        """Generate integration points for knowledge synthesis"""
        
        integration_points = []
        
        # Pattern-based integration points
        for pattern in analysis.patterns_extracted:
            integration_points.append({
                "type": "code_pattern",
                "source": "pattern_extraction",
                "data": {
                    "pattern_type": pattern['pattern_type'],
                    "file_path": pattern['file_path'],
                    "confidence": pattern['temporal_stability']
                },
                "knowledge_domain": self._map_pattern_to_domain(pattern['pattern_type'])
            })
        
        # Architectural integration points
        if analysis.architectural_insights:
            integration_points.append({
                "type": "architectural_insight",
                "source": "architecture_analysis",
                "data": analysis.architectural_insights,
                "knowledge_domain": "system_architecture"
            })
        
        # Temporal evolution integration points
        if analysis.temporal_evolution:
            integration_points.append({
                "type": "temporal_evolution",
                "source": "evolution_analysis", 
                "data": analysis.temporal_evolution,
                "knowledge_domain": "software_evolution"
            })
        
        return integration_points
    
    def _map_pattern_to_domain(self, pattern_type: str) -> str:
        """Map pattern types to knowledge domains"""
        
        domain_mapping = {
            "singleton": "design_patterns",
            "factory": "creational_patterns",
            "observer": "behavioral_patterns",
            "decorator": "structural_patterns",
            "async_patterns": "concurrency_patterns",
            "error_handling": "reliability_patterns",
            "api_patterns": "integration_patterns",
            "configuration_patterns": "configuration_management"
        }
        
        return domain_mapping.get(pattern_type, "general_patterns")
    
    def _parse_github_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse GitHub URL to extract owner and repository"""
        
        # Handle different GitHub URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'github\.com/([^/]+)/([^/]+)/.*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)
        
        return None, None
    
    def _is_analysis_fresh(self, analysis: RepositoryAnalysis, cache_duration_hours: int) -> bool:
        """Check if cached analysis is still fresh"""
        
        cache_expiry = analysis.analysis_timestamp + timedelta(hours=cache_duration_hours)
        return datetime.now() < cache_expiry

async def main():
    """Main function to run repository analysis"""
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "github_sources.yml"
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize analyzer
    analyzer = RepositoryAnalyzer()
    
    # Analyze repositories from configuration
    for category_name, category_config in config.get('repository_categories', {}).items():
        logger.info(f"Analyzing repositories in category: {category_name}")
        
        for repo_config in category_config.get('repositories', []):
            try:
                repo_url = repo_config['url']
                repo_analysis_config = {
                    'focus_areas': repo_config.get('focus_areas', []),
                    'knowledge_domains': repo_config.get('knowledge_domains', []),
                    'analysis_priority': repo_config.get('analysis_priority', 'medium'),
                    'max_files_to_analyze': 100 if repo_config.get('analysis_priority') == 'high' else 50,
                    'cache_duration_hours': 24
                }
                
                # Perform analysis
                analysis = await analyzer.analyze_repository(repo_url, repo_analysis_config)
                
                # Save analysis results
                output_dir = Path(__file__).parent.parent / "analysis_results"
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / f"{analysis.repository_name.replace('/', '_')}_analysis.json"
                
                # Convert analysis to JSON-serializable format
                analysis_dict = asdict(analysis)
                analysis_dict['analysis_timestamp'] = analysis.analysis_timestamp.isoformat()
                
                with open(output_file, 'w') as f:
                    json.dump(analysis_dict, f, indent=2)
                
                logger.info(f"Analysis saved to: {output_file}")
                
            except Exception as e:
                logger.error(f"Failed to analyze repository {repo_config['url']}: {str(e)}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
