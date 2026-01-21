from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class TMState:
    """Represents the instantaneous description of a Turing Machine."""

    tape: Tuple[
        int, ...
    ]  # Frozen tuple for hashing, sparse representation logic handled externally
    head_pos: int
    state: int

    def __repr__(self):
        # Determine tape bounds for display

        return f"State({self.state}, Head={self.head_pos})"


@dataclass
class TuringMachineRule:
    """
    Represents the rule set for a Turing Machine.
    Supports non-determinism: one (state, color) can map to multiple outcomes.
    """

    # Key: (current_state, read_color)
    # Value: List of (write_color, move_dir, new_state)
    transitions: Dict[Tuple[int, int], List[Tuple[int, int, int]]]

    @staticmethod
    def from_wolfram_code(
        code: int, num_states: int = 2, num_colors: int = 2
    ) -> "TuringMachineRule":
        """
        Construct a DETRMINISTIC rule from a Wolfram code number.
        Standard enumeration for (n, k) TMs.
        """
        transitions = {}
        # Parse code into transitions...
        # For (2,2) TMs, code is 0..4095.
        # Inputs order: (0,0), (0,1), (1,0), (1,1) typically?
        # Wolfram convention: (state, color). State 1..n.
        # Actually Wolfram uses 1-indexed states in docs, commonly 0-indexed in code implementations.
        # Let's stick to 0-indexed states (0, 1) and colors (0, 1).

        # (2,2) TM has 4 inputs: (s0, c0), (s0, c1), (s1, c0), (s1, c1)
        # Each output has 3 bits: new_color (1), dir (1), new_state (1)?
        # Actually there are 2*2*2 = 8 options per input.
        # 8^4 = 4096 rules.

        inputs = [(s, c) for s in range(num_states) for c in range(num_colors)]

        for s, c in inputs:
            # Extract 3 bits (or more for larger TMs)
            # This is specific to (2,2) for now.
            # Let's assume generic logic:
            # Digit = code % (num_colors * 2 * num_states)
            base = num_colors * 2 * num_states
            op_code = code % base
            code //= base

            # Decode op_code
            # Generic decoding usually: new_color, dir, new_state
            # But the order varies by convention.
            # Let's use a standard mapping or just specific for (2,2) as 8*8*8*8.

            # For (2,2): output range 0..7.
            # Let's use:
            # new_color = op % 2
            # dir = (op // 2) % 2  (0 -> -1, 1 -> +1)
            # new_state = (op // 4) % 2

            write_color = op_code % num_colors
            dir_bit = (op_code // num_colors) % 2
            move_dir = 1 if dir_bit == 1 else -1
            new_state = (op_code // (num_colors * 2)) % num_states

            transitions[(s, c)] = [(write_color, move_dir, new_state)]

        return TuringMachineRule(transitions)


class MultiwayTuringSystem:
    """
    Manages the evolution of a Turing Machine in Rulial Space (Multiway System).
    """

    def __init__(self, rule: TuringMachineRule):
        self.rule = rule

    def step(self, state: TMState) -> List[TMState]:
        """Perform one step of evolution, returning all possible next states."""
        # Unpack tape to read
        # Note: Optimization needed for large tapes.
        # For now, simplistic conversion from tuple to dict
        tape_dict = {i: val for i, val in enumerate(state.tape)}
        current_head = state.head_pos
        current_state = state.state

        current_color = tape_dict.get(current_head, 0)

        # Get possibilities
        outcomes = self.rule.transitions.get((current_state, current_color), [])

        next_states = []
        for write_color, move_dir, new_state_id in outcomes:
            # Create new config
            new_tape_dict = tape_dict.copy()
            new_tape_dict[current_head] = write_color

            # Trim zeroes for canonical representation
            # Find min and max index
            # Logic for canonical representation handled in _make_state

            # Re-implementing sparse storage for TMState to involve explicit bounds
            # This allows efficient storage

            next_states.append(
                self._make_state(new_tape_dict, current_head + move_dir, new_state_id)
            )

        return next_states

    def _make_state(self, tape_dict: Dict[int, int], head: int, state: int) -> TMState:
        # Prune zeroes
        keys = [k for k, v in tape_dict.items() if v != 0]
        if not keys:
            return TMState(tape=(), head_pos=0, state=state)  # Empty tape

        min_k, max_k = min(keys), max(keys)
        # We store the segment from min_k to max_k
        # And we store the offset of the head relative to min_k?
        # Wait, if we move the head far away into 0-space, we need to track it.

        full_min = min(min_k, head)
        full_max = max(max_k, head)

        canonical_tape = []
        for i in range(full_min, full_max + 1):
            canonical_tape.append(tape_dict.get(i, 0))

        # We normalize so full_min is index 0 in the tuple?
        # No, that loses absolute position.
        # But for state equivalence, Shift Equivalence is usually assumed.
        # Let's assume Shift Equivalence: State is defined by (tape_pattern, head_relative_to_pattern, internal_state).

        return TMState(
            tape=tuple(canonical_tape),
            head_pos=head - full_min,  # Head relative to start of slice
            state=state,
        )

    def evolve(self, initial_state: TMState, steps: int) -> Dict[int, List[TMState]]:
        """
        Evolve for N steps.
        Returns: {step: [states]}
        """
        history = {0: [initial_state]}
        current_layer = {initial_state}

        for t in range(1, steps + 1):
            next_layer = set()
            for s in current_layer:
                outcomes = self.step(s)
                next_layer.update(outcomes)

            history[t] = list(next_layer)
            current_layer = next_layer

            if not current_layer:
                break

        return history


class FunctionMiner:
    """
    Mines the Rulial Space for rules that perform specific functions.
    Searches for a path: InitialState (Input) -> ... -> TargetState (Output).
    """

    def __init__(self, num_states: int = 2, num_colors: int = 2):
        self.num_states = num_states
        self.num_colors = num_colors

    def mine(
        self,
        input_tape: Tuple[int, ...],
        target_tape: Tuple[int, ...],
        max_steps: int = 15,
        rule_range: range = range(4096),
    ) -> List[Dict]:
        """
        Search for rules that transform input_tape to target_tape.
        Returns list of solutions: {'rule': int, 'path': List[TMState], 'steps': int}
        """
        solutions = []

        # Canonicalize target for comparison
        # We only care that the non-zero parts match.
        target_pattern = self._clean_tape(target_tape)

        initial_state = TMState(tape=input_tape, head_pos=0, state=0)

        for code in rule_range:
            rule = TuringMachineRule.from_wolfram_code(
                code, self.num_states, self.num_colors
            )
            system = MultiwayTuringSystem(rule)

            # BFS Search
            visited = {initial_state}

            # Simple bounded BFS
            # Note: This is per-rule. For true multiway, we'd search the union of rules.
            # But "Mining" usually means finding *a* rule that does it.

            # Optimization: Don't store full history if we just want reachability.
            # But we want the path.

            # We limit depth (steps)
            found_for_rule = False

            # To handle steps, we can use a slightly different loop structure
            current_generation = [(initial_state, [initial_state])]

            for step in range(max_steps):
                next_generation = []
                for curr, path in current_generation:
                    if self._matches(curr.tape, target_pattern):
                        solutions.append({"rule": code, "path": path, "steps": step})
                        found_for_rule = True
                        break  # Found a solution for this rule

                    if found_for_rule:
                        break

                    # Evolve
                    next_states = system.step(curr)
                    for n in next_states:
                        # Hashing TMState is crucial here.
                        # Assuming TMState is frozen and hashable.
                        # We need to prune to avoid cycles if deterministic,
                        # but in NDTM cycles are valid paths?
                        # Let's avoid cycles for efficiency.
                        # Note: path-based visited check?
                        # Simple visited check for BFS is fine.
                        # But wait, visited needs to be per-rule.
                        if n not in visited:
                            visited.add(n)
                            next_generation.append((n, path + [n]))

                if found_for_rule:
                    break
                current_generation = next_generation
                if not current_generation:
                    break

        return solutions

    def _clean_tape(self, tape: Tuple[int, ...]) -> Tuple[int, ...]:
        """Strip leading/trailing zeros."""
        if not tape:
            return ()
        start, end = 0, len(tape)
        while start < end and tape[start] == 0:
            start += 1
        while end > start and tape[end - 1] == 0:
            end -= 1
        return tape[start:end]

    def _matches(self, tape: Tuple[int, ...], target_pattern: Tuple[int, ...]) -> bool:
        """Check if tape content matches target pattern (ignoring surrounding zeros)."""
        return self._clean_tape(tape) == target_pattern
