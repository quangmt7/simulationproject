class PhysicalResourceAwareAlgorithm:
    def __init__(self, bwps,max_prbs,ratio=0.99,time_window=1):
        self.bwps=bwps
        self.ratio=ratio
        self.time_window=time_window
        self.max_prbs=max_prbs
        self.threshold={j: ratio*max_prbs[j] for j in bwps}
        self.history = {j: [] for j in bwps}
        
        self.weight_full = 100
        self.weight_partial = 1
        self.last_used_bwp = 1
    def calculate_bocc(self, j):

        h_j = self.history[j]
        if not h_j:
            return 0.0
        
        weighted_sum = 0
        sum_weights = 0
        
        for rho_k in h_j:
            # Determine weight based on whether it's a full assignment 
            w = self.weight_full if rho_k == self.max_prbs[j] else self.weight_partial
            weighted_sum += w * rho_k
            sum_weights += w
            
        return weighted_sum / sum_weights if sum_weights > 0 else 0
    def choose_bwp(self):
        find=False
        selected_bwp=self.last_used_bwp
        for j in self.bwps:
            b_jocc_j=self.calculate_bocc(j)
            if b_jocc_j<self.threshold[j]:
                selected_bwp=j
                find=True
                break
            
        if find:
            self.last_used_bwp=selected_bwp
            return selected_bwp
        else:
            return self.last_used_bwp
    def update_history(self, bwp_index, assigned_prbs):
        """
        Updates PRB assignment history and maintains the time window size.
        """
        self.history[bwp_index].append(assigned_prbs)
        
        # Manually maintain the time window 
        if len(self.history[bwp_index]) > self.time_window:
            self.history[bwp_index].pop(0)

# --- Example ---
# Define BWPs and their maximum capacities
available_bwps = [1, 2, 3, 4, 5]
max_prbs = {1: 273, 2: 273, 3: 135, 4: 135, 5: 66}

pra = PhysicalResourceAwareAlgorithm(available_bwps, max_prbs)

# Update BWP 1 with full load

pra.update_history(1,273)

# The algorithm will now evaluate BWP 1 as saturated and move to BWP 2
next_bwp = pra.choose_bwp()
print(f"Selected BWP: {next_bwp}")  
