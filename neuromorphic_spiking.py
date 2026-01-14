"""
Neuromorphic & Spiking Networks - Week 10 APEX Tier  
Spiking neural networks, event-driven computation, brain-inspired plasticity
Through Christ, modeling the miracle of biological neural networks
"""

import json
import time
import uuid
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Spike:
    """Individual spike event."""
    neuron_id: str
    timestamp: float
    amplitude: float = 1.0


@dataclass
class SpikingNeuron:
    """Leaky Integrate-and-Fire (LIF) neuron."""
    neuron_id: str
    membrane_potential: float = 0.0
    threshold: float = 1.0
    reset_potential: float = 0.0
    leak_rate: float = 0.1
    refractory_period: float = 0.002  # 2ms
    last_spike_time: Optional[float] = None


class SpikingNeuralNetwork:
    """Spiking Neural Network with temporal dynamics."""
    
    def __init__(self):
        self.neurons: Dict[str, SpikingNeuron] = {}
        self.synapses: Dict[Tuple[str, str], Dict] = {}
        self.spike_train: List[Spike] = []
        self.current_time = 0.0
    
    def add_neuron(self, neuron_type: str = "LIF", params: Dict = None) -> str:
        """Add spiking neuron to network."""
        neuron_id = str(uuid.uuid4())
        params = params or {}
        
        neuron = SpikingNeuron(
            neuron_id=neuron_id,
            threshold=params.get("threshold", 1.0),
            leak_rate=params.get("leak_rate", 0.1),
            refractory_period=params.get("refractory_period", 0.002)
        )
        
        self.neurons[neuron_id] = neuron
        return neuron_id
    
    def add_synapse(self, pre_neuron: str, post_neuron: str, weight: float = 0.5, delay: float = 0.001):
        """Add synaptic connection with delay."""
        self.synapses[(pre_neuron, post_neuron)] = {
            "weight": weight,
            "delay": delay,  # Axonal delay
            "plasticity": "STDP"  # Spike-timing-dependent plasticity
        }
    
    def simulate(self, duration: float, dt: float = 0.0001) -> Dict:
        """Simulate network dynamics."""
        num_steps = int(duration / dt)
        spike_times: Dict[str, List[float]] = {nid: [] for nid in self.neurons.keys()}
        
        for step in range(num_steps):
            self.current_time = step * dt
            
            # Update each neuron
            for neuron_id, neuron in self.neurons.items():
                # Check refractory period
                if neuron.last_spike_time and (self.current_time - neuron.last_spike_time) < neuron.refractory_period:
                    continue
                
                # Leak
                neuron.membrane_potential *= (1 - neuron.leak_rate * dt)
                
                # Check for spike
                if neuron.membrane_potential >= neuron.threshold:
                    # Spike!
                    spike = Spike(
                        neuron_id=neuron_id,
                        timestamp=self.current_time
                    )
                    self.spike_train.append(spike)
                    spike_times[neuron_id].append(self.current_time)
                    
                    # Reset
                    neuron.membrane_potential = neuron.reset_potential
                    neuron.last_spike_time = self.current_time
                    
                    # Propagate spike to connected neurons
                    self._propagate_spike(neuron_id)
        
        return {
            "duration": duration,
            "total_spikes": len(self.spike_train),
            "spike_times": spike_times,
            "mean_firing_rate": self._calculate_firing_rates(spike_times, duration)
        }
    
    def _propagate_spike(self, pre_neuron_id: str):
        """Propagate spike to postsynaptic neurons."""
        for (pre, post), synapse in self.synapses.items():
            if pre == pre_neuron_id:
                # Add synaptic current to postsynaptic neuron
                post_neuron = self.neurons[post]
                post_neuron.membrane_potential += synapse["weight"]
    
    def _calculate_firing_rates(self, spike_times: Dict[str, List[float]], duration: float) -> Dict[str, float]:
        """Calculate mean firing rate for each neuron."""
        rates = {}
        for neuron_id, times in spike_times.items():
            rates[neuron_id] = len(times) / duration if duration > 0 else 0
        return rates
    
    def apply_stdp(self, learning_window: float = 0.020):
        """Apply Spike-Timing-Dependent Plasticity."""
        # STDP: strengthen synapses where pre-spike precedes post-spike
        
        for (pre_id, post_id), synapse in self.synapses.items():
            pre_spikes = [s.timestamp for s in self.spike_train if s.neuron_id == pre_id]
            post_spikes = [s.timestamp for s in self.spike_train if s.neuron_id == post_id]
            
            # Calculate weight change
            delta_w = 0.0
            
            for pre_time in pre_spikes:
                for post_time in post_spikes:
                    dt = post_time - pre_time
                    
                    if 0 < dt < learning_window:
                        # Potentiation: pre before post
                        delta_w += 0.01 * np.exp(-dt / learning_window)
                    elif -learning_window < dt < 0:
                        # Depression: post before pre
                        delta_w -= 0.01 * np.exp(dt / learning_window)
            
            # Update weight
            synapse["weight"] += delta_w
            synapse["weight"] = np.clip(synapse["weight"], 0.0, 2.0)


