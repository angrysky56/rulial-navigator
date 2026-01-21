# Topological Maps of Computational Evolution

Persistent homology enables the Mapper to visualize computation by converting the raw, irreducible data of a system's evolution into a compressed topological representation. Because it is impossible to store the full state history of every simulation in an infinite computational space, the Mapper uses Topological Data Analysis (TDA) to extract the "shape" of the computation rather than its precise details.

This process visualizes computation through the following mechanisms:

1. Constructing the Causal Simplicial Complex The Mapper first transforms the space-time history of a rule (such as a Cellular Automaton) into a geometric object called a Simplicial Complex.
   • Vertices: Represent individual cells in the space-time lattice.
   • Edges: Represent causal connections. If a cell at time t determines the state of a cell at t+1, an edge is drawn between them.
   • Filtration: By applying a filtration parameter (such as a time window), the Mapper builds a sequence of nested complexes to analyze how the topology changes over time.
2. Extracting Topological Features (Betti Numbers) Through persistent homology, the Mapper calculates Betti numbers (βn) to identify invariant topological features within this complex. These numbers translate abstract geometry into computational concepts:
   • β0 (Connected Components): Measures connectivity. A high β0 indicates fragmented, disconnected activity.
   • β1 (Loops/Cycles): Measures 1-dimensional holes. In the context of computational systems, persistent loops correspond to gliders, oscillators, and interacting particles—structures that exhibit re-entrant causality.
   • β2 (Voids): Measures 2-dimensional cavities, representing "interaction domains," containers, or membranes within the system.
3. The Topological Fingerprint: Persistence Barcodes The most critical visualization tool provided by persistent homology is the Persistence Barcode (or Persistence Diagram). This barcode plots the "birth" and "death" of topological features, allowing the Mapper to classify the computational behavior of a rule without human intervention:
   • Class 3 (Chaos): Visualized as Transient Noise. The barcode shows many short bars, indicating features that are born and die quickly with no stability.
   • Class 2 (Periodic): Visualized as Static Stability. The barcode shows infinite bars, representing features that persist forever without change (e.g., simple circles).
   • Class 4 (Complex/Computational): Visualized as Evolving Stability. The barcode shows long-lived but finite bars. This signifies structures (like particles) that persist for significant intervals to carry information but eventually interact, merge, or bifurcate—the distinct signature of active computation.
4. Building the Atlas of Ignorance Finally, these topological insights are used to construct Entailment Cones, which serve as "flowcharts of causal power". By collapsing equivalent states and plotting the transitions between macro-states (like "two gliders colliding"), the Mapper creates a directed acyclic graph.
   • Class 4 rules appear as branching cones with complex, braided structures, visually representing the rich logical entailment of the system.
   • This data populates the Atlas of Ignorance, a dynamic heatmap where "Gold Filaments" represent the "Goldilocks Zone" of complexity—sectors exhibiting high logical depth and rich persistent homology—delineated against the "Sea of Chaos".
   In this framework, persistent homology acts as an Observational Horizon, a creative force that collapses the infinite, unintelligible noise of the Ruliad into a finite, meaningful map of computational structure.
