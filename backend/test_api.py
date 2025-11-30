import httpx
import json
import time
import subprocess
import sys
import os

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server to start...")
    for _ in range(30):
        try:
            response = httpx.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("Server is up!")
                return True
        except httpx.ConnectError:
            time.sleep(1)
    print("Server failed to start.")
    return False

def test_health():
    print("\nTesting /health...")
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict():
    print("\nTesting /api/v1/predict...")
    payload = {
        "ship_id": "SHIP-123",
        "voyage_duration_days": 15.5,
        "avg_speed": 12.0,
        "distance_traveled": 4500.0,
        "port_time_ratio": 0.2,
        "fuel_consumption": 50.0,
        "temperature_avg": 28.0,
        "last_cleaning_days": 180
    }
    response = httpx.post(f"{BASE_URL}/api/v1/predict", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert "biofouling_level" in response.json()

def test_predict_batch():
    print("\nTesting /api/v1/predict/batch...")
    payload = {
        "voyages": [
            {
                "ship_id": "SHIP-123",
                "voyage_duration_days": 15.5,
                "avg_speed": 12.0,
                "distance_traveled": 4500.0,
                "port_time_ratio": 0.2,
                "fuel_consumption": 50.0,
                "temperature_avg": 28.0,
                "last_cleaning_days": 180
            },
            {
                "ship_id": "SHIP-456",
                "voyage_duration_days": 10.0,
                "avg_speed": 18.0,
                "distance_traveled": 4000.0,
                "port_time_ratio": 0.1,
                "fuel_consumption": 40.0,
                "temperature_avg": 15.0,
                "last_cleaning_days": 30
            }
        ]
    }
    response = httpx.post(f"{BASE_URL}/api/v1/predict/batch", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()["predictions"]) == 2

def run_tests():
    # Start server in background
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        if wait_for_server():
            test_health()
            test_predict()
            test_predict_batch()
            print("\nAll tests passed!")
        else:
            print("Skipping tests as server is not available.")
    except Exception as e:
        print(f"\nTest failed: {e}")
    finally:
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_tests()
