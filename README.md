# EcoGuard — Distributed Acoustic Forest Monitoring Simulation

An educational **Python + Pygame** simulation exploring how a wireless sensor network could detect acoustic events and route alerts through a multi-hop mesh network.

The project was developed for a university wireless networks course. It focuses on **sensor-network behavior, routing, event propagation and network resilience**, not on production-grade field detection.

## What the Simulation Does

- Places a network of acoustic sensor nodes across a forest map
- Simulates different event types such as chainsaw, gunshot and vehicle sounds
- Propagates event waves with different speed/range parameters
- Routes alerts to a gateway using multi-hop paths
- Visualizes packet movement across the network
- Models node battery depletion and route changes when nodes become unavailable
- Displays network health, hop count, packet totals and event history in a live dashboard

## System Flow

```text
Acoustic event
     ↓
Nearby sensors detect it
     ↓
Route selection
     ↓
Multi-hop packet forwarding
     ↓
Gateway receives alert
     ↓
Dashboard updates
```

## Tech Stack

- Python 3
- Pygame
- Graph / BFS-based routing
- Wireless sensor network simulation
- Event-driven visualization

## Run Locally

```bash
git clone https://github.com/omrfarukkahraman/ecoguard-dagitik-akustik-algilama-ile-ormanlari-koruma.git
cd ecoguard-dagitik-akustik-algilama-ile-ormanlari-koruma
pip install pygame
python ecoguard_simulation.py
```

## Controls

| Control | Action |
|---|---|
| Left click | Create chainsaw event |
| Right click | Create gunshot event |
| Middle click / `C` | Create vehicle event |
| `SPACE` | Pause / resume |
| `R` | Reset the network |
| `H` | Show / hide communication links |
| `V` | Show / hide sensing ranges |

## What I Practiced

- Modeling a distributed sensor network
- Multi-hop routing and path recovery
- Event propagation and visualization
- Battery-aware node behavior
- Real-time simulation dashboards

## Scope

This is a software simulation created for academic exploration of wireless sensor-network concepts. It is not a deployed forest surveillance system.

## Author

**Ömer Faruk Kahraman**  
Computer Engineering · 2026
