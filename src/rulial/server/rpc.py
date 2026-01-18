import asyncio
import os

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..compression.metrics import TelemetryAnalyzer

# Import our components
from ..engine.eca import ECAEngine
from ..engine.totalistic import Totalistic2DEngine
from ..mapper.atlas import Atlas
from ..mapper.topology import TopologyMapper
from ..navigator.annealing import AnnealingController
from ..navigator.classifier import RuleClassifier
from ..quantum.superfluid import SuperfluidFilter


def int_to_rule_str(n: int) -> str:
    # Logic matched to src/rulial/runners/probe_2d.py (Lines 69-76)
    bin_str = format(int(n), "018b")

    # In probe_2d.py:
    # int_to_bits(n, 18) -> creates np.array from bin_str
    # rule_bits[0:9] -> First 9 bits -> Used for BORN
    # rule_bits[9:18] -> Last 9 bits -> Used for SURVIVE

    # Example: n=1 => 00...001
    # bin_str = "000000000000000001"
    # B = [0..8] = 000000000 -> No Births
    # S = [9..17] = 000000001 -> Survive 8 (index 8 of slice, which is index 17 of full)
    # Wait, enumerate(rule_bits[9:18]):
    # If S = [0,0,0,0,0,0,0,0,1], then '1' is at index 8.
    # So b=1 at index 8 of the chunk.
    # So it means S8.

    # Let's map it:
    b_bits = bin_str[0:9]
    s_bits = bin_str[9:18]

    born = [i for i, bit in enumerate(b_bits) if bit == "1"]
    survive = [i for i, bit in enumerate(s_bits) if bit == "1"]

    return f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"


app = FastAPI(title="Rulial Navigator RPC")

# Serve static files (for observatory.html)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# State
atlas = Atlas()
annealing = AnnealingController()
topology_mapper = TopologyMapper()
telemetry_analyzer = TelemetryAnalyzer()
superfluid = SuperfluidFilter()


@app.get("/")
async def root():
    return RedirectResponse(url="/static/observatory.html")


# Models
class ProbeRequest(BaseModel):
    rule: int
    steps: int = 500
    width: int = 200


class NavigateRequest(BaseModel):
    center: int
    steps: int = 10


class AnalysisResult(BaseModel):
    rule: int
    wolfram_class: int
    rigid_ratio: float
    loss_slope: float
    entropy: float
    betti_1: int
    superfluid_entropy: float
    classification: str


@app.post("/probe", response_model=AnalysisResult)
async def probe_rule(req: ProbeRequest):
    """
    Run a full analysis on a single rule.
    """
    # 1. Simulate
    engine = ECAEngine(req.rule)
    spacetime = engine.simulate(req.width, req.steps, init_condition="random")

    # 2. Compress (V1)
    telemetry = telemetry_analyzer.analyze(spacetime)

    # 3. Classify (V1)
    w_class = RuleClassifier.classify(telemetry)

    # 4. Topology (V1)
    topo = topology_mapper.compute_persistence(spacetime)

    # 5. Quantum Superfluid (V2)
    sf_data = superfluid.analyze(spacetime)

    # 7. Record
    atlas.record(req.rule, telemetry, w_class, topo)

    return AnalysisResult(
        rule=req.rule,
        wolfram_class=w_class,
        rigid_ratio=telemetry.rigid_ratio_lzma,
        loss_slope=telemetry.loss_derivative,
        entropy=telemetry.shannon_entropy,
        betti_1=topo.betti_1,
        superfluid_entropy=sf_data.get("normalized_entropy", 0.0),
        classification=sf_data.get("classification", "unknown"),
    )


@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket, rule: str = "B3/S23"):
    """
    Stream a 2D Totalistic Universe over WebSocket.
    """
    await websocket.accept()
    rule_str = rule  # Local var for compatibility

    # 1. Init Engine
    try:
        # Check if integer
        if rule_str.isdigit():
            rule_str = int_to_rule_str(int(rule_str))

        engine = Totalistic2DEngine(rule_str)
    except Exception as e:
        await websocket.close(code=1000, reason=f"Invalid Rule: {e}")
        return

    # 2. Config
    height = 64
    width = 64

    # 3. Simulation Loop
    # We yield frames one by one
    # Initial state
    grid = engine.init_grid(height, width, "random")

    try:
        while True:
            # Send Frame (flattened binary or check if text is faster for simple JS parsing)
            # For simplicity, sending bytes. 0 = Dead, 1 = Alive.
            # Flatten grid
            data = grid.astype("uint8").tobytes()
            await websocket.send_bytes(data)

            # Step
            grid = engine.step(grid)

            # Rate limit/Throttle
            await asyncio.sleep(0.05)  # 20 FPS

    except Exception as e:
        print(f"Stream Closed: {e}")
    finally:
        pass


@app.get("/atlas")
async def get_atlas():
    """Get the current map state."""
    return atlas.get_map_status()


@app.get("/atlas/filaments")
async def get_filaments():
    """Get discovered Class 4 filaments."""
    return atlas.get_gold_filaments()


@app.get("/atlas/history")
async def get_history():
    """Get the full exploration history (The Star Chart)."""
    import json

    # Prefer atlas_grid.json (from 2D Mapper V3)
    history_file = "atlas_grid.json"
    if not os.path.exists(history_file):
        history_file = "atlas_data.json"  # Fallback to V2 list
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            return json.load(f)
    return []


def start_server(port: int = 8000):
    uvicorn.run(app, host="127.0.0.1", port=port)
