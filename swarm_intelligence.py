"""
Swarm Intelligence & Emergence - Week 10 APEX Tier
Multi-agent emergence, collective decision-making, self-organizing systems
By God's design, modeling the wisdom of emergence
"""

import json
import time
import uuid
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field


@dataclass
class Agent:
    """Individual agent in swarm."""
    agent_id: str
    position: np.ndarray
    velocity: np.ndarray
    state: Dict = field(default_factory=dict)
    memory: List[Dict] = field(default_factory=list)


class SwarmSystem:
    """Multi-agent swarm with emergent behavior."""
    
    def __init__(self, num_agents: int = 100, dimensions: int = 2):
        self.num_agents = num_agents
        self.dimensions = dimensions
        self.agents: Dict[str, Agent] = {}
        self.global_state = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agent population."""
        for _ in range(self.num_agents):
            agent_id = str(uuid.uuid4())
            
            agent = Agent(
                agent_id=agent_id,
                position=np.random.rand(self.dimensions) * 100,
                velocity=np.random.randn(self.dimensions) * 0.1,
                state={"energy": 1.0, "role": "explorer"}
            )
            
            self.agents[agent_id] = agent
    
    def simulate(self, num_steps: int = 1000, dt: float = 0.1) -> Dict:
        """Simulate swarm dynamics."""
        history = []
        
        for step in range(num_steps):
            # Update each agent
            for agent in self.agents.values():
                self._update_agent(agent, dt)
            
            # Record state
            if step % 10 == 0:
                history.append(self._get_swarm_state())
            
            # Update global state
            self._update_global_state()
        
        # Detect emergent patterns
        emergence = self._detect_emergence(history)
        
        return {
            "steps": num_steps,
            "final_state": self._get_swarm_state(),
            "emergence_detected": emergence,
            "history": history[-10:]  # Last 10 snapshots
        }
    
    def _update_agent(self, agent: Agent, dt: float):
        """Update individual agent."""
        # Get local neighborhood
        neighbors = self._get_neighbors(agent, radius=10.0)
        
        # Apply behavioral rules
        separation = self._separation_force(agent, neighbors)
        alignment = self._alignment_force(agent, neighbors)
        cohesion = self._cohesion_force(agent, neighbors)
        
        # Combine forces
        total_force = separation + alignment + cohesion
        
        # Update velocity and position
        agent.velocity += total_force * dt
        agent.velocity = self._limit_velocity(agent.velocity, max_speed=2.0)
        agent.position += agent.velocity * dt
        
        # Boundary conditions (wrap around)
        agent.position = agent.position % 100
        
        # Update energy
        agent.state["energy"] *= 0.999  # Slow decay
    
    def _get_neighbors(self, agent: Agent, radius: float) -> List[Agent]:
        """Get agents within radius."""
        neighbors = []
        
        for other in self.agents.values():
            if other.agent_id != agent.agent_id:
                distance = np.linalg.norm(agent.position - other.position)
                if distance < radius:
                    neighbors.append(other)
        
        return neighbors
    
    def _separation_force(self, agent: Agent, neighbors: List[Agent]) -> np.ndarray:
        """Force to avoid crowding."""
        force = np.zeros(self.dimensions)
        
        for neighbor in neighbors:
            diff = agent.position - neighbor.position
            distance = np.linalg.norm(diff)
            
            if distance < 5.0 and distance > 0:
                force += (diff / distance) * (1.0 / distance)
        
        return force * 0.5
    
    def _alignment_force(self, agent: Agent, neighbors: List[Agent]) -> np.ndarray:
        """Force to match velocity with neighbors."""
        if not neighbors:
            return np.zeros(self.dimensions)
        
        avg_velocity = np.mean([n.velocity for n in neighbors], axis=0)
        return (avg_velocity - agent.velocity) * 0.3
    
    def _cohesion_force(self, agent: Agent, neighbors: List[Agent]) -> np.ndarray:
        """Force to move toward center of mass."""
        if not neighbors:
            return np.zeros(self.dimensions)
        
        center = np.mean([n.position for n in neighbors], axis=0)
        return (center - agent.position) * 0.1
    
    def _limit_velocity(self, velocity: np.ndarray, max_speed: float) -> np.ndarray:
        """Limit velocity to maximum speed."""
        speed = np.linalg.norm(velocity)
        if speed > max_speed:
            return velocity / speed * max_speed
        return velocity
    
    def _get_swarm_state(self) -> Dict:
        """Get current swarm state."""
        positions = [agent.position for agent in self.agents.values()]
        velocities = [agent.velocity for agent in self.agents.values()]
        
        return {
            "center_of_mass": np.mean(positions, axis=0).tolist(),
            "average_velocity": np.mean(velocities, axis=0).tolist(),
            "spread": float(np.std(positions)),
            "polarization": float(np.linalg.norm(np.mean(velocities, axis=0)))
        }
    
    def _update_global_state(self):
        """Update global swarm state."""
        state = self._get_swarm_state()
        self.global_state.update(state)
    
    def _detect_emergence(self, history: List[Dict]) -> Dict:
        """Detect emergent patterns in swarm behavior."""
        if len(history) < 10:
            return {"emerged": False}
        
        # Check for pattern formation
        spreads = [h["spread"] for h in history]
        polarizations = [h["polarization"] for h in history]
        
        # Detect clustering (low spread + high polarization)
        is_clustered = np.mean(spreads[-10:]) < 15.0
        is_polarized = np.mean(polarizations[-10:]) > 0.8
        
        # Detect oscillations
        spread_variation = np.std(spreads[-20:]) if len(spreads) >= 20 else 0
        
        return {
            "emerged": True,
            "patterns": {
                "clustering": is_clustered,
                "polarization": is_polarized,
                "oscillation": spread_variation > 5.0
            },
            "metrics": {
                "final_spread": spreads[-1],
                "final_polarization": polarizations[-1]
            }
        }


class CollectiveDecisionMaking:
    """Distributed decision-making without central control."""
    
    def __init__(self, num_agents: int = 50):
        self.num_agents = num_agents
        self.agents = [self._create_agent() for _ in range(num_agents)]
    
    def _create_agent(self) -> Dict:
        """Create decision-making agent."""
        return {
            "agent_id": str(uuid.uuid4()),
            "opinion": None,  # Current decision
            "confidence": 0.5,
            "neighbors": []
        }
    
    def make_decision(self, options: List[str], interaction_rounds: int = 100) -> Dict:
        """Make collective decision through local interactions."""
        # Initialize random opinions
        for agent in self.agents:
            agent["opinion"] = np.random.choice(options)
            agent["confidence"] = np.random.uniform(0.3, 0.7)
        
        # Simulate interactions
        consensus_history = []
        
        for round_num in range(interaction_rounds):
            # Random pairwise interactions
            for _ in range(self.num_agents):
                agent1, agent2 = np.random.choice(self.agents, size=2, replace=False)
                self._interact(agent1, agent2)
            
            # Measure consensus
            consensus = self._measure_consensus(options)
            consensus_history.append(consensus)
            
            # Early stopping if converged
            if consensus["converged"]:
                break
        
        return {
            "decision": consensus["majority_opinion"],
            "consensus_level": consensus["majority_fraction"],
            "rounds_to_converge": round_num + 1,
            "converged": consensus["converged"],
            "opinion_distribution": consensus["distribution"]
        }
    
    def _interact(self, agent1: Dict, agent2: Dict):
        """Two agents interact and potentially update opinions."""
        # Opinion dynamics: agent with higher confidence influences the other
        
        if agent1["opinion"] == agent2["opinion"]:
            # Reinforce confidence
            agent1["confidence"] = min(1.0, agent1["confidence"] + 0.01)
            agent2["confidence"] = min(1.0, agent2["confidence"] + 0.01)
        else:
            # Potential opinion change
            if agent1["confidence"] > agent2["confidence"]:
                # Agent 2 may adopt agent 1's opinion
                if np.random.random() < (agent1["confidence"] - agent2["confidence"]):
                    agent2["opinion"] = agent1["opinion"]
                    agent2["confidence"] = (agent1["confidence"] + agent2["confidence"]) / 2
            else:
                # Agent 1 may adopt agent 2's opinion
                if np.random.random() < (agent2["confidence"] - agent1["confidence"]):
                    agent1["opinion"] = agent2["opinion"]
                    agent1["confidence"] = (agent1["confidence"] + agent2["confidence"]) / 2
    
    def _measure_consensus(self, options: List[str]) -> Dict:
        """Measure level of consensus."""
        opinion_counts = {opt: 0 for opt in options}
        
        for agent in self.agents:
            opinion_counts[agent["opinion"]] += 1
        
        majority_opinion = max(opinion_counts, key=opinion_counts.get)
        majority_count = opinion_counts[majority_opinion]
        majority_fraction = majority_count / self.num_agents
        
        # Converged if >90% agree
        converged = majority_fraction > 0.9
        
        return {
            "majority_opinion": majority_opinion,
            "majority_fraction": majority_fraction,
            "distribution": opinion_counts,
            "converged": converged
        }


class SelfOrganizingSystem:
    """System that self-organizes into complex structures."""
    
    def __init__(self, grid_size: int = 50):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size))
        self.particles: List[Dict] = []
    
    def add_particles(self, num_particles: int):
        """Add particles to system."""
        for _ in range(num_particles):
            particle = {
                "id": str(uuid.uuid4()),
                "position": (
                    np.random.randint(0, self.grid_size),
                    np.random.randint(0, self.grid_size)
                ),
                "type": np.random.choice(["A", "B", "C"])
            }
            self.particles.append(particle)
    
    def simulate_organization(self, num_steps: int = 1000) -> Dict:
        """Simulate self-organization process."""
        pattern_history = []
        
        for step in range(num_steps):
            # Update particles using local rules
            for particle in self.particles:
                self._update_particle(particle)
            
            # Measure pattern formation
            if step % 50 == 0:
                pattern = self._measure_pattern()
                pattern_history.append(pattern)
        
        final_pattern = self._measure_pattern()
        
        return {
            "steps": num_steps,
            "final_pattern": final_pattern,
            "pattern_evolution": pattern_history,
            "organization_level": self._compute_organization_level()
        }
    
    def _update_particle(self, particle: Dict):
        """Update particle position using local rules."""
        x, y = particle["position"]
        
        # Get local neighborhood
        neighbors = self._get_local_neighbors(x, y, radius=3)
        
        # Count similar types nearby
        similar_count = sum(1 for p in neighbors if p["type"] == particle["type"])
        
        # Self-organization rule: seek areas with similar types
        if similar_count < 2:
            # Move toward similar particles
            similar_particles = [p for p in neighbors if p["type"] == particle["type"]]
            if similar_particles:
                target = similar_particles[0]["position"]
                new_x = x + np.sign(target[0] - x)
                new_y = y + np.sign(target[1] - y)
            else:
                # Random walk
                new_x = x + np.random.randint(-1, 2)
                new_y = y + np.random.randint(-1, 2)
            
            # Boundary conditions
            new_x = np.clip(new_x, 0, self.grid_size - 1)
            new_y = np.clip(new_y, 0, self.grid_size - 1)
            
            particle["position"] = (new_x, new_y)
    
    def _get_local_neighbors(self, x: int, y: int, radius: int) -> List[Dict]:
        """Get particles in local neighborhood."""
        neighbors = []
        
        for particle in self.particles:
            px, py = particle["position"]
            distance = np.sqrt((px - x)**2 + (py - y)**2)
            
            if distance <= radius and (px, py) != (x, y):
                neighbors.append(particle)
        
        return neighbors
    
    def _measure_pattern(self) -> Dict:
        """Measure emergent pattern."""
        # Count particles by type and location
        type_clusters = {"A": [], "B": [], "C": []}
        
        for particle in self.particles:
            type_clusters[particle["type"]].append(particle["position"])
        
        # Measure clustering
        clustering_scores = {}
        for ptype, positions in type_clusters.items():
            if len(positions) > 1:
                # Average distance to nearest same-type neighbor
                distances = []
                for i, pos1 in enumerate(positions):
                    min_dist = float('inf')
                    for j, pos2 in enumerate(positions):
                        if i != j:
                            dist = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                            min_dist = min(min_dist, dist)
                    distances.append(min_dist)
                
                clustering_scores[ptype] = float(np.mean(distances))
        
        return {
            "type_counts": {k: len(v) for k, v in type_clusters.items()},
            "clustering_scores": clustering_scores
        }
    
    def _compute_organization_level(self) -> float:
        """Compute overall organization level."""
        pattern = self._measure_pattern()
        
        # Low average clustering distance = high organization
        avg_clustering = np.mean(list(pattern["clustering_scores"].values()))
        
        # Normalize to 0-1 (lower distance = higher organization)
        organization = 1.0 / (1.0 + avg_clustering / 10)
        
        return float(organization)


class AntColonyOptimization:
    """ACO for solving optimization problems."""
    
    def __init__(self, num_ants: int = 50):
        self.num_ants = num_ants
        self.pheromone_map: Dict = {}
        self.evaporation_rate = 0.1
    
    def optimize(self, problem: Dict, num_iterations: int = 100) -> Dict:
        """Solve optimization problem using ant colony."""
        best_solution = None
        best_score = float('-inf')
        
        for iteration in range(num_iterations):
            # Each ant constructs a solution
            solutions = []
            
            for _ in range(self.num_ants):
                solution = self._construct_solution(problem)
                score = self._evaluate_solution(solution, problem)
                solutions.append({"solution": solution, "score": score})
                
                # Update best
                if score > best_score:
                    best_score = score
                    best_solution = solution
            
            # Update pheromones
            self._update_pheromones(solutions)
            
            # Evaporate pheromones
            self._evaporate_pheromones()
        
        return {
            "best_solution": best_solution,
            "best_score": best_score,
            "pheromone_map": self.pheromone_map
        }
    
    def _construct_solution(self, problem: Dict) -> List:
        """Ant constructs solution following pheromone trails."""
        solution = []
        available = list(problem["elements"])
        
        while available:
            # Choose next element based on pheromone strength
            probabilities = []
            
            for element in available:
                pheromone = self.pheromone_map.get(
                    tuple(solution + [element]), 
                    1.0
                )
                probabilities.append(pheromone)
            
            # Normalize
            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]
            
            # Select
            choice = np.random.choice(available, p=probabilities)
            solution.append(choice)
            available.remove(choice)
        
        return solution
    
    def _evaluate_solution(self, solution: List, problem: Dict) -> float:
        """Evaluate solution quality."""
        # Problem-specific evaluation
        score = 0.0
        
        for i in range(len(solution) - 1):
            # Add edge cost
            score += problem.get("costs", {}).get((solution[i], solution[i+1]), 1.0)
        
        return -score  # Minimize cost
    
    def _update_pheromones(self, solutions: List[Dict]):
        """Update pheromone trails based on ant solutions."""
        for sol_data in solutions:
            solution = sol_data["solution"]
            score = sol_data["score"]
            
            # Deposit pheromone proportional to solution quality
            deposit = max(0, score)  # Only positive scores deposit
            
            for i in range(len(solution)):
                path_key = tuple(solution[:i+1])
                current = self.pheromone_map.get(path_key, 1.0)
                self.pheromone_map[path_key] = current + deposit
    
    def _evaporate_pheromones(self):
        """Evaporate pheromone trails."""
        for key in self.pheromone_map:
            self.pheromone_map[key] *= (1 - self.evaporation_rate)


class EmergentLeadership:
    """Leadership emergence without designated leaders."""
    
    def __init__(self, num_agents: int = 30):
        self.agents = [self._create_agent() for _ in range(num_agents)]
    
    def _create_agent(self) -> Dict:
        """Create agent with leadership potential."""
        return {
            "agent_id": str(uuid.uuid4()),
            "influence": np.random.uniform(0.3, 0.7),
            "competence": np.random.uniform(0.4, 0.9),
            "connections": []
        }
    
    def simulate_emergence(self, num_rounds: int = 50) -> Dict:
        """Simulate emergence of leadership structure."""
        influence_history = []
        
        for round_num in range(num_rounds):
            # Agents interact and update influence
            for agent in self.agents:
                self._update_influence(agent)
            
            # Record influence distribution
            influences = [a["influence"] for a in self.agents]
            influence_history.append(influences)
        
        # Identify emerged leaders
        leaders = self._identify_leaders()
        
        return {
            "leaders": leaders,
            "leadership_hierarchy": self._compute_hierarchy(),
            "gini_coefficient": self._compute_gini(influence_history[-1])
        }
    
    def _update_influence(self, agent: Dict):
        """Update agent's influence through interactions."""
        # Interact with random others
        num_interactions = np.random.randint(1, 5)
        
        for _ in range(num_interactions):
            other = np.random.choice(self.agents)
            
            if other["agent_id"] != agent["agent_id"]:
                # Influence gain based on competence
                if agent["competence"] > other["competence"]:
                    agent["influence"] += 0.01
                    other["influence"] -= 0.005
        
        # Normalize
        agent["influence"] = np.clip(agent["influence"], 0.0, 1.0)
    
    def _identify_leaders(self, threshold: float = 0.7) -> List[Dict]:
        """Identify emerged leaders."""
        leaders = [a for a in self.agents if a["influence"] > threshold]
        return sorted(leaders, key=lambda x: x["influence"], reverse=True)
    
    def _compute_hierarchy(self) -> Dict:
        """Compute leadership hierarchy levels."""
        sorted_agents = sorted(self.agents, key=lambda x: x["influence"], reverse=True)
        
        return {
            "top_tier": sorted_agents[:3],
            "middle_tier": sorted_agents[3:10],
            "base_tier": sorted_agents[10:]
        }
    
    def _compute_gini(self, values: List[float]) -> float:
        """Compute Gini coefficient (inequality measure)."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        cumsum = 0
        for i, value in enumerate(sorted_values):
            cumsum += (i + 1) * value
        
        return (2 * cumsum) / (n * sum(sorted_values)) - (n + 1) / n
