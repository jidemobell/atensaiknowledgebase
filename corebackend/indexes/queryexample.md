query = "topology-merge times out under load"
results = weaviate_client.query.get("Case", ["case_id", "title", "fix_summary"]).with_near_text({
    "concepts": [query]
}).with_where({
    "path": ["service"],
    "operator": "Equal",
    "valueText": "topology-merge"
}).do()