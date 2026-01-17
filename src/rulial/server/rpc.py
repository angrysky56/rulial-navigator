import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from ..compression.metrics import TelemetryAnalyzer

# Import our components
from ..engine.eca import ECAEngine
from ..mapper.atlas import Atlas
from ..mapper.topology import TopologyMapper
from ..navigator.annealing import AnnealingController
from ..navigator.classifier import RuleClassifier
from ..quantum.superfluid import SuperfluidFilter

app = FastAPI(title="Rulial Navigator RPC")

# State
atlas = Atlas()
annealing = AnnealingController()
topology_mapper = TopologyMapper()
telemetry_analyzer = TelemetryAnalyzer()
superfluid = SuperfluidFilter()


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


@app.get("/atlas")
async def get_atlas():
    """Get the current map state."""
    return atlas.get_map_status()


@app.get("/atlas/filaments")
async def get_filaments():
    """Get discovered Class 4 filaments."""
    return atlas.get_gold_filaments()


def start_server(port: int = 8000):
    uvicorn.run(app, host="127.0.0.1", port=port)
