"""
IoT & Edge AI Platform - Week 9 Ultra-Rare Tier
Device SDK, edge model deployment, real-time sensor processing, offline-first AI
"""

import json
import time
import uuid
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class EdgeDevice:
    """Edge device representation."""
    device_id: str
    device_type: str  # "mobile", "iot", "embedded", "gateway"
    capabilities: Dict
    status: str = "online"
    last_heartbeat: float = field(default_factory=time.time)
    deployed_models: List[str] = field(default_factory=list)


@dataclass
class EdgeModel:
    """Model optimized for edge deployment."""
    model_id: str
    name: str
    framework: str  # "tensorflow_lite", "onnx", "pytorch_mobile", "core_ml"
    size_mb: float
    quantized: bool
    accelerator: Optional[str] = None  # "gpu", "npu", "tpu"


class EdgeModelDeployer:
    """Deploy AI models to edge devices."""
    
    def __init__(self):
        self.devices: Dict[str, EdgeDevice] = {}
        self.models: Dict[str, EdgeModel] = {}
        self.deployments: Dict[str, List[str]] = defaultdict(list)
    
    def register_device(self, device_type: str, capabilities: Dict) -> EdgeDevice:
        """Register edge device."""
        device = EdgeDevice(
            device_id=str(uuid.uuid4()),
            device_type=device_type,
            capabilities=capabilities
        )
        
        self.devices[device.device_id] = device
        return device
    
    def prepare_model_for_edge(self, model: Dict, target_device: str) -> EdgeModel:
        """Convert model for edge deployment."""
        device = self.devices.get(target_device)
        if not device:
            raise ValueError(f"Device {target_device} not found")
        
        # Select appropriate framework
        framework = self._select_framework(device)
        
        # Quantize for smaller size
        quantized_model = self._quantize_model(model, bits=8)
        
        edge_model = EdgeModel(
            model_id=str(uuid.uuid4()),
            name=model.get("name", "model"),
            framework=framework,
            size_mb=quantized_model["size_mb"],
            quantized=True,
            accelerator=device.capabilities.get("accelerator")
        )
        
        self.models[edge_model.model_id] = edge_model
        return edge_model
    
    def deploy_to_device(self, model_id: str, device_id: str) -> Dict:
        """Deploy model to edge device."""
        device = self.devices.get(device_id)
        model = self.models.get(model_id)
        
        if not device or not model:
            raise ValueError("Device or model not found")
        
        # Check device compatibility
        if not self._is_compatible(model, device):
            return {
                "status": "failed",
                "reason": "Device incompatible with model requirements"
            }
        
        # Deploy (in production: push to device via OTA update)
        device.deployed_models.append(model_id)
        self.deployments[device_id].append(model_id)
        
        return {
            "status": "deployed",
            "device_id": device_id,
            "model_id": model_id,
            "framework": model.framework,
            "size_mb": model.size_mb
        }
    
    def _select_framework(self, device: EdgeDevice) -> str:
        """Select best framework for device."""
        device_type = device.device_type
        
        if device_type == "mobile":
            if device.capabilities.get("os") == "ios":
                return "core_ml"
            else:
                return "tensorflow_lite"
        elif device_type == "iot":
            return "tensorflow_lite"
        elif device_type == "embedded":
            return "onnx"
        else:
            return "tensorflow_lite"
    
    def _quantize_model(self, model: Dict, bits: int = 8) -> Dict:
        """Quantize model for edge."""
        original_size = model.get("size_mb", 50.0)
        quantized_size = original_size * (bits / 32)
        
        return {
            "size_mb": quantized_size,
            "quantization_bits": bits,
            "compression_ratio": original_size / quantized_size
        }
    
    def _is_compatible(self, model: EdgeModel, device: EdgeDevice) -> bool:
        """Check model-device compatibility."""
        # Check memory
        available_memory = device.capabilities.get("memory_mb", 1000)
        if model.size_mb > available_memory * 0.5:  # Max 50% memory usage
            return False
        
        # Check framework support
        supported_frameworks = device.capabilities.get("frameworks", [])
        if supported_frameworks and model.framework not in supported_frameworks:
            return False
        
        return True


