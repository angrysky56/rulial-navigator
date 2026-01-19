# cd /your-path-to/rulial-navigator && uv run python -c
from rulial.compression.flow import CompressionFlowAnalyzer
from rulial.mapper.tpe import TPEAnalyzer
from rulial.mining.extractor import ParticleMiner
from rulial.mining.oligon import OligonCounter

rule = "B078/S012478"
print("=" * 60)
print(f"FULL ANALYSIS: {rule}")
print("=" * 60)

# 1. Compression Flow
print("\n📊 COMPRESSION FLOW")
cfa = CompressionFlowAnalyzer()
cf_result = cfa.analyze(rule)
print(cf_result.summary())

# 2. T-P+E
print("\n\n🌀 T-P+E ANALYSIS")
tpe = TPEAnalyzer()
tpe_result = tpe.analyze(rule)
print(tpe_result.summary())

# 3. Oligons
print("\n\n⚛️ OLIGON CENSUS")
oc = OligonCounter()
ol_result = oc.count(rule)
print(ol_result.summary())

# 4. Particle Mining
print("\n\n⛏️ PARTICLE MINING")
miner = ParticleMiner(rule)
particles = miner.mine()
print(f"Found {len(particles)} particles:")
for p in particles:
    print(
        f"  - {p.name}: period={p.period}, velocity={p.velocity}, spaceship={p.is_spaceship}"
    )
