import logging

import pytest
import respx
from httpx import Response

from services.task_dispatcher import AsyncTaskDispatcher
from utils.logger import error_logger


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_preload_age_predictions_success() -> None:
    """Test successful preload of age predictions from Agify API."""
    respx.get("https://api.agify.io").mock(
        return_value=Response(
            200, json=[{"name": "Alice", "age": 30, "count": 100, "country_id": "US"}]
        )
    )

    dispatcher = AsyncTaskDispatcher()
    await dispatcher.preload_age_predictions([("Alice", "US")])

    assert ("Alice", "US") in dispatcher.age_cache
    assert dispatcher.age_cache[("Alice", "US")]["age"] == 30


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_handle_age_cached() -> None:
    """Test that cached age result is used without calling Agify API."""
    dispatcher = AsyncTaskDispatcher()
    dispatcher.age_cache[("Bob", "GB")] = {"name": "Bob", "age": 42, "country_id": "GB"}

    respx.post("https://postman-echo.com/post").mock(
        return_value=Response(200, json={"json": dispatcher.age_cache[("Bob", "GB")]})
    )

    result = await dispatcher.handle({"type": "age", "name": "Bob", "country": "GB"})
    assert result["name"] == "Bob"
    assert result["age"] == 42


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_handle_age_not_cached() -> None:
    """Test age is fetched from Agify if not cached."""
    respx.get("https://api.agify.io").mock(
        return_value=Response(
            200, json={"name": "Charlie", "age": 35, "country_id": "CA"}
        )
    )
    respx.post("https://postman-echo.com/post").mock(
        return_value=Response(
            200, json={"json": {"name": "Charlie", "age": 35, "country_id": "CA"}}
        )
    )

    dispatcher = AsyncTaskDispatcher()
    result = await dispatcher.handle(
        {"type": "age", "name": "Charlie", "country": "CA"}
    )

    assert result["age"] == 35


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_handle_joke() -> None:
    """Test joke handling logic."""
    respx.get("https://official-joke-api.appspot.com/random_joke").mock(
        return_value=Response(200, json={"setup": "Why?", "punchline": "Because!"})
    )
    respx.post("https://postman-echo.com/post").mock(
        return_value=Response(
            200, json={"json": {"setup": "Why?", "punchline": "Because!"}}
        )
    )

    dispatcher = AsyncTaskDispatcher()
    result = await dispatcher.handle({"type": "joke"})

    assert "setup" in result
    assert "punchline" in result


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_handle_unknown_type() -> None:
    """Test handling of unknown message types."""
    input_data = {"type": "unknown", "message": "Hello"}

    respx.post("https://postman-echo.com/post").mock(
        return_value=Response(200, json={"json": input_data})
    )

    dispatcher = AsyncTaskDispatcher()
    result = await dispatcher.handle(input_data)

    assert result == input_data


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_handle_postman_error() -> None:
    """Test error handling if Postman Echo returns an error."""
    respx.get("https://api.agify.io").mock(
        return_value=Response(200, json={"name": "Dana", "age": 28, "country_id": "DE"})
    )
    respx.post("https://postman-echo.com/post").mock(
        return_value=Response(500, json={"error": "Internal Server Error"})
    )

    dispatcher = AsyncTaskDispatcher()

    with pytest.raises(Exception):
        await dispatcher.handle({"type": "age", "name": "Dana", "country": "DE"})


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_handle_age_uses_cache(monkeypatch) -> None:
    """Ensure Agify API is NOT called when result is cached."""
    dispatcher = AsyncTaskDispatcher()
    dispatcher.age_cache[("Emily", "US")] = {"name": "Emily", "age": 33}

    called = False

    async def fake_get_age(name: str, country: str) -> dict:
        nonlocal called
        called = True
        return {"name": name, "age": 99}

    monkeypatch.setattr(dispatcher.agify_client, "get_age", fake_get_age)

    respx.post("https://postman-echo.com/post").mock(
        return_value=Response(200, json={"json": {"name": "Emily", "age": 33}})
    )

    result = await dispatcher.handle({"type": "age", "name": "Emily", "country": "US"})

    assert result["age"] == 33
    assert not called


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_preload_age_predictions_batch_error(caplog) -> None:
    """Test that Agify batch API failure is logged."""
    respx.get("https://api.agify.io").mock(
        return_value=Response(500, json={"error": "Agify failure"})
    )

    dispatcher = AsyncTaskDispatcher()
    error_logger.addHandler(caplog.handler)
    error_logger.setLevel(logging.ERROR)

    await dispatcher.preload_age_predictions([("Tom", "DE")])

    assert any("Failed batch request" in r.message for r in caplog.records)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.dispatcher
@respx.mock
async def test_preload_age_predictions_caches_results() -> None:
    """Test batch preload populates the age_cache."""
    respx.get("https://api.agify.io").mock(
        return_value=Response(
            200,
            json=[
                {"name": "Anna", "age": 25, "count": 80, "country_id": "PL"},
                {"name": "Ola", "age": 23, "count": 60, "country_id": "PL"},
            ],
        )
    )

    dispatcher = AsyncTaskDispatcher()
    await dispatcher.preload_age_predictions([("Anna", "PL"), ("Ola", "PL")])

    assert ("Anna", "PL") in dispatcher.age_cache
    assert dispatcher.age_cache[("Ola", "PL")]["age"] == 23
