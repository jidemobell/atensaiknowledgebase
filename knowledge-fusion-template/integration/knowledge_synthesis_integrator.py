"""
Knowledge Synthesis Integration Service
Integrates GitHub repository analysis with the novel temporal knowledge synthesis system
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import aiofiles
import yaml

# Import our novel architecture components
from main_novel_architecture import (
    TemporalKnowledgeNode, 
    KnowledgeTemporalState,
    KnowledgeConfidenceSource,
    KnowledgeRelationship,
    novel_synthesis_engine
)

# Import GitHub analyzer
from tools.github_repository_analyzer import RepositoryAnalyzer, RepositoryAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeSynthesisIntegrator:
    """
    Integrates external repository analysis with temporal knowledge synthesis
    Creates knowledge nodes from repository patterns and insights
    """
    
    def __init__(self):
        self.github_analyzer = RepositoryAnalyzer()
        self.synthesis_engine = novel_synthesis_engine
        self.integration_history: List[Dict[str, Any]] = []
        
    async def integrate_repository_knowledge(self, repository_url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete integration pipeline: analyze repository and create knowledge nodes
        """
        logger.info(f"Starting knowledge integration for: {repository_url}")
        
        try:
            # Step 1: Analyze repository
            analysis = await self.github_analyzer.analyze_repository(repository_url, config)
            
            # Step 2: Transform analysis into temporal knowledge nodes
            knowledge_nodes = await self._transform_to_knowledge_nodes(analysis)
            
            # Step 3: Discover cross-repository relationships
            relationships = await self._discover_cross_repo_relationships(analysis, knowledge_nodes)
            
            # Step 4: Integrate into synthesis engine
            integration_results = await self._integrate_with_synthesis_engine(
                knowledge_nodes, relationships
            )
            
            # Step 5: Generate predictive insights
            predictive_insights = await self._generate_predictive_insights(analysis)
            
            # Step 6: Record integration
            integration_record = {
                "repository_url": repository_url,
                "integration_timestamp": datetime.now().isoformat(),
                "knowledge_nodes_created": len(knowledge_nodes),
                "relationships_discovered": len(relationships),
                "confidence_score": analysis.confidence_metrics.get('overall_confidence', 0.5),
                "predictive_insights": predictive_insights,
                "integration_status": "success"
            }
            
            self.integration_history.append(integration_record)
            
            logger.info(f"Successfully integrated {repository_url}: {len(knowledge_nodes)} nodes, {len(relationships)} relationships")
            
            return integration_record
            
        except Exception as e:
            logger.error(f"Failed to integrate repository {repository_url}: {str(e)}")
            error_record = {
                "repository_url": repository_url,
                "integration_timestamp": datetime.now().isoformat(),
                "integration_status": "failed",
                "error": str(e)
            }
            self.integration_history.append(error_record)
            return error_record
    
    async def _transform_to_knowledge_nodes(self, analysis: RepositoryAnalysis) -> List[TemporalKnowledgeNode]:
        """
        Transform repository analysis into temporal knowledge nodes
        """
        knowledge_nodes = []
        
        # Create nodes from code patterns
        for pattern_data in analysis.patterns_extracted:
            node = await self._create_pattern_knowledge_node(pattern_data, analysis)
            if node:
                knowledge_nodes.append(node)
        
        # Create nodes from architectural insights
        if analysis.architectural_insights:
            arch_node = await self._create_architectural_knowledge_node(analysis)
            if arch_node:
                knowledge_nodes.append(arch_node)
        
        # Create nodes from temporal evolution data
        if analysis.temporal_evolution:
            temporal_node = await self._create_temporal_evolution_node(analysis)
            if temporal_node:
                knowledge_nodes.append(temporal_node)
        
        # Create nodes from community patterns
        if analysis.architectural_insights.get('community'):
            community_node = await self._create_community_knowledge_node(analysis)
            if community_node:
                knowledge_nodes.append(community_node)
        
        return knowledge_nodes
    
    async def _create_pattern_knowledge_node(self, pattern_data: Dict[str, Any], analysis: RepositoryAnalysis) -> Optional[TemporalKnowledgeNode]:
        """
        Create a knowledge node from a code pattern
        """
        try:
            # Determine temporal state based on pattern characteristics
            temporal_state = self._determine_pattern_temporal_state(pattern_data)
            
            # Create confidence sources
            confidence_sources = [
                KnowledgeConfidenceSource(
                    source_id=f"github_analysis_{analysis.repository_name}",
                    reliability_score=analysis.confidence_metrics.get('pattern_extraction_confidence', 0.7),
                    recency_weight=self._calculate_recency_weight(analysis.analysis_timestamp),
                    domain_expertise=0.8,  # High for code analysis
                    consensus_factor=pattern_data.get('usage_frequency', 1) / 10.0,
                    evolution_stability=pattern_data.get('temporal_stability', 0.5)
                )
            ]
            
            # Generate node ID
            node_id = f"pattern_{analysis.repository_name.replace('/', '_')}_{pattern_data['pattern_type']}_{hash(pattern_data['file_path']) % 10000}"
            
            # Create descriptive content
            content = f"""
            Code Pattern: {pattern_data['pattern_type']} in {analysis.repository_name}
            Location: {pattern_data['file_path']}
            Description: {pattern_data['description']}
            Complexity Score: {pattern_data['complexity_score']}
            Code Sample: {pattern_data['code_snippet'][:200]}...
            Repository Context: {analysis.repository_url}
            """
            
            # Create predictive indicators
            predictive_indicators = {
                "pattern_adoption_trend": pattern_data.get('usage_frequency', 0) / 10.0,
                "complexity_evolution": 1.0 - pattern_data.get('complexity_score', 0.5),
                "stability_projection": pattern_data.get('temporal_stability', 0.5)
            }
            
            node = TemporalKnowledgeNode(
                node_id=node_id,
                content=content.strip(),
                domain=self._map_pattern_to_domain(pattern_data['pattern_type']),
                temporal_state=temporal_state,
                creation_time=analysis.analysis_timestamp,
                last_validated=analysis.analysis_timestamp,
                confidence_sources=confidence_sources,
                related_nodes=[],
                evolution_history=[{
                    "type": "pattern_extraction",
                    "timestamp": analysis.analysis_timestamp.isoformat(),
                    "source": "github_repository_analysis",
                    "details": f"Extracted from {analysis.repository_name}"
                }],
                predictive_indicators=predictive_indicators,
                usage_patterns={
                    "source_repository": analysis.repository_name,
                    "pattern_frequency": pattern_data.get('usage_frequency', 1),
                    "complexity_category": self._categorize_complexity(pattern_data.get('complexity_score', 0.5))
                }
            )
            
            return node
            
        except Exception as e:
            logger.warning(f"Failed to create pattern knowledge node: {str(e)}")
            return None
    
    async def _create_architectural_knowledge_node(self, analysis: RepositoryAnalysis) -> Optional[TemporalKnowledgeNode]:
        """
        Create a knowledge node from architectural insights
        """
        try:
            arch_insights = analysis.architectural_insights
            
            # Create confidence sources
            confidence_sources = [
                KnowledgeConfidenceSource(
                    source_id=f"architectural_analysis_{analysis.repository_name}",
                    reliability_score=analysis.confidence_metrics.get('architectural_insight_confidence', 0.8),
                    recency_weight=self._calculate_recency_weight(analysis.analysis_timestamp),
                    domain_expertise=0.9,  # Very high for architectural analysis
                    consensus_factor=0.8,
                    evolution_stability=0.7
                )
            ]
            
            node_id = f"architecture_{analysis.repository_name.replace('/', '_')}_{hash(str(arch_insights)) % 10000}"
            
            # Create architectural summary
            content = f"""
            Architectural Analysis: {analysis.repository_name}
            
            Architectural Style: {arch_insights.get('architectural_style', 'Unknown')}
            
            Pattern Distribution:
            {json.dumps(arch_insights.get('pattern_distribution', {}), indent=2)}
            
            Complexity Assessment:
            - Average Complexity: {arch_insights.get('complexity_assessment', {}).get('average_complexity', 0.0):.2f}
            - High Complexity Areas: {len(arch_insights.get('complexity_assessment', {}).get('high_complexity_areas', []))}
            
            Quality Indicators:
            - Pattern Usage Diversity: {arch_insights.get('quality_indicators', {}).get('pattern_usage_diversity', 0)}
            - Code Organization Score: {arch_insights.get('quality_indicators', {}).get('code_organization_score', 0.0):.2f}
            
            Repository: {analysis.repository_url}
            """
            
            # Determine temporal state based on architecture maturity
            avg_complexity = arch_insights.get('complexity_assessment', {}).get('average_complexity', 0.5)
            if avg_complexity > 0.8:
                temporal_state = KnowledgeTemporalState.ESTABLISHED
            elif avg_complexity > 0.5:
                temporal_state = KnowledgeTemporalState.EVOLVING
            else:
                temporal_state = KnowledgeTemporalState.EMERGING
            
            predictive_indicators = {
                "architecture_maturity": avg_complexity,
                "scalability_potential": arch_insights.get('quality_indicators', {}).get('code_organization_score', 0.5),
                "evolution_readiness": 1.0 - avg_complexity
            }
            
            node = TemporalKnowledgeNode(
                node_id=node_id,
                content=content.strip(),
                domain="software_architecture",
                temporal_state=temporal_state,
                creation_time=analysis.analysis_timestamp,
                last_validated=analysis.analysis_timestamp,
                confidence_sources=confidence_sources,
                related_nodes=[],
                evolution_history=[{
                    "type": "architectural_analysis",
                    "timestamp": analysis.analysis_timestamp.isoformat(),
                    "source": "github_repository_analysis",
                    "architectural_style": arch_insights.get('architectural_style', 'unknown')
                }],
                predictive_indicators=predictive_indicators,
                usage_patterns={
                    "repository_size": "large" if len(analysis.patterns_extracted) > 50 else "medium" if len(analysis.patterns_extracted) > 20 else "small",
                    "architectural_complexity": "high" if avg_complexity > 0.7 else "medium" if avg_complexity > 0.4 else "low"
                }
            )
            
            return node
            
        except Exception as e:
            logger.warning(f"Failed to create architectural knowledge node: {str(e)}")
            return None
    
    async def _create_temporal_evolution_node(self, analysis: RepositoryAnalysis) -> Optional[TemporalKnowledgeNode]:
        """
        Create knowledge node from temporal evolution data
        """
        try:
            temporal_data = analysis.temporal_evolution
            
            confidence_sources = [
                KnowledgeConfidenceSource(
                    source_id=f"temporal_analysis_{analysis.repository_name}",
                    reliability_score=analysis.confidence_metrics.get('temporal_analysis_confidence', 0.7),
                    recency_weight=1.0,  # Very recent data
                    domain_expertise=0.8,
                    consensus_factor=0.7,
                    evolution_stability=temporal_data.get('code_stability', 0.5)
                )
            ]
            
            node_id = f"evolution_{analysis.repository_name.replace('/', '_')}_{hash(str(temporal_data)) % 10000}"
            
            content = f"""
            Temporal Evolution Analysis: {analysis.repository_name}
            
            Development Velocity: {temporal_data.get('development_velocity', 0.0):.3f} commits/day
            Code Stability: {temporal_data.get('code_stability', 0.0):.2f}
            
            Feature Evolution Patterns:
            {chr(10).join(temporal_data.get('feature_evolution_patterns', []))}
            
            Growth Trends:
            {json.dumps(temporal_data.get('growth_trends', {}), indent=2)}
            
            Repository: {analysis.repository_url}
            Analysis Date: {analysis.analysis_timestamp.isoformat()}
            """
            
            # Determine temporal state based on development activity
            dev_velocity = temporal_data.get('development_velocity', 0.0)
            if dev_velocity > 2.0:
                temporal_state = KnowledgeTemporalState.EVOLVING
            elif dev_velocity > 0.5:
                temporal_state = KnowledgeTemporalState.ESTABLISHED
            else:
                temporal_state = KnowledgeTemporalState.DEPRECATED
            
            predictive_indicators = {
                "development_momentum": min(1.0, dev_velocity / 5.0),
                "stability_trend": temporal_data.get('code_stability', 0.5),
                "future_activity_projection": min(1.0, dev_velocity / 3.0)
            }
            
            node = TemporalKnowledgeNode(
                node_id=node_id,
                content=content.strip(),
                domain="software_evolution",
                temporal_state=temporal_state,
                creation_time=analysis.analysis_timestamp,
                last_validated=analysis.analysis_timestamp,
                confidence_sources=confidence_sources,
                predictive_indicators=predictive_indicators,
                usage_patterns={
                    "development_activity": "high" if dev_velocity > 1.0 else "medium" if dev_velocity > 0.3 else "low",
                    "stability_category": "stable" if temporal_data.get('code_stability', 0) > 0.7 else "evolving"
                }
            )
            
            return node
            
        except Exception as e:
            logger.warning(f"Failed to create temporal evolution node: {str(e)}")
            return None
    
    async def _create_community_knowledge_node(self, analysis: RepositoryAnalysis) -> Optional[TemporalKnowledgeNode]:
        """
        Create knowledge node from community patterns
        """
        try:
            community_data = analysis.architectural_insights.get('community', {})
            
            confidence_sources = [
                KnowledgeConfidenceSource(
                    source_id=f"community_analysis_{analysis.repository_name}",
                    reliability_score=0.8,
                    recency_weight=self._calculate_recency_weight(analysis.analysis_timestamp),
                    domain_expertise=0.7,
                    consensus_factor=community_data.get('community_engagement', 0.5),
                    evolution_stability=0.6
                )
            ]
            
            node_id = f"community_{analysis.repository_name.replace('/', '_')}_{hash(str(community_data)) % 10000}"
            
            content = f"""
            Community Analysis: {analysis.repository_name}
            
            Community Engagement: {community_data.get('community_engagement', 0.0):.2f}
            Support Quality: {community_data.get('support_quality', 0.0):.2f}
            
            Common Issues:
            {chr(10).join(community_data.get('common_issues', []))}
            
            Solution Patterns:
            {chr(10).join(community_data.get('solution_patterns', []))}
            
            Repository: {analysis.repository_url}
            """
            
            # Determine temporal state based on community activity
            engagement = community_data.get('community_engagement', 0.5)
            if engagement > 0.8:
                temporal_state = KnowledgeTemporalState.ESTABLISHED
            elif engagement > 0.5:
                temporal_state = KnowledgeTemporalState.EVOLVING
            else:
                temporal_state = KnowledgeTemporalState.EMERGING
            
            predictive_indicators = {
                "community_growth_potential": engagement,
                "support_sustainability": community_data.get('support_quality', 0.5),
                "adoption_likelihood": (engagement + community_data.get('support_quality', 0.5)) / 2.0
            }
            
            node = TemporalKnowledgeNode(
                node_id=node_id,
                content=content.strip(),
                domain="community_patterns",
                temporal_state=temporal_state,
                creation_time=analysis.analysis_timestamp,
                last_validated=analysis.analysis_timestamp,
                confidence_sources=confidence_sources,
                predictive_indicators=predictive_indicators,
                usage_patterns={
                    "community_size": "large" if engagement > 0.7 else "medium" if engagement > 0.4 else "small",
                    "support_level": "high" if community_data.get('support_quality', 0) > 0.7 else "medium"
                }
            )
            
            return node
            
        except Exception as e:
            logger.warning(f"Failed to create community knowledge node: {str(e)}")
            return None
    
    async def _discover_cross_repo_relationships(self, analysis: RepositoryAnalysis, 
                                               knowledge_nodes: List[TemporalKnowledgeNode]) -> List[KnowledgeRelationship]:
        """
        Discover relationships between repositories and existing knowledge
        """
        relationships = []
        
        # Get existing knowledge nodes from synthesis engine
        existing_nodes = self.synthesis_engine.knowledge_graph.nodes
        
        for new_node in knowledge_nodes:
            for existing_id, existing_node in existing_nodes.items():
                relationship = await self._analyze_node_relationship(new_node, existing_node)
                if relationship:
                    relationships.append(relationship)
        
        return relationships
    
    async def _analyze_node_relationship(self, node1: TemporalKnowledgeNode, 
                                       node2: TemporalKnowledgeNode) -> Optional[KnowledgeRelationship]:
        """
        Analyze relationship between two knowledge nodes
        """
        # Domain similarity
        domain_similarity = 1.0 if node1.domain == node2.domain else 0.3
        
        # Content similarity (simplified)
        content_words1 = set(node1.content.lower().split())
        content_words2 = set(node2.content.lower().split())
        content_similarity = len(content_words1.intersection(content_words2)) / len(content_words1.union(content_words2))
        
        # Temporal alignment
        time_diff = abs((node1.creation_time - node2.creation_time).total_seconds())
        temporal_alignment = max(0, 1 - (time_diff / (365 * 24 * 3600)))  # 1 year normalization
        
        # Overall relationship strength
        relationship_strength = (domain_similarity * 0.4 + content_similarity * 0.4 + temporal_alignment * 0.2)
        
        if relationship_strength > 0.6:
            relationship_type = self._determine_relationship_type(node1, node2, domain_similarity, content_similarity)
            
            return KnowledgeRelationship(
                from_node=node1.node_id,
                to_node=node2.node_id,
                relationship_type=relationship_type,
                strength=relationship_strength,
                temporal_stability=min(node1.predictive_indicators.get('stability_projection', 0.5),
                                     node2.predictive_indicators.get('stability_projection', 0.5)),
                evidence_sources=[f"cross_repo_analysis_{datetime.now().isoformat()}"],
                discovery_method="automated_cross_repository_analysis"
            )
        
        return None
    
    async def _integrate_with_synthesis_engine(self, knowledge_nodes: List[TemporalKnowledgeNode], 
                                             relationships: List[KnowledgeRelationship]) -> Dict[str, Any]:
        """
        Integrate knowledge nodes and relationships with the synthesis engine
        """
        integration_results = {
            "nodes_added": 0,
            "relationships_added": 0,
            "errors": []
        }
        
        # Add knowledge nodes
        for node in knowledge_nodes:
            try:
                self.synthesis_engine.knowledge_graph.add_knowledge_node(node)
                integration_results["nodes_added"] += 1
            except Exception as e:
                integration_results["errors"].append(f"Failed to add node {node.node_id}: {str(e)}")
        
        # Add relationships
        for relationship in relationships:
            try:
                self.synthesis_engine.knowledge_graph.relationships.append(relationship)
                integration_results["relationships_added"] += 1
            except Exception as e:
                integration_results["errors"].append(f"Failed to add relationship: {str(e)}")
        
        return integration_results
    
    async def _generate_predictive_insights(self, analysis: RepositoryAnalysis) -> List[Dict[str, Any]]:
        """
        Generate predictive insights from repository analysis
        """
        insights = []
        
        # Development velocity prediction
        dev_velocity = analysis.temporal_evolution.get('development_velocity', 0.0)
        if dev_velocity > 1.0:
            insights.append({
                "type": "development_trend",
                "insight": f"Repository {analysis.repository_name} shows high development velocity ({dev_velocity:.2f} commits/day)",
                "prediction": "Likely to introduce new patterns and architectural changes in next 3 months",
                "confidence": 0.8,
                "timeframe": "3_months"
            })
        
        # Pattern evolution prediction
        pattern_count = len(analysis.patterns_extracted)
        if pattern_count > 30:
            insights.append({
                "type": "pattern_evolution",
                "insight": f"Rich pattern library detected ({pattern_count} patterns)",
                "prediction": "High likelihood of pattern standardization and reuse opportunities",
                "confidence": 0.7,
                "timeframe": "6_months"
            })
        
        # Architecture maturity prediction
        arch_insights = analysis.architectural_insights
        if arch_insights.get('complexity_assessment', {}).get('average_complexity', 0) > 0.7:
            insights.append({
                "type": "architecture_maturity",
                "insight": "High architectural complexity detected",
                "prediction": "May benefit from refactoring and simplification efforts",
                "confidence": 0.75,
                "timeframe": "12_months"
            })
        
        return insights
    
    # Helper methods
    
    def _determine_pattern_temporal_state(self, pattern_data: Dict[str, Any]) -> KnowledgeTemporalState:
        """Determine temporal state of a pattern"""
        stability = pattern_data.get('temporal_stability', 0.5)
        complexity = pattern_data.get('complexity_score', 0.5)
        
        if stability > 0.8 and complexity > 0.6:
            return KnowledgeTemporalState.ESTABLISHED
        elif stability > 0.5:
            return KnowledgeTemporalState.EVOLVING
        elif complexity < 0.3:
            return KnowledgeTemporalState.DEPRECATED
        else:
            return KnowledgeTemporalState.EMERGING
    
    def _calculate_recency_weight(self, timestamp: datetime) -> float:
        """Calculate recency weight based on timestamp"""
        age_days = (datetime.now() - timestamp).days
        return max(0.1, 1.0 - (age_days / 365.0))  # Linear decay over 1 year
    
    def _map_pattern_to_domain(self, pattern_type: str) -> str:
        """Map pattern type to knowledge domain"""
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
    
    def _categorize_complexity(self, complexity_score: float) -> str:
        """Categorize complexity score"""
        if complexity_score > 0.8:
            return "high"
        elif complexity_score > 0.5:
            return "medium"
        else:
            return "low"
    
    def _determine_relationship_type(self, node1: TemporalKnowledgeNode, node2: TemporalKnowledgeNode,
                                   domain_similarity: float, content_similarity: float) -> str:
        """Determine the type of relationship between nodes"""
        
        if domain_similarity > 0.9 and content_similarity > 0.7:
            return "similar_implementation"
        elif domain_similarity > 0.9:
            return "domain_related"
        elif content_similarity > 0.6:
            return "content_overlap"
        elif node1.temporal_state != node2.temporal_state:
            return "temporal_evolution"
        else:
            return "cross_reference"

