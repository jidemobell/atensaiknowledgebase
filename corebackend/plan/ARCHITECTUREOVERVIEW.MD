+------------------+     +-------------------+
|   React UI       | <-> |   FastAPI Backend |
| (localhost:3000) |     |   (localhost:8000)|
+------------------+     +-------------------+
                                |
                                v
                  +---------------------------+
                  |   Weaviate (Vector + Graph)|
                  |   or Pinecone + Neo4j      |
                  +---------------------------+
                                |
                                v
                   [cases/*.md, docs/, logs/]