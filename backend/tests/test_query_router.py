from app.services.query_router import QueryRouter


def test_query_router_hybrid() -> None:
    assert QueryRouter().route("Need visual style under memory constraint") == "hybrid"