class SensorDataProcessor:
    """Real-time sensor data processing."""
    
    def __init__(self):
        self.sensors: Dict[str, Dict] = {}
        self.data_streams: Dict[str, List[Dict]] = defaultdict(list)
        self.processors: Dict[str, Any] = {}
    
    def register_sensor(self, sensor_type: str, sampling_rate_hz: float, device_id: str) -> str:
        """Register sensor for data collection."""
        sensor_id = str(uuid.uuid4())
        
        self.sensors[sensor_id] = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "sampling_rate_hz": sampling_rate_hz,
            "device_id": device_id,
            "status": "active",
            "samples_collected": 0
        }
        
        return sensor_id
    
    def process_sensor_data(self, sensor_id: str, data: List[float], timestamp: float) -> Dict:
        """Process incoming sensor data in real-time."""
        sensor = self.sensors.get(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} not found")
        
        # Store data point
        data_point = {
            "timestamp": timestamp,
            "values": data,
            "sensor_id": sensor_id
        }
        self.data_streams[sensor_id].append(data_point)
        
        # Real-time processing
        processed = self._apply_filters(data, sensor["sensor_type"])
        anomalies = self._detect_anomalies(processed)
        features = self._extract_features(processed)
        
        sensor["samples_collected"] += 1
        
        return {
            "sensor_id": sensor_id,
            "processed_data": processed,
            "anomalies": anomalies,
            "features": features,
            "latency_ms": (time.time() - timestamp) * 1000
        }
    
    def _apply_filters(self, data: List[float], sensor_type: str) -> List[float]:
        """Apply signal processing filters."""
        # Moving average filter
        window_size = 5
        filtered = []
        
        for i in range(len(data)):
            start = max(0, i - window_size + 1)
            window = data[start:i+1]
            filtered.append(np.mean(window))
        
        return filtered
    
    def _detect_anomalies(self, data: List[float]) -> List[Dict]:
        """Detect anomalies in sensor data."""
        if len(data) < 10:
            return []
        
        mean = np.mean(data)
        std = np.std(data)
        threshold = 3.0  # 3-sigma rule
        
        anomalies = []
        for i, value in enumerate(data):
            if abs(value - mean) > threshold * std:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "expected_range": (mean - threshold * std, mean + threshold * std)
                })
        
        return anomalies
    
    def _extract_features(self, data: List[float]) -> Dict:
        """Extract statistical features from sensor data."""
        if not data:
            return {}
        
        return {
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "range": float(np.max(data) - np.min(data)),
            "rms": float(np.sqrt(np.mean(np.square(data))))
        }


class OfflineAIEngine:
    """AI inference without internet connection."""
    
    def __init__(self):
        self.offline_models: Dict[str, Dict] = {}
        self.cache: Dict[str, Any] = {}
        self.sync_queue: List[Dict] = []
    
    def load_offline_model(self, model_id: str, model_path: str) -> Dict:
        """Load model for offline inference."""
        self.offline_models[model_id] = {
            "model_id": model_id,
            "model_path": model_path,
            "loaded_at": time.time(),
            "inference_count": 0,
            "last_used": time.time()
        }
        
        return {
            "status": "loaded",
            "model_id": model_id,
            "offline_ready": True
        }
    
    def offline_inference(self, model_id: str, input_data: Any) -> Dict:
        """Run inference offline."""
        model = self.offline_models.get(model_id)
        if not model:
            return {"status": "error", "message": "Model not loaded"}
        
        # Check cache first
        cache_key = self._generate_cache_key(input_data)
        if cache_key in self.cache:
            return {
                "prediction": self.cache[cache_key],
                "source": "cache",
                "latency_ms": 1
            }
        
        # Run inference
        start_time = time.time()
        prediction = self._run_inference(model_id, input_data)
        latency = (time.time() - start_time) * 1000
        
        # Cache result
        self.cache[cache_key] = prediction
        
        # Update stats
        model["inference_count"] += 1
        model["last_used"] = time.time()
        
        # Queue for sync when online
        self._queue_for_sync(model_id, input_data, prediction)
        
        return {
            "prediction": prediction,
            "source": "offline_model",
            "latency_ms": latency,
            "queued_for_sync": True
        }
    
    def _run_inference(self, model_id: str, input_data: Any) -> Any:
        """Execute model inference."""
        # Mock inference
        return {
            "class": np.random.randint(0, 10),
            "confidence": float(np.random.uniform(0.7, 0.99))
        }
    
    def _generate_cache_key(self, input_data: Any) -> str:
        """Generate cache key for input."""
        data_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _queue_for_sync(self, model_id: str, input_data: Any, prediction: Any):
        """Queue inference for sync when back online."""
        self.sync_queue.append({
            "model_id": model_id,
            "input": input_data,
            "prediction": prediction,
            "timestamp": time.time()
        })
    
    def sync_when_online(self) -> Dict:
        """Sync queued inferences when connection restored."""
        if not self.sync_queue:
            return {"synced": 0}
        
        synced_count = len(self.sync_queue)
        
        # Upload queued data (in production: to cloud)
        self.sync_queue = []
        
        return {
            "synced": synced_count,
            "queue_cleared": True
        }


