class PhysicalResourceAwareAlgorithm:
    def __init__(self, B, max_rho_config=None):
        self.B = B
        # MAX_rho(j): The total capacity for that BWP's numerology
        self.max_rho = max_rho_config if max_rho_config else {j: 100 for j in self.B}
        # Initial Stage: Algorithm starts with bwp=1 (mu=0).
        self.last_used_bwp = self.B[0] 

    def run_pra(self, r, history_map, weights_map, Tw):
        """
        r: Ratio value in (0, 1] for threshold calculation
        history_map: {j: [list of rho_k assignments]} over time window 
        weights_map: {j: [list of W_rho weights]} for each assignment
        Tw: The length of the time window
        """
        # 1. INITIAL STAGE: If history window is not yet full, use BWP with mu=0
        if any(len(history_map[j]) < Tw for j in self.B):
            return self.B[0]

        selected_bwp = self.last_used_bwp 
        find = False
        for j in reversed(self.B):
            h_j = history_map[j]
            w_j = weights_map[j]
            
            numerator = sum(w * rho for w, rho in zip(w_j, h_j))
            denominator = sum(w_j)
            b_occ_j = numerator / denominator if denominator != 0 else 0
            
            # Threshold t(j) = r * MAX_rho(j)
            threshold = r * self.max_rho.get(j, 100)
            
            # 3. SELECTION: Check if occupation is below the threshold
            if b_occ_j < threshold:
                selected_bwp = j
                find = True
                break
                
        self.last_used_bwp = selected_bwp
        return selected_bwp