# Global integrator instance
knowledge_integrator = KnowledgeSynthesisIntegrator()

async def integrate_github_repositories():
    """
    Main function to integrate GitHub repositories with knowledge synthesis
    """
    logger.info("Starting GitHub repository integration process")
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "github_sources.yml"
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return
    
    async with aiofiles.open(config_path, 'r') as f:
        config_content = await f.read()
        config = yaml.safe_load(config_content)
    
    integration_results = []
    
    # Process repositories by priority
    for category_name, category_config in config.get('repository_categories', {}).items():
        logger.info(f"Processing category: {category_name}")
        
        for repo_config in category_config.get('repositories', []):
            repo_url = repo_config['url']
            
            # Create integration configuration
            integration_config = {
                'focus_areas': repo_config.get('focus_areas', []),
                'knowledge_domains': repo_config.get('knowledge_domains', []),
                'analysis_priority': repo_config.get('analysis_priority', 'medium'),
                'max_files_to_analyze': 100 if repo_config.get('analysis_priority') == 'high' else 50,
                'cache_duration_hours': 24
            }
            
            # Integrate repository
            result = await knowledge_integrator.integrate_repository_knowledge(repo_url, integration_config)
            integration_results.append(result)
            
            # Add delay between repositories to respect rate limits
            await asyncio.sleep(2)
    
    # Save integration summary
    summary = {
        "integration_timestamp": datetime.now().isoformat(),
        "total_repositories_processed": len(integration_results),
        "successful_integrations": len([r for r in integration_results if r.get('integration_status') == 'success']),
        "failed_integrations": len([r for r in integration_results if r.get('integration_status') == 'failed']),
        "total_knowledge_nodes": sum(r.get('knowledge_nodes_created', 0) for r in integration_results),
        "total_relationships": sum(r.get('relationships_discovered', 0) for r in integration_results),
        "results": integration_results
    }
    
    # Save summary
    output_dir = Path(__file__).parent.parent / "integration_results"
    output_dir.mkdir(exist_ok=True)
    
    summary_file = output_dir / f"integration_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    async with aiofiles.open(summary_file, 'w') as f:
        await f.write(json.dumps(summary, indent=2))
    
    logger.info(f"Integration complete. Summary saved to: {summary_file}")
    logger.info(f"Successfully integrated {summary['successful_integrations']}/{summary['total_repositories_processed']} repositories")
    logger.info(f"Created {summary['total_knowledge_nodes']} knowledge nodes and {summary['total_relationships']} relationships")

if __name__ == "__main__":
    asyncio.run(integrate_github_repositories())
