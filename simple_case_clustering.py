#!/usr/bin/env python3
"""
Simple Case Similarity System (No External Dependencies)
Groups similar support cases using basic text analysis and built-in Python libraries
"""

import json
import re
import math
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, Counter
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CaseCluster:
    """Represents a cluster of similar cases"""
    cluster_id: int
    cases: List[Dict[str, Any]]
    common_patterns: List[str]
    severity_distribution: Dict[str, int]
    service_distribution: Dict[str, int]
    resolution_patterns: List[str]
    cluster_confidence: float

class SimpleCaseClusteringSystem:
    """Basic case clustering and similarity analysis using only built-in libraries"""
    
    def __init__(self):
        self.clusters = []
        self.service_keywords = self._build_service_keywords()
        self.resolution_keywords = self._build_resolution_keywords()
        self.stop_words = self._build_stop_words()
        
    def _build_service_keywords(self) -> Dict[str, List[str]]:
        """Build comprehensive service keywords for categorization"""
        return {
            'topology': ['topology', 'nasm-topology', 'topology-service', 'merge', 'composite'],
            'ui': ['ui-content', 'dashboard', 'interface', 'browser', 'hdm-common-ui'],
            'observer': ['observer', 'file-observer', 'rest-observer', 'data-ingestion'],
            'analytics': ['analytics', 'aggregation', 'dedup', 'spark', 'hdm-analytics'],
            'infrastructure': ['kubernetes', 'k8s', 'openshift', 'pod', 'deployment'],
            'database': ['cassandra', 'postgresql', 'database', 'db', 'query'],
            'messaging': ['kafka', 'message', 'topic', 'queue', 'event'],
            'security': ['authentication', 'authorization', 'rbac', 'permission', 'ssl'],
            'performance': ['performance', 'slow', 'timeout', 'memory', 'cpu', 'latency'],
            'configuration': ['config', 'configuration', 'setup', 'deployment', 'helm']
        }
    
    def _build_resolution_keywords(self) -> Dict[str, List[str]]:
        """Build resolution pattern keywords"""
        return {
            'hotfix': ['hotfix', 'patch', 'image', 'digest', 'csv', 'oc patch'],
            'restart': ['restart', 'reboot', 'pod restart', 'service restart'],
            'configuration': ['config change', 'reconfigure', 'update config'],
            'upgrade': ['upgrade', 'version update', 'migration', 'rollback'],
            'scaling': ['scale', 'scaling', 'resources', 'replicas'],
            'networking': ['network', 'dns', 'firewall', 'port', 'connectivity'],
            'permissions': ['permission', 'rbac', 'role', 'access', 'auth'],
            'documentation': ['documentation', 'guide', 'howto', 'example']
        }
    
    def _build_stop_words(self) -> Set[str]:
        """Build basic stop words list"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'is', 'was', 'are', 'been', 'be', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def analyze_cases(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive analysis of case collection"""
        
        if not cases:
            return {'error': 'No cases provided for analysis'}
        
        print(f"🔍 Analyzing {len(cases)} cases...")
        
        # Perform clustering using simple similarity
        clusters = self._perform_simple_clustering(cases)
        
        # Analyze patterns
        patterns = self._analyze_patterns(cases)
        
        # Find similar cases
        similarity_analysis = self._analyze_similarities(cases)
        
        # Generate insights
        insights = self._generate_insights(cases, clusters, patterns)
        
        return {
            'total_cases': len(cases),
            'clusters': clusters,
            'patterns': patterns,
            'similarity_analysis': similarity_analysis,
            'insights': insights,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using word overlap"""
        
        words1 = set(self._tokenize_text(text1.lower()))
        words2 = set(self._tokenize_text(text2.lower()))
        
        # Remove stop words
        words1 = words1 - self.stop_words
        words2 = words2 - self.stop_words
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Simple text tokenization"""
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter short words but keep technical terms
        filtered_words = [w for w in words if len(w) > 2 or w in ['ui', 'db', 'os', 'vm', 'ip']]
        
        return filtered_words
    
    def _perform_simple_clustering(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform simple clustering based on text similarity"""
        
        print("🔗 Performing similarity-based clustering...")
        
        # Calculate pairwise similarities
        similarities = []
        case_texts = self._prepare_case_texts(cases)
        
        for i in range(len(cases)):
            row = []
            for j in range(len(cases)):
                if i == j:
                    row.append(1.0)
                else:
                    similarity = self._calculate_text_similarity(case_texts[i], case_texts[j])
                    row.append(similarity)
            similarities.append(row)
        
        # Simple clustering: group cases with similarity > threshold
        threshold = 0.3
        visited = set()
        clusters = []
        
        for i, case in enumerate(cases):
            if i in visited:
                continue
            
            # Start new cluster
            cluster_cases = [case]
            cluster_indices = [i]
            visited.add(i)
            
            # Find similar cases
            for j in range(i + 1, len(cases)):
                if j not in visited and similarities[i][j] > threshold:
                    cluster_cases.append(cases[j])
                    cluster_indices.append(j)
                    visited.add(j)
            
            # Create cluster info
            cluster_info = {
                'cluster_id': len(clusters),
                'size': len(cluster_cases),
                'cases': cluster_cases[:5],  # Sample cases
                'case_ids': [case.get('case_number', f'case_{idx}') for idx, case in enumerate(cluster_cases)],
                'common_services': self._find_common_services(cluster_cases),
                'common_patterns': self._find_common_patterns(cluster_cases),
                'severity_distribution': self._analyze_severity_distribution(cluster_cases),
                'resolution_patterns': self._find_common_resolutions(cluster_cases),
                'avg_confidence': sum(case.get('confidence', 0) for case in cluster_cases) / len(cluster_cases),
                'representative_case': self._find_representative_case_simple(cluster_cases)
            }
            
            clusters.append(cluster_info)
        
        # Sort clusters by size
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        return {
            'method': 'simple_similarity',
            'n_clusters': len(clusters),
            'threshold': threshold,
            'clusters': clusters
        }
    
    def _prepare_case_texts(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Prepare case texts for analysis"""
        texts = []
        
        for case in cases:
            # Combine relevant text fields
            text_parts = []
            
            # Add main content
            for field in ['title', 'subject', 'description', 'problem_description', 
                         'resolution_description', 'full_text_for_rag']:
                if case.get(field):
                    text_parts.append(str(case[field]))
            
            # Add services and tags
            if case.get('services'):
                text_parts.extend(case['services'])
            
            if case.get('tags'):
                text_parts.extend(case['tags'])
            
            # Add symptoms and error patterns
            if case.get('symptoms'):
                text_parts.extend(case['symptoms'])
            
            if case.get('error_patterns'):
                text_parts.extend(case['error_patterns'])
            
            # Join and clean
            combined_text = ' '.join(text_parts)
            texts.append(combined_text)
        
        return texts
    
    def _find_common_services(self, cases: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
        """Find most common services in a cluster"""
        service_counter = Counter()
        
        for case in cases:
            services = case.get('services', []) or case.get('affected_services', [])
            service_counter.update(services)
        
        return service_counter.most_common(10)
    
    def _find_common_patterns(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Find common patterns in cluster cases"""
        
        # Combine all text content
        all_text = []
        for case in cases:
            text_parts = []
            for field in ['description', 'problem_description', 'title', 'subject']:
                if case.get(field):
                    text_parts.append(str(case[field]))
            all_text.append(' '.join(text_parts).lower())
        
        combined_text = ' '.join(all_text)
        
        # Find common technical patterns
        patterns = []
        
        # Version patterns
        version_patterns = re.findall(r'\d+\.\d+\.\d+', combined_text)
        if version_patterns:
            patterns.extend(list(set(version_patterns))[:5])
        
        # Error patterns
        error_patterns = re.findall(r'error[:\s]+([^.!?\n]+)', combined_text)
        if error_patterns:
            patterns.extend(list(set(error_patterns))[:3])
        
        # Command patterns
        command_patterns = re.findall(r'(oc\s+\w+|kubectl\s+\w+)', combined_text)
        if command_patterns:
            patterns.extend(list(set(command_patterns))[:3])
        
        return patterns[:10]
    
    def _analyze_severity_distribution(self, cases: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze severity distribution in cluster"""
        severity_counter = Counter()
        
        for case in cases:
            severity = case.get('severity', 'Unknown')
            severity_counter[severity] += 1
        
        return dict(severity_counter)
    
    def _find_common_resolutions(self, cases: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
        """Find common resolution patterns in cluster"""
        resolution_counter = Counter()
        
        for case in cases:
            patterns = case.get('resolution_patterns', [])
            resolution_counter.update(patterns)
        
        return resolution_counter.most_common(5)
    
    def _find_representative_case_simple(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the most representative case in a cluster"""
        
        if not cases:
            return {}
        
        # Use case with highest confidence as representative
        best_case = max(cases, key=lambda c: c.get('confidence', 0))
        
        return {
            'case_number': best_case.get('case_number', 'Unknown'),
            'title': best_case.get('title', best_case.get('subject', ''))[:100],
            'services': best_case.get('services', [])[:5],
            'confidence': best_case.get('confidence', 0)
        }
    
    def _analyze_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall patterns across all cases"""
        
        patterns = {
            'service_patterns': self._analyze_service_patterns(cases),
            'resolution_effectiveness': self._analyze_resolution_effectiveness(cases),
            'complexity_patterns': self._analyze_complexity_patterns(cases),
            'keyword_analysis': self._analyze_keywords(cases)
        }
        
        return patterns
    
    def _analyze_service_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze service-related patterns"""
        
        service_combinations = defaultdict(int)
        service_issue_types = defaultdict(lambda: defaultdict(int))
        
        for case in cases:
            services = case.get('services', []) or case.get('affected_services', [])
            category = case.get('case_category', case.get('category', 'unknown'))
            
            # Track service combinations
            if len(services) > 1:
                combo = tuple(sorted(services))
                service_combinations[combo] += 1
            
            # Track service-issue type relationships
            for service in services:
                service_issue_types[service][category] += 1
        
        return {
            'common_service_combinations': dict(Counter(service_combinations).most_common(10)),
            'service_issue_correlations': dict(service_issue_types)
        }
    
    def _analyze_resolution_effectiveness(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resolution pattern effectiveness"""
        
        resolution_success = defaultdict(list)
        
        for case in cases:
            patterns = case.get('resolution_patterns', [])
            confidence = case.get('confidence', 0)
            
            for pattern in patterns:
                resolution_success[pattern].append(confidence)
        
        # Calculate average confidence for each resolution pattern
        effectiveness = {}
        for pattern, confidences in resolution_success.items():
            if confidences:
                effectiveness[pattern] = {
                    'avg_confidence': sum(confidences) / len(confidences),
                    'usage_count': len(confidences)
                }
        
        return effectiveness
    
    def _analyze_complexity_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze case complexity patterns"""
        
        complexity_indicators = {
            'multi_service_cases': 0,
            'high_symptom_cases': 0,
            'low_confidence_cases': 0,
            'complex_resolutions': 0
        }
        
        for case in cases:
            services = case.get('services', []) or case.get('affected_services', [])
            symptoms = case.get('symptoms', [])
            confidence = case.get('confidence', 1.0)
            resolution_patterns = case.get('resolution_patterns', [])
            
            if len(services) > 2:
                complexity_indicators['multi_service_cases'] += 1
            
            if len(symptoms) > 3:
                complexity_indicators['high_symptom_cases'] += 1
            
            if confidence < 0.5:
                complexity_indicators['low_confidence_cases'] += 1
            
            if len(resolution_patterns) > 3:
                complexity_indicators['complex_resolutions'] += 1
        
        return complexity_indicators
    
    def _analyze_keywords(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze keyword frequency across all cases"""
        
        all_words = []
        technical_terms = Counter()
        
        for case in cases:
            # Combine all text
            text_parts = []
            for field in ['title', 'description', 'problem_description', 'resolution_description']:
                if case.get(field):
                    text_parts.append(str(case[field]))
            
            combined_text = ' '.join(text_parts).lower()
            words = self._tokenize_text(combined_text)
            
            # Filter technical terms (longer than 3 chars, not common words)
            for word in words:
                if len(word) > 3 and word not in self.stop_words:
                    technical_terms[word] += 1
            
            all_words.extend(words)
        
        return {
            'total_words': len(all_words),
            'unique_words': len(set(all_words)),
            'top_technical_terms': technical_terms.most_common(20)
        }
    
    def _analyze_similarities(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze case similarities using simple metrics"""
        
        case_texts = self._prepare_case_texts(cases)
        similar_pairs = []
        
        # Find similar case pairs
        for i in range(len(cases)):
            for j in range(i + 1, len(cases)):
                similarity = self._calculate_text_similarity(case_texts[i], case_texts[j])
                
                if similarity > 0.5:  # High similarity threshold
                    similar_pairs.append({
                        'case1': cases[i].get('case_number', f'case_{i}'),
                        'case2': cases[j].get('case_number', f'case_{j}'),
                        'similarity': similarity,
                        'common_services': list(set(
                            (cases[i].get('services', []) or []) + 
                            (cases[j].get('services', []) or [])
                        ))
                    })
        
        # Sort by similarity
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Calculate average similarity
        all_similarities = []
        for i in range(len(cases)):
            for j in range(i + 1, len(cases)):
                similarity = self._calculate_text_similarity(case_texts[i], case_texts[j])
                all_similarities.append(similarity)
        
        avg_similarity = sum(all_similarities) / len(all_similarities) if all_similarities else 0
        
        return {
            'high_similarity_pairs': similar_pairs[:20],
            'average_similarity': avg_similarity,
            'similarity_distribution': {
                'very_high': len([s for s in all_similarities if s > 0.8]),
                'high': len([s for s in all_similarities if 0.6 < s <= 0.8]),
                'medium': len([s for s in all_similarities if 0.4 < s <= 0.6]),
                'low': len([s for s in all_similarities if s <= 0.4])
            }
        }
    
    def _generate_insights(self, cases: List[Dict[str, Any]], 
                          clusters: Dict[str, Any], 
                          patterns: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from analysis"""
        
        insights = []
        
        # Clustering insights
        if 'clusters' in clusters:
            cluster_list = clusters['clusters']
            if cluster_list:
                largest_cluster = max(cluster_list, key=lambda x: x['size'])
                insights.append(
                    f"Largest issue cluster contains {largest_cluster['size']} cases "
                    f"primarily related to {largest_cluster['common_services'][0][0] if largest_cluster['common_services'] else 'unknown service'}"
                )
                
                # Check for many small clusters (potential noise)
                small_clusters = [c for c in cluster_list if c['size'] == 1]
                if len(small_clusters) > len(cluster_list) * 0.5:
                    insights.append(f"High number of singleton clusters ({len(small_clusters)}) suggests diverse case patterns")
        
        # Service insights
        if 'service_patterns' in patterns:
            service_combos = patterns['service_patterns']['common_service_combinations']
            if service_combos:
                top_combo = list(service_combos.keys())[0]
                insights.append(f"Most common service combination issue: {' + '.join(top_combo)}")
        
        # Resolution insights
        if 'resolution_effectiveness' in patterns:
            effectiveness = patterns['resolution_effectiveness']
            if effectiveness:
                best_resolution = max(effectiveness.keys(), 
                                    key=lambda k: effectiveness[k]['avg_confidence'])
                insights.append(f"Most effective resolution pattern: {best_resolution}")
        
        # Complexity insights
        if 'complexity_patterns' in patterns:
            complexity = patterns['complexity_patterns']
            total_cases = len(cases)
            
            if complexity['low_confidence_cases'] > total_cases * 0.3:
                insights.append(
                    f"High number of low-confidence cases ({complexity['low_confidence_cases']}) "
                    "suggests need for better case documentation"
                )
        
        # Keyword insights
        if 'keyword_analysis' in patterns:
            keywords = patterns['keyword_analysis']
            if keywords.get('top_technical_terms'):
                top_term = keywords['top_technical_terms'][0][0]
                insights.append(f"Most frequent technical term: '{top_term}' - consider creating focused knowledge articles")
        
        return insights
    
    def find_similar_cases(self, target_case: Dict[str, Any], 
                          all_cases: List[Dict[str, Any]], 
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """Find cases similar to a target case"""
        
        target_text = self._prepare_case_texts([target_case])[0]
        case_texts = self._prepare_case_texts(all_cases)
        
        similarities = []
        for i, case_text in enumerate(case_texts):
            similarity = self._calculate_text_similarity(target_text, case_text)
            similarities.append((i, similarity))
        
        # Sort by similarity and get top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        similar_cases = []
        for i, (case_idx, similarity) in enumerate(similarities[:top_k]):
            if case_idx < len(all_cases):
                similar_case = all_cases[case_idx].copy()
                similar_case['similarity_score'] = similarity
                similar_cases.append(similar_case)
        
        return similar_cases
    
    def save_analysis(self, analysis_results: Dict[str, Any], filename: str):
        """Save analysis results"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"💾 Analysis saved to: {filename}")

def main():
    """Main function for case clustering analysis"""
    
    print("🔗 IBM Support Case Clustering & Similarity Analysis (Simple Version)")
    print("="*70)
    
    # Load processed cases
    knowledge_base_file = "enterprise_knowledge_base.json"
    
    try:
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        if not cases:
            print("❌ No cases found in knowledge base")
            return
        
        print(f"📁 Loaded {len(cases)} cases from {knowledge_base_file}")
        
        # Initialize clustering system
        clustering_system = SimpleCaseClusteringSystem()
        
        # Perform analysis
        analysis_results = clustering_system.analyze_cases(cases)
        
        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"  • Total cases analyzed: {analysis_results['total_cases']}")
        
        if 'clusters' in analysis_results:
            clusters = analysis_results['clusters']
            print(f"  • Clustering method: {clusters['method']}")
            print(f"  • Number of clusters: {clusters['n_clusters']}")
            print(f"  • Similarity threshold: {clusters['threshold']}")
        
        # Display top clusters
        if 'clusters' in analysis_results and analysis_results['clusters'].get('clusters'):
            print(f"\n🔍 Top Clusters:")
            for i, cluster in enumerate(analysis_results['clusters']['clusters'][:5]):
                print(f"  Cluster {i+1}: {cluster['size']} cases")
                if cluster['common_services']:
                    services = [s[0] for s in cluster['common_services'][:3]]
                    print(f"    Common services: {', '.join(services)}")
        
        # Display insights
        if 'insights' in analysis_results:
            print(f"\n💡 Key Insights:")
            for insight in analysis_results['insights']:
                print(f"  • {insight}")
        
        # Save results
        output_file = "simple_case_clustering_analysis.json"
        clustering_system.save_analysis(analysis_results, output_file)
        
        print(f"\n✅ Clustering analysis complete!")
        
    except FileNotFoundError:
        print(f"❌ Knowledge base file not found: {knowledge_base_file}")
        print("💡 Run enterprise_case_processor.py first to generate the knowledge base")
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()