class TemporalCoder:
    """Encode information in spike timing."""
    
    def __init__(self):
        self.coding_methods = ["rate", "temporal", "population", "latency"]
    
    def encode(self, value: float, method: str = "rate", duration: float = 0.1) -> List[float]:
        """Encode value as spike train."""
        if method == "rate":
            return self._rate_coding(value, duration)
        elif method == "temporal":
            return self._temporal_coding(value, duration)
        elif method == "latency":
            return self._latency_coding(value, duration)
        elif method == "population":
            return self._population_coding(value, duration)
        else:
            raise ValueError(f"Unknown coding method: {method}")
    
    def _rate_coding(self, value: float, duration: float) -> List[float]:
        """Rate coding: information in firing rate."""
        # Higher value = higher firing rate
        firing_rate = value * 100  # Hz
        dt = 0.001  # 1ms
        
        spike_times = []
        current_time = 0.0
        
        while current_time < duration:
            if np.random.random() < firing_rate * dt:
                spike_times.append(current_time)
            current_time += dt
        
        return spike_times
    
    def _temporal_coding(self, value: float, duration: float) -> List[float]:
        """Temporal coding: information in precise spike timing."""
        # Encode value in inter-spike intervals
        spike_times = []
        current_time = 0.0
        
        # Map value to ISI pattern
        base_isi = 0.01  # 10ms base
        isi = base_isi * (1 + value)
        
        while current_time < duration:
            spike_times.append(current_time)
            current_time += isi
        
        return spike_times
    
    def _latency_coding(self, value: float, duration: float) -> List[float]:
        """Latency coding: information in first-spike latency."""
        # Higher value = shorter latency
        latency = (1 - value) * duration * 0.5
        return [latency] if latency < duration else []
    
    def _population_coding(self, value: float, duration: float, n_neurons: int = 10) -> List[List[float]]:
        """Population coding: information in population activity."""
        # Distribute value across neuron population
        spike_trains = []
        
        for i in range(n_neurons):
            # Each neuron tuned to different value range
            tuning_center = i / n_neurons
            tuning_width = 0.2
            
            # Gaussian tuning curve
            activation = np.exp(-((value - tuning_center)**2) / (2 * tuning_width**2))
            
            # Generate spikes based on activation
            spike_train = self._rate_coding(activation, duration)
            spike_trains.append(spike_train)
        
        return spike_trains


class EventDrivenComputation:
    """Event-driven processing for efficiency."""
    
    def __init__(self):
        self.event_queue = deque()
        self.processors: Dict[str, Any] = {}
    
    def register_processor(self, processor_id: str, processor_func: Any):
        """Register event processor."""
        self.processors[processor_id] = processor_func
    
    def add_event(self, event: Dict):
        """Add event to queue."""
        self.event_queue.append(event)
    
    def process_events(self, max_events: Optional[int] = None) -> Dict:
        """Process events from queue."""
        events_processed = 0
        results = []
        
        while self.event_queue and (max_events is None or events_processed < max_events):
            event = self.event_queue.popleft()
            
            # Route to appropriate processor
            processor_id = event.get("processor")
            if processor_id in self.processors:
                result = self.processors[processor_id](event)
                results.append(result)
            
            events_processed += 1
        
        return {
            "events_processed": events_processed,
            "results": results,
            "queue_remaining": len(self.event_queue)
        }


