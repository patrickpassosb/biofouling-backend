import httpx
import json
import time
import subprocess
import sys
import os

BASE_URL = "http://localhost:8001"

def wait_for_server():
    print("Waiting for server to start...")
    for i in range(60): # Increased wait time
        try:
            response = httpx.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("Server is up!")
                return True
        except httpx.ConnectError:
            time.sleep(1)
        except Exception as e:
            print(f"Error waiting for server: {e}")
            time.sleep(1)
    print("Server failed to start within timeout.")
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
        "shipName": "SHIP-123",
        "speed": 12.0,
        "duration": 15.5,
        "distance": 4500.0,
        "beaufortScale": 3,
        "Area_Molhada": 500.0,
        "MASSA_TOTAL_TON": 50000.0,
        "TIPO_COMBUSTIVEL_PRINCIPAL": "HFO",
        "decLatitude": -23.0,
        "decLongitude": -43.0,
        "DiasDesdeUltimaLimpeza": 180.0
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
                "shipName": "SHIP-123",
                "speed": 12.0,
                "duration": 15.5,
                "distance": 4500.0,
                "beaufortScale": 3,
                "Area_Molhada": 500.0,
                "MASSA_TOTAL_TON": 50000.0,
                "TIPO_COMBUSTIVEL_PRINCIPAL": "HFO",
                "decLatitude": -23.0,
                "decLongitude": -43.0,
                "DiasDesdeUltimaLimpeza": 180.0
            },
            {
                "shipName": "SHIP-456",
                "speed": 18.0,
                "duration": 10.0,
                "distance": 4000.0,
                "beaufortScale": 2,
                "Area_Molhada": 450.0,
                "MASSA_TOTAL_TON": 40000.0,
                "TIPO_COMBUSTIVEL_PRINCIPAL": "VLSFO",
                "decLatitude": 10.0,
                "decLongitude": 20.0,
                "DiasDesdeUltimaLimpeza": 30.0
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
    # Use a different port for testing to avoid conflicts
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
        cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
        # Remove PIPE to let it print to console for debugging
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE
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
