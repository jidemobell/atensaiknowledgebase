#!/usr/bin/env python3
"""
Case Clustering and Similarity Analysis System
Groups similar support cases and identifies patterns across thousands of cases
"""

import json
import re
import numpy as np
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, Counter
from datetime import datetime
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import pickle

@dataclass
class CaseCluster:
    """Represents a cluster of similar cases"""
    cluster_id: int
    cases: List[Dict[str, Any]]
    centroid_features: Dict[str, float]
    common_patterns: List[str]
    severity_distribution: Dict[str, int]
    service_distribution: Dict[str, int]
    resolution_patterns: List[str]
    cluster_confidence: float

class CaseClusteringSystem:
    """Advanced case clustering and similarity analysis"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        
        self.clusters = []
        self.case_vectors = None
        self.similarity_matrix = None
        self.service_keywords = self._build_service_keywords()
        self.resolution_keywords = self._build_resolution_keywords()
        
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
    
    def analyze_cases(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive analysis of case collection"""
        
        if not cases:
            return {'error': 'No cases provided for analysis'}
        
        print(f"🔍 Analyzing {len(cases)} cases...")
        
        # Prepare text data for vectorization
        case_texts = self._prepare_case_texts(cases)
        
        # Create TF-IDF vectors
        self.case_vectors = self.vectorizer.fit_transform(case_texts)
        print(f"📊 Created {self.case_vectors.shape[1]} feature vectors")
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.case_vectors)
        
        # Perform clustering
        clusters = self._perform_clustering(cases)
        
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
    
    def _prepare_case_texts(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Prepare case texts for vectorization"""
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
            cleaned_text = self._clean_text(combined_text)
            texts.append(cleaned_text)
        
        return texts
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep important technical terms
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove very short words but keep technical abbreviations
        words = text.split()
        filtered_words = [w for w in words if len(w) > 2 or w in ['ui', 'db', 'os', 'vm', 'ip']]
        
        return ' '.join(filtered_words)
    
    def _perform_clustering(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform multiple clustering approaches"""
        
        clustering_results = {}
        
        # K-Means clustering with different k values
        for k in [5, 10, 15, 20]:
            if k < len(cases):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(self.case_vectors)
                
                clusters = self._organize_clusters(cases, cluster_labels, k)
                clustering_results[f'kmeans_{k}'] = {
                    'method': 'kmeans',
                    'n_clusters': k,
                    'clusters': clusters,
                    'silhouette_analysis': self._calculate_cluster_quality(cluster_labels)
                }
        
        # DBSCAN clustering for automatic cluster detection
        dbscan = DBSCAN(eps=0.3, min_samples=3, metric='cosine')
        dbscan_labels = dbscan.fit_predict(self.case_vectors.toarray())
        
        n_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
        if n_clusters > 0:
            dbscan_clusters = self._organize_clusters(cases, dbscan_labels, n_clusters)
            clustering_results['dbscan'] = {
                'method': 'dbscan',
                'n_clusters': n_clusters,
                'n_noise': list(dbscan_labels).count(-1),
                'clusters': dbscan_clusters
            }
        
        return clustering_results
    
    def _organize_clusters(self, cases: List[Dict[str, Any]], 
                          labels: np.ndarray, n_clusters: int) -> List[Dict[str, Any]]:
        """Organize cases into cluster objects"""
        
        clusters = []
        
        for cluster_id in range(n_clusters):
            cluster_cases = [cases[i] for i, label in enumerate(labels) if label == cluster_id]
            
            if not cluster_cases:
                continue
            
            # Analyze cluster characteristics
            cluster_info = {
                'cluster_id': cluster_id,
                'size': len(cluster_cases),
                'cases': cluster_cases[:10],  # Sample cases
                'case_ids': [case.get('case_number', f'case_{i}') for i, case in enumerate(cluster_cases)],
                'common_services': self._find_common_services(cluster_cases),
                'common_patterns': self._find_common_patterns(cluster_cases),
                'severity_distribution': self._analyze_severity_distribution(cluster_cases),
                'resolution_patterns': self._find_common_resolutions(cluster_cases),
                'avg_confidence': sum(case.get('confidence', 0) for case in cluster_cases) / len(cluster_cases),
                'representative_case': self._find_representative_case(cluster_cases, cluster_id, labels)
            }
            
            clusters.append(cluster_info)
        
        # Sort clusters by size
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        return clusters
    
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
    
    def _find_representative_case(self, cases: List[Dict[str, Any]], 
                                cluster_id: int, all_labels: np.ndarray) -> Dict[str, Any]:
        """Find the most representative case in a cluster"""
        
        # Get indices of cases in this cluster
        cluster_indices = [i for i, label in enumerate(all_labels) if label == cluster_id]
        
        if not cluster_indices:
            return cases[0] if cases else {}
        
        # Calculate centroid similarity for each case in cluster
        cluster_vectors = self.case_vectors[cluster_indices]
        centroid = cluster_vectors.mean(axis=0)
        
        similarities = cosine_similarity(cluster_vectors, centroid.reshape(1, -1)).flatten()
        
        # Find most similar case to centroid
        best_idx = cluster_indices[similarities.argmax()]
        
        # Return basic info about representative case
        rep_case = cases[best_idx] if best_idx < len(cases) else cases[0]
        
        return {
            'case_number': rep_case.get('case_number', 'Unknown'),
            'title': rep_case.get('title', rep_case.get('subject', ''))[:100],
            'services': rep_case.get('services', [])[:5],
            'confidence': rep_case.get('confidence', 0),
            'similarity_to_centroid': float(similarities.max())
        }
    
    def _calculate_cluster_quality(self, labels: np.ndarray) -> Dict[str, float]:
        """Calculate cluster quality metrics"""
        
        try:
            from sklearn.metrics import silhouette_score
            
            if len(set(labels)) > 1:
                silhouette_avg = silhouette_score(self.case_vectors, labels)
                return {'silhouette_score': float(silhouette_avg)}
            else:
                return {'silhouette_score': 0.0}
        except ImportError:
            return {'silhouette_score': 'sklearn_not_available'}
    
    def _analyze_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall patterns across all cases"""
        
        patterns = {
            'service_patterns': self._analyze_service_patterns(cases),
            'temporal_patterns': self._analyze_temporal_patterns(cases),
            'resolution_effectiveness': self._analyze_resolution_effectiveness(cases),
            'complexity_patterns': self._analyze_complexity_patterns(cases)
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
    
    def _analyze_temporal_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in cases"""
        
        # This would require timestamp data - placeholder for now
        return {
            'note': 'Temporal analysis requires timestamp data',
            'cases_with_timestamps': len([c for c in cases if c.get('parsed_at') or c.get('timestamp')])
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
    
    def _analyze_similarities(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze case similarities"""
        
        if self.similarity_matrix is None:
            return {'error': 'Similarity matrix not calculated'}
        
        # Find most similar case pairs
        similar_pairs = []
        n_cases = len(cases)
        
        for i in range(n_cases):
            for j in range(i + 1, n_cases):
                similarity = self.similarity_matrix[i][j]
                if similarity > 0.7:  # High similarity threshold
                    similar_pairs.append({
                        'case1': cases[i].get('case_number', f'case_{i}'),
                        'case2': cases[j].get('case_number', f'case_{j}'),
                        'similarity': float(similarity),
                        'common_services': list(set(
                            (cases[i].get('services', []) or []) + 
                            (cases[j].get('services', []) or [])
                        ))
                    })
        
        # Sort by similarity
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'high_similarity_pairs': similar_pairs[:20],
            'average_similarity': float(np.mean(self.similarity_matrix)),
            'similarity_distribution': {
                'very_high': len([s for s in self.similarity_matrix.flatten() if s > 0.8]),
                'high': len([s for s in self.similarity_matrix.flatten() if 0.6 < s <= 0.8]),
                'medium': len([s for s in self.similarity_matrix.flatten() if 0.4 < s <= 0.6]),
                'low': len([s for s in self.similarity_matrix.flatten() if s <= 0.4])
            }
        }
    
    def _generate_insights(self, cases: List[Dict[str, Any]], 
                          clusters: Dict[str, Any], 
                          patterns: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from analysis"""
        
        insights = []
        
        # Clustering insights
        if 'kmeans_10' in clusters:
            kmeans_clusters = clusters['kmeans_10']['clusters']
            largest_cluster = max(kmeans_clusters, key=lambda x: x['size'])
            insights.append(
                f"Largest issue cluster contains {largest_cluster['size']} cases "
                f"primarily related to {largest_cluster['common_services'][0][0] if largest_cluster['common_services'] else 'unknown service'}"
            )
        
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
        
        return insights
    
    def find_similar_cases(self, target_case: Dict[str, Any], 
                          all_cases: List[Dict[str, Any]], 
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """Find cases similar to a target case"""
        
        if not self.case_vectors or not self.vectorizer:
            return []
        
        # Prepare target case text
        target_text = self._prepare_case_texts([target_case])[0]
        
        # Transform target case
        target_vector = self.vectorizer.transform([target_text])
        
        # Calculate similarities
        similarities = cosine_similarity(target_vector, self.case_vectors).flatten()
        
        # Get top similar cases
        similar_indices = similarities.argsort()[-top_k-1:-1][::-1]  # Exclude self
        
        similar_cases = []
        for idx in similar_indices:
            if idx < len(all_cases):
                similar_case = all_cases[idx].copy()
                similar_case['similarity_score'] = float(similarities[idx])
                similar_cases.append(similar_case)
        
        return similar_cases
    
    def save_analysis(self, analysis_results: Dict[str, Any], filename: str):
        """Save analysis results and model"""
        
        # Save analysis results
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        # Save vectorizer for future use
        vectorizer_file = filename.replace('.json', '_vectorizer.pkl')
        with open(vectorizer_file, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"💾 Analysis saved to: {filename}")
        print(f"💾 Vectorizer saved to: {vectorizer_file}")

def main():
    """Main function for case clustering analysis"""
    
    print("🔗 IBM Support Case Clustering & Similarity Analysis")
    print("="*55)
    
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
        clustering_system = CaseClusteringSystem()
        
        # Perform analysis
        analysis_results = clustering_system.analyze_cases(cases)
        
        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"  • Total cases analyzed: {analysis_results['total_cases']}")
        
        if 'clusters' in analysis_results:
            clusters = analysis_results['clusters']
            for method, cluster_data in clusters.items():
                print(f"  • {method}: {cluster_data['n_clusters']} clusters found")
        
        # Display insights
        if 'insights' in analysis_results:
            print(f"\n💡 Key Insights:")
            for insight in analysis_results['insights']:
                print(f"  • {insight}")
        
        # Save results
        output_file = "case_clustering_analysis.json"
        clustering_system.save_analysis(analysis_results, output_file)
        
        print(f"\n✅ Clustering analysis complete!")
        
    except FileNotFoundError:
        print(f"❌ Knowledge base file not found: {knowledge_base_file}")
        print("💡 Run enterprise_case_processor.py first to generate the knowledge base")
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()