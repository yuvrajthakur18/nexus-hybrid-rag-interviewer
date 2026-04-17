import asyncio
from time import perf_counter

from app.services.query_router import QueryRouter


async def _simulate() -> float:
    started = perf_counter()
    _ = QueryRouter().route("Need interview strategy under production constraints and art style")
    await asyncio.sleep(0.01)
    return (perf_counter() - started) * 1000


def test_latency_budget_baseline() -> None:
    elapsed = asyncio.run(_simulate())
    assert elapsed < 5000
