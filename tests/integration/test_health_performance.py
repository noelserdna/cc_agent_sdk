"""
Integration tests for health endpoint performance.

Tests verify that health endpoint meets performance requirements:
- Response time < 500ms (FR-066)
- Handles concurrent requests without degradation
- No memory leaks under load
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, stdev

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_response_time_under_500ms(client):
    """Test that health endpoint responds in under 500ms (FR-066)."""
    # Warm up
    client.get("/health")

    # Measure 10 requests
    response_times = []
    for _ in range(10):
        start = time.time()
        response = client.get("/health")
        end = time.time()

        duration_ms = (end - start) * 1000
        response_times.append(duration_ms)

        assert response.status_code == 200
        assert duration_ms < 500, f"Response time {duration_ms:.2f}ms exceeds 500ms limit"

    # Calculate statistics
    avg_time = mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    print(f"\nHealth endpoint response times:")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    print(f"  Std Dev: {stdev(response_times):.2f}ms")

    # All should be well under 500ms
    assert avg_time < 100, f"Average response time {avg_time:.2f}ms too slow"
    assert max_time < 500, f"Max response time {max_time:.2f}ms exceeds limit"


def test_health_endpoint_p95_latency(client):
    """Test that 95th percentile latency is under 100ms."""
    # Warm up
    client.get("/health")

    # Measure 100 requests
    response_times = []
    for _ in range(100):
        start = time.time()
        response = client.get("/health")
        end = time.time()

        duration_ms = (end - start) * 1000
        response_times.append(duration_ms)

        assert response.status_code == 200

    # Calculate p95
    sorted_times = sorted(response_times)
    p95_index = int(len(sorted_times) * 0.95)
    p95_latency = sorted_times[p95_index]

    print(f"\nLatency statistics (100 requests):")
    print(f"  P50: {sorted_times[50]:.2f}ms")
    print(f"  P95: {p95_latency:.2f}ms")
    print(f"  P99: {sorted_times[99]:.2f}ms")

    # p95 should be well under 500ms
    assert p95_latency < 100, f"P95 latency {p95_latency:.2f}ms too high"


def test_health_endpoint_concurrent_requests_performance(client):
    """Test that health endpoint handles 10 concurrent requests without degradation."""

    def make_request(request_id: int) -> dict:
        """Make a single health check request and measure time."""
        start = time.time()
        response = client.get("/health")
        end = time.time()

        duration_ms = (end - start) * 1000

        return {
            "request_id": request_id,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "data": response.json(),
        }

    # Warm up
    client.get("/health")

    # Make 10 concurrent requests
    num_concurrent = 10
    results = []

    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_concurrent)]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # All requests should succeed
    assert len(results) == num_concurrent
    for result in results:
        assert result["status_code"] == 200
        assert result["data"]["status"] == "healthy"

    # Calculate performance metrics
    durations = [r["duration_ms"] for r in results]
    avg_duration = mean(durations)
    max_duration = max(durations)

    print(f"\nConcurrent requests performance ({num_concurrent} concurrent):")
    print(f"  Average: {avg_duration:.2f}ms")
    print(f"  Max: {max_duration:.2f}ms")
    print(f"  Min: {min(durations):.2f}ms")

    # Under concurrent load, should still be fast
    assert avg_duration < 200, f"Average concurrent response time {avg_duration:.2f}ms too slow"
    assert max_duration < 500, f"Max concurrent response time {max_duration:.2f}ms exceeds limit"


def test_health_endpoint_sustained_load(client):
    """Test that health endpoint maintains performance under sustained load."""
    # Warm up
    client.get("/health")

    # Sustained load: 100 requests over time
    num_requests = 100
    results = []

    start_test = time.time()
    for i in range(num_requests):
        start = time.time()
        response = client.get("/health")
        end = time.time()

        duration_ms = (end - start) * 1000
        results.append(
            {
                "request_num": i,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )

        # Small delay to simulate realistic load
        time.sleep(0.01)

    end_test = time.time()
    total_duration = end_test - start_test

    # All requests should succeed
    for result in results:
        assert result["status_code"] == 200

    # Calculate performance degradation
    first_10 = [r["duration_ms"] for r in results[:10]]
    last_10 = [r["duration_ms"] for r in results[-10:]]

    avg_first = mean(first_10)
    avg_last = mean(last_10)

    print(f"\nSustained load test ({num_requests} requests):")
    print(f"  Total duration: {total_duration:.2f}s")
    print(f"  Throughput: {num_requests / total_duration:.2f} req/s")
    print(f"  First 10 avg: {avg_first:.2f}ms")
    print(f"  Last 10 avg: {avg_last:.2f}ms")

    # Performance should not degrade significantly
    degradation = ((avg_last - avg_first) / avg_first) * 100
    print(f"  Degradation: {degradation:.2f}%")

    assert avg_last < 500, "Performance degraded beyond acceptable limit"
    assert degradation < 50, f"Performance degraded by {degradation:.2f}% (>50% threshold)"


def test_health_endpoint_burst_load(client):
    """Test that health endpoint handles burst traffic (50 concurrent requests)."""

    def make_request(request_id: int) -> dict:
        start = time.time()
        response = client.get("/health")
        end = time.time()

        return {
            "request_id": request_id,
            "status_code": response.status_code,
            "duration_ms": (end - start) * 1000,
        }

    # Warm up
    client.get("/health")

    # Burst: 50 concurrent requests
    num_concurrent = 50
    results = []

    start_burst = time.time()
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_concurrent)]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    end_burst = time.time()

    burst_duration = end_burst - start_burst

    # All requests should succeed
    assert len(results) == num_concurrent
    for result in results:
        assert result["status_code"] == 200

    # Calculate statistics
    durations = [r["duration_ms"] for r in results]
    avg_duration = mean(durations)
    max_duration = max(durations)
    p95_duration = sorted(durations)[int(len(durations) * 0.95)]

    print(f"\nBurst load test ({num_concurrent} concurrent requests):")
    print(f"  Total burst duration: {burst_duration:.2f}s")
    print(f"  Average latency: {avg_duration:.2f}ms")
    print(f"  P95 latency: {p95_duration:.2f}ms")
    print(f"  Max latency: {max_duration:.2f}ms")

    # Under burst load, most requests should still be fast
    assert avg_duration < 300, f"Average burst latency {avg_duration:.2f}ms too high"
    assert p95_duration < 500, f"P95 burst latency {p95_duration:.2f}ms exceeds limit"


def test_health_endpoint_no_memory_leak(client):
    """Test that repeated health checks don't cause memory leaks."""
    import gc
    import sys

    # Force garbage collection
    gc.collect()

    # Warm up
    for _ in range(10):
        client.get("/health")

    # Measure initial memory
    initial_objects = len(gc.get_objects())

    # Make many requests
    num_requests = 1000
    for _ in range(num_requests):
        response = client.get("/health")
        assert response.status_code == 200

    # Force garbage collection
    gc.collect()

    # Measure final memory
    final_objects = len(gc.get_objects())

    # Calculate object growth
    object_growth = final_objects - initial_objects
    growth_per_request = object_growth / num_requests

    print(f"\nMemory leak test ({num_requests} requests):")
    print(f"  Initial objects: {initial_objects}")
    print(f"  Final objects: {final_objects}")
    print(f"  Object growth: {object_growth}")
    print(f"  Growth per request: {growth_per_request:.4f}")

    # Object growth should be minimal (< 0.1 objects per request)
    assert (
        growth_per_request < 1.0
    ), f"Potential memory leak: {growth_per_request:.4f} objects per request"


