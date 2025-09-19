
✅ Step 3: Index for Search + Graph
Tools:
Weaviate (recommended): Native graph + vector search, supports nearText + where filters
Or: Pinecone + Neo4j combo
Embedding Strategy:
Use IBM Granite-13B-Embed (enterprise-safe, on-prem friendly)
Chunk each case into:
Title + symptoms → for semantic search
Fix description → for retrieval
Store metadata: service, env, status, created_at