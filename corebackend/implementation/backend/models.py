from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class KnowledgeSourceType(str, Enum):
    SALESFORCE_CASE = "salesforce_case"
    GITHUB_CODE = "github_code"
    DOCUMENTATION = "documentation"
    WIKI = "wiki"
    SEARCH_HISTORY = "search_history"
    DIAGNOSTIC_SESSION = "diagnostic_session"
    USER_FEEDBACK = "user_feedback"

class CaseEntry(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.SALESFORCE_CASE
    raw_content: Optional[str] = None  # Original pasted content
    affected_services: List[str] = []
    symptoms: List[str] = []
    severity: str = "Medium"
    resolution_status: str = "Open"
    resolution_steps: List[str] = []
    tags: List[str] = []
    created_date: datetime = datetime.now()
    updated_date: datetime = datetime.now()
    confidence: float = 0.0
    manual_entry: bool = True
    extracted_metadata: Dict[str, Any] = {}

class CodeKnowledge(BaseModel):
    id: Optional[str] = None
    repository: str
    file_path: str
    function_name: Optional[str] = None
    error_pattern: str
    code_snippet: str
    related_services: List[str] = []
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None
    deployment_correlation: bool = False
    tags: List[str] = []
    created_date: datetime = datetime.now()

class DocumentationEntry(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    source_url: Optional[str] = None
    doc_type: str  # runbook, wiki, api_doc, troubleshooting
    related_services: List[str] = []
    tags: List[str] = []
    last_updated: datetime = datetime.now()
    effectiveness_score: float = 0.0

class DiagnosticSession(BaseModel):
    id: Optional[str] = None
    initial_query: str
    user_id: Optional[str] = None
    search_history: List[Dict[str, Any]] = []
    knowledge_sources_accessed: List[str] = []
    cases_viewed: List[str] = []
    resolution_attempted: bool = False
    resolution_successful: Optional[bool] = None
    resolution_steps: List[str] = []
    time_to_resolve: Optional[int] = None  # minutes
    user_feedback: Optional[Dict[str, Any]] = None
    created_date: datetime = datetime.now()
    completed_date: Optional[datetime] = None

class SearchInteraction(BaseModel):
    session_id: str
    query: str
    results_count: int
    clicked_results: List[str] = []
    effectiveness_rating: Optional[int] = None  # 1-5 scale
    timestamp: datetime = datetime.now()

class UnifiedSearchRequest(BaseModel):
    query: str
    search_mode: str = "all"  # all, cases, code, docs, history
    filters: Dict[str, Any] = {}
    session_id: Optional[str] = None

class UnifiedSearchResponse(BaseModel):
    query: str
    total_results: int
    case_results: List[Dict[str, Any]] = []
    code_results: List[Dict[str, Any]] = []
    doc_results: List[Dict[str, Any]] = []
    historical_searches: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    diagnostic_confidence: float = 0.0

class KnowledgeExtractionRequest(BaseModel):
    raw_content: str
    content_type: str = "salesforce_case"  # salesforce_case, email, log, documentation

class ExtractedKnowledge(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    affected_services: List[str] = []
    symptoms: List[str] = []
    error_messages: List[str] = []
    severity: Optional[str] = None
    tags: List[str] = []
    confidence: float = 0.0
    suggested_case_type: str = "incident"

class FeedbackRequest(BaseModel):
    session_id: str
    item_id: str
    item_type: str  # case, code, doc, suggestion
    feedback_type: str  # helpful, not_helpful, incorrect, needs_update
    rating: Optional[int] = None  # 1-5 scale
    comments: Optional[str] = None

class LearningInsights(BaseModel):
    most_effective_sources: List[Dict[str, Any]]
    common_search_patterns: List[str]
    average_resolution_time: float
    success_rate_by_source: Dict[str, float]
    knowledge_gaps: List[str]
    trending_issues: List[str]