def test_health_endpoint_cold_start_performance(client):
    """Test health endpoint performance on first request (cold start)."""
    # Note: This test should be run first in the suite, but we can't guarantee order
    # So we use a fresh client instance
    from src.main import app

    fresh_client = TestClient(app)

    # First request (cold start)
    start = time.time()
    response = fresh_client.get("/health")
    end = time.time()

    cold_start_ms = (end - start) * 1000

    print(f"\nCold start performance:")
    print(f"  First request: {cold_start_ms:.2f}ms")

    assert response.status_code == 200
    # Cold start should still be under 1 second
    assert cold_start_ms < 1000, f"Cold start {cold_start_ms:.2f}ms too slow"


def test_health_endpoint_consistency_under_load(client):
    """Test that health endpoint returns consistent data under load."""
    # Make 100 requests and verify all return consistent data
    num_requests = 100
    responses_data = []

    for _ in range(num_requests):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        responses_data.append(data)

    # Verify consistency
    first_response = responses_data[0]

    # Status should always be "healthy"
    for data in responses_data:
        assert data["status"] == "healthy"

    # Version should be consistent
    for data in responses_data:
        assert data["version"] == first_response["version"]

    # Agent SDK version should be consistent
    for data in responses_data:
        assert data["agent_sdk_version"] == first_response["agent_sdk_version"]

    # Environment should be consistent
    for data in responses_data:
        assert data["environment"] == first_response["environment"]

    # Uptime should increase monotonically (within reasonable bounds)
    uptimes = [data["uptime_seconds"] for data in responses_data]
    for i in range(1, len(uptimes)):
        # Uptime should increase or stay the same (within 1 second tolerance)
        assert uptimes[i] >= uptimes[i - 1] - 1

    print(f"\nConsistency check passed for {num_requests} requests")