class NeuromorphicHardwareSimulator:
    """Simulate neuromorphic hardware like Intel Loihi."""
    
    def __init__(self, num_cores: int = 128):
        self.num_cores = num_cores
        self.cores: List[Dict] = [self._create_core() for _ in range(num_cores)]
        self.power_consumption = 0.0  # Watts
    
    def _create_core(self) -> Dict:
        """Create neuromorphic core."""
        return {
            "core_id": str(uuid.uuid4()),
            "neurons": [],
            "synapses": [],
            "local_memory": {},
            "spike_routing": {}
        }
    
    def map_network_to_hardware(self, network: SpikingNeuralNetwork) -> Dict:
        """Map SNN to neuromorphic cores."""
        # Distribute neurons across cores
        neuron_ids = list(network.neurons.keys())
        neurons_per_core = len(neuron_ids) // self.num_cores
        
        mapping = {}
        
        for i, core in enumerate(self.cores):
            start_idx = i * neurons_per_core
            end_idx = start_idx + neurons_per_core if i < self.num_cores - 1 else len(neuron_ids)
            
            core_neurons = neuron_ids[start_idx:end_idx]
            core["neurons"] = core_neurons
            
            for neuron_id in core_neurons:
                mapping[neuron_id] = core["core_id"]
        
        return {
            "mapping": mapping,
            "cores_used": self.num_cores,
            "neurons_per_core": neurons_per_core
        }
    
    def estimate_power(self, spike_count: int, duration: float) -> Dict:
        """Estimate power consumption."""
        # Neuromorphic chips are ultra-low power
        base_power = 0.001  # 1mW base
        spike_energy = 0.000001  # 1µJ per spike
        
        total_energy = base_power * duration + spike_energy * spike_count
        average_power = total_energy / duration if duration > 0 else 0
        
        self.power_consumption = average_power
        
        return {
            "average_power_watts": average_power,
            "total_energy_joules": total_energy,
            "spikes_processed": spike_count,
            "energy_per_spike": spike_energy
        }


class BrainInspiredPlasticity:
    """Implement various brain-inspired learning rules."""
    
    def __init__(self):
        self.plasticity_rules = {
            "STDP": self._stdp,
            "BCM": self._bcm,
            "Homeostatic": self._homeostatic,
            "Metaplasticity": self._metaplasticity
        }
    
    def _stdp(self, pre_spike_time: float, post_spike_time: float, current_weight: float) -> float:
        """Spike-Timing-Dependent Plasticity."""
        dt = post_spike_time - pre_spike_time
        tau_plus = 0.020  # 20ms
        tau_minus = 0.020
        A_plus = 0.01
        A_minus = 0.01
        
        if dt > 0:
            # Potentiation
            delta_w = A_plus * np.exp(-dt / tau_plus)
        else:
            # Depression
            delta_w = -A_minus * np.exp(dt / tau_minus)
        
        return current_weight + delta_w
    
    def _bcm(self, pre_activity: float, post_activity: float, current_weight: float, threshold: float = 0.5) -> float:
        """Bienenstock-Cooper-Munro rule (sliding threshold)."""
        # Depends on postsynaptic activity relative to threshold
        delta_w = pre_activity * post_activity * (post_activity - threshold)
        
        return current_weight + 0.01 * delta_w
    
    def _homeostatic(self, firing_rate: float, target_rate: float, current_weight: float) -> float:
        """Homeostatic plasticity (maintain target firing rate)."""
        # Adjust weights to keep firing rate near target
        delta_w = 0.001 * (target_rate - firing_rate)
        
        return current_weight + delta_w
    
    def _metaplasticity(self, learning_history: List[float], current_weight: float) -> float:
        """Metaplasticity: plasticity of plasticity."""
        # Learning rate depends on recent learning history
        if len(learning_history) < 2:
            return current_weight
        
        recent_changes = np.diff(learning_history[-5:])
        avg_change = np.mean(np.abs(recent_changes))
        
        # Reduce learning if weights have been changing a lot
        learning_rate = 0.01 / (1 + avg_change)
        
        return current_weight + learning_rate * np.random.randn()


