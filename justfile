set dotenv-load := true


tst:
    uv run pytest
pg:
    PGPASSWORD=$P2P_DB__PASSWORD pgcli -U p2p_hub_app -d p2p_knowledge_hub -h localhost
