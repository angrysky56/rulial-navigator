
import torch
import torch.nn as nn
from torch_geometric.nn import MessagePassing


class SheafLaplacianLayer(MessagePassing):
    """
    Neural Sheaf Laplacian Layer (Hansen & Gebhart 2021).
    Learns restriction maps F_{u->v} to construct the Sheaf Laplacian L.
    
    Architecture:
    1. Restriction Learner: Phi(x_u, x_v) -> O(d) matrix
    2. Laplacian Construction: L = B^T B
    3. Diffusion: Y = (I - alpha * L) X
    """
    
    def __init__(self, in_channels: int, stalk_dim: int, num_heads: int = 1):
        super().__init__(aggr='add')
        self.in_channels = in_channels
        self.stalk_dim = stalk_dim
        
        # Learner for restriction maps: Maps node features (u, v) to a scalar (or matrix)
        # For simplicity (1D stalk), we predict a single value "rho" for each edge
        # which represents the relationship: Resonant (+1) or Tense (-1)
        self.restriction_learner = nn.Sequential(
            nn.Linear(2 * in_channels, 32),
            nn.Tanh(),
            nn.Linear(32, stalk_dim * stalk_dim) 
        )
        
        # Learnable diffusion rate
        self.alpha = nn.Parameter(torch.tensor(0.5))

    def forward(self, x, edge_index):
        # 1. Learn Restriction Maps
        # We process edges: predict F_{u->v} from (x_u, x_v)
        row, col = edge_index
        
        # Concatenate edge features
        edge_input = torch.cat([x[row], x[col]], dim=-1)
        
        # Predict restriction map values (-1 to 1)
        # Using Tanh to bound the relationship
        restrictions = torch.tanh(self.restriction_learner(edge_input))
        
        # 2. Construct Sheaf Laplacian action (implicit)
        # Instead of building the full matrix L (which is huge), apply it:
        # L f(u) = d_u f(u) - sum_{v~u} F_{v->u}^T F_{u->v} f(v)
        
        # We need to compute the "sheaf diffusion" message
        # Message = F_{u->v} x_u  (transported value)
        
        # But wait, Hansen & Gebhart's L = B^T B formulation implies:
        # We minimize differences: || F_{u->v} x_u - F_{v->u} x_v ||^2
        
        # Let's verify the diffusion layer:
        # x_new = x - alpha * L * x
        
        return self.propagate(edge_index, x=x, restrictions=restrictions)

    def message(self, x_j, restrictions):
        # The neighbor 'j' sends its value transformed by the restriction map?
        # Actually, Sheaf Laplacian diffusion is:
        # (L x)_i = D_i x_i - sum_{j in N(i)} F_{j->i} x_j
        
        # Here we approximate:
        # restrictions is implicitly F_{i->j} * F_{j->i} term 
        # If restrictions > 0 (resonant), we aggregate similarly
        # If restrictions < 0 (tense), we aggregate opposingly
        
        return x_j * restrictions

    def update(self, aggr_out, x):
        # Update node: x_new = x - alpha * (Degree * x - Aggregation)
        # This is a bit simplified. A proper diagonal degree matrix D depends on restrictions.
        
        # Assuming simplified normalized Laplacian D=I for conceptual diffusion
        return x - self.alpha * (x - aggr_out)

class SheafLearner(nn.Module):
    def __init__(self, in_features=18, hidden_dim=64, out_dim=2):
        super().__init__()
        
        self.encoder = nn.Linear(in_features, hidden_dim)
        
        # Stack of Sheaf Layers
        self.sheaf1 = SheafLaplacianLayer(hidden_dim, stalk_dim=1)
        self.sheaf2 = SheafLaplacianLayer(hidden_dim, stalk_dim=1)
        
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, out_dim)
        )

    def forward(self, x, edge_index):
        x = torch.relu(self.encoder(x))
        x = self.sheaf1(x, edge_index)
        x = torch.relu(x)
        x = self.sheaf2(x, edge_index)
        return self.decoder(x)