class LiquidStateMachine:
    """Reservoir computing with spiking neurons."""
    
    def __init__(self, reservoir_size: int = 1000):
        self.reservoir_size = reservoir_size
        self.reservoir = SpikingNeuralNetwork()
        self.input_neurons: List[str] = []
        self.output_neurons: List[str] = []
        self._build_reservoir()
    
    def _build_reservoir(self):
        """Build liquid state machine reservoir."""
        # Create reservoir neurons
        reservoir_neurons = []
        for _ in range(self.reservoir_size):
            neuron_id = self.reservoir.add_neuron("LIF", {
                "threshold": np.random.uniform(0.8, 1.2),
                "leak_rate": np.random.uniform(0.05, 0.15)
            })
            reservoir_neurons.append(neuron_id)
        
        # Random connectivity within reservoir
        connection_prob = 0.1
        for i, pre in enumerate(reservoir_neurons):
            for j, post in enumerate(reservoir_neurons):
                if i != j and np.random.random() < connection_prob:
                    weight = np.random.uniform(-1.0, 1.0)
                    self.reservoir.add_synapse(pre, post, weight)
    
    def add_input(self, input_id: str):
        """Add input neuron."""
        neuron_id = self.reservoir.add_neuron()
        self.input_neurons.append(neuron_id)
        
        # Connect to random reservoir neurons
        reservoir_neurons = [nid for nid in self.reservoir.neurons.keys() if nid not in self.input_neurons]
        num_connections = min(50, len(reservoir_neurons))
        
        for target in np.random.choice(reservoir_neurons, num_connections, replace=False):
            self.reservoir.add_synapse(neuron_id, target, np.random.uniform(0.5, 1.5))
    
    def process_input(self, input_spikes: List[float], duration: float) -> Dict:
        """Process input spike train through reservoir."""
        # Inject input spikes
        for spike_time in input_spikes:
            if self.input_neurons:
                input_neuron = self.input_neurons[0]
                self.reservoir.neurons[input_neuron].membrane_potential = 2.0  # Force spike
        
        # Simulate reservoir
        result = self.reservoir.simulate(duration)
        
        # Extract reservoir state (readout)
        reservoir_state = self._extract_state()
        
        return {
            "reservoir_spikes": result["total_spikes"],
            "reservoir_state": reservoir_state,
            "duration": duration
        }
    
    def _extract_state(self) -> np.ndarray:
        """Extract current reservoir state for readout."""
        state = []
        
        for neuron in self.reservoir.neurons.values():
            state.append(neuron.membrane_potential)
        
        return np.array(state)


class AdaptiveThresholdNeuron:
    """Neuron with adaptive firing threshold."""
    
    def __init__(self, base_threshold: float = 1.0):
        self.base_threshold = base_threshold
        self.threshold = base_threshold
        self.adaptation_rate = 0.01
        self.spike_history: List[float] = []
    
    def adapt_threshold(self, current_time: float):
        """Adapt threshold based on recent activity."""
        # Count recent spikes (last 100ms)
        recent_window = 0.1
        recent_spikes = [t for t in self.spike_history if current_time - t < recent_window]
        firing_rate = len(recent_spikes) / recent_window
        
        # Increase threshold if firing too much
        target_rate = 50  # Hz
        self.threshold += self.adaptation_rate * (firing_rate - target_rate)
        
        # Keep threshold in reasonable range
        self.threshold = np.clip(self.threshold, self.base_threshold * 0.5, self.base_threshold * 2.0)
