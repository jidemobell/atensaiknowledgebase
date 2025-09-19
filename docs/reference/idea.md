// Neo4j-style schema (we can use any graph DB)
(Case {id, title, description, status, created_at})
-[:HAS_SYMPTOM]->(Symptom {text, log_snippet, error_type})
-[:AFFECTS_SERVICE]->(Service {name})  // e.g., topology-merge
-[:HAS_ROOT_CAUSE]->(Cause {category, detail})
-[:RESOLVED_BY]->(Fix {type, command, doc_link, slack_thread})

// Other connections
(Fix)-[:USEFUL_IN]->(Environment {type}) // cloud / on-prem
(Case)-[:DISCUSSED_IN]->(SlackMessage {text, ts, channel})
(Document)-[:INFORMS]->(Fix)