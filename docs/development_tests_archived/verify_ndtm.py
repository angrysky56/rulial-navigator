from rulial.engine.turing import TuringMachineRule, MultiwayTuringSystem, TMState

# Manually define a non-deterministic rule
# State 0, Read 0 -> Two possibilities:
# 1. Write 1, Move R (+1), State 0
# 2. Write 1, Move L (-1), State 0
nd_transitions = {
    (0, 0): [
        (1, 1, 0),  # Branch A
        (1, -1, 0)  # Branch B
    ]
}

rule = TuringMachineRule(nd_transitions)
system = MultiwayTuringSystem(rule)

initial_state = TMState(tape=(0,), head_pos=0, state=0)

print("Evolving NDTM...")
history = system.evolve(initial_state, steps=2)

for t, states in history.items():
    print(f"Step {t}: {len(states)} states")
    for s in states:
        print(f"  {s}")