class DeviceOrchestrator:
    """Orchestrate multiple edge devices."""
    
    def __init__(self):
        self.devices: Dict[str, EdgeDevice] = {}
        self.device_groups: Dict[str, List[str]] = defaultdict(list)
    
    def create_device_group(self, group_name: str, device_ids: List[str]) -> str:
        """Create group of devices for coordinated operations."""
        group_id = str(uuid.uuid4())
        self.device_groups[group_id] = device_ids
        
        return group_id
    
    def broadcast_to_group(self, group_id: str, command: Dict) -> Dict:
        """Broadcast command to device group."""
        device_ids = self.device_groups.get(group_id, [])
        
        results = {}
        for device_id in device_ids:
            result = self._send_command(device_id, command)
            results[device_id] = result
        
        return {
            "group_id": group_id,
            "devices_contacted": len(device_ids),
            "results": results
        }
    
    def _send_command(self, device_id: str, command: Dict) -> Dict:
        """Send command to device."""
        # In production: use MQTT, WebSocket, or HTTP
        return {
            "status": "success",
            "device_id": device_id,
            "command": command["type"]
        }
    
    def coordinate_inference(self, group_id: str, input_data: Any) -> Dict:
        """Coordinate inference across multiple devices."""
        device_ids = self.device_groups.get(group_id, [])
        
        # Split workload across devices
        results = []
        for i, device_id in enumerate(device_ids):
            # Each device processes a portion
            result = self._device_inference(device_id, input_data, partition=i)
            results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_results(results)
        
        return {
            "devices_used": len(device_ids),
            "aggregated_result": aggregated
        }
    
    def _device_inference(self, device_id: str, input_data: Any, partition: int) -> Dict:
        """Run inference on single device."""
        return {
            "device_id": device_id,
            "prediction": np.random.rand(),
            "partition": partition
        }
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate results from multiple devices."""
        predictions = [r["prediction"] for r in results]
        
        return {
            "mean_prediction": float(np.mean(predictions)),
            "std": float(np.std(predictions)),
            "consensus": float(np.median(predictions))
        }


class EdgeDataSyncManager:
    """Manage data sync between edge and cloud."""
    
    def __init__(self):
        self.pending_uploads: List[Dict] = []
        self.sync_policies: Dict[str, Dict] = {}
    
    def set_sync_policy(self, policy_name: str, conditions: Dict):
        """Define when to sync data."""
        self.sync_policies[policy_name] = {
            "policy_name": policy_name,
            "conditions": conditions,
            "created_at": time.time()
        }
    
    def queue_data_for_sync(self, data: Dict, priority: str = "normal"):
        """Queue data for sync to cloud."""
        self.pending_uploads.append({
            "data": data,
            "priority": priority,
            "queued_at": time.time(),
            "attempts": 0
        })
    
    def sync_to_cloud(self, connection_quality: str = "good") -> Dict:
        """Sync queued data to cloud."""
        if not self.pending_uploads:
            return {"synced": 0, "pending": 0}
        
        # Prioritize uploads
        sorted_queue = sorted(
            self.pending_uploads,
            key=lambda x: (0 if x["priority"] == "high" else 1, x["queued_at"])
        )
        
        synced = 0
        failed = 0
        
        # Adjust batch size based on connection
        batch_size = {
            "excellent": 100,
            "good": 50,
            "fair": 10,
            "poor": 1
        }.get(connection_quality, 10)
        
        for item in sorted_queue[:batch_size]:
            success = self._upload_to_cloud(item["data"])
            
            if success:
                self.pending_uploads.remove(item)
                synced += 1
            else:
                item["attempts"] += 1
                failed += 1
        
        return {
            "synced": synced,
            "failed": failed,
            "pending": len(self.pending_uploads)
        }
    
    def _upload_to_cloud(self, data: Dict) -> bool:
        """Upload data to cloud."""
        # Mock upload (in production: API call)
        return np.random.random() > 0.1  # 90% success rate


import hashlib
