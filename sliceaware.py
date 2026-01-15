class SliceAwareAlgorithm:
    def __init__(self, B, C):
        self.B=sorted(B)
        self.C=C
        self.P_hat=C*len(B)
        self.X={}
    def run_sa(self,user_i,P_B_i,L_B_i,L_i):
        if user_i not in self.X:
            self.X[user_i]=self.B[0]
        X_i = self.X[user_i] 
        P_X_i = P_B_i.get(X_i, 0)  # Packets transmitted with last used BWP
        
        # Calculate filter threshold
        denominator = len(self.B) - X_i
        if denominator == 0:
            filter_threshold = self.P_hat  # Avoid division by zero
        else:
            filter_threshold = self.P_hat // denominator
        
        # STAGE 2: BWP SELECTION DECISION
        if P_X_i > filter_threshold:
            # System is in full-swing, proceed with BWP selection
            
            # Find BWP j such that:
            # - L(j)_i <= L_i (satisfies latency requirement)
            # - L(j)_i is maximum among all eligible BWPs
            
            eligible_bwps = []
            
            for j in self.B:
                L_j_i = L_B_i.get(j, float('inf'))  # Default to infinity if no data
                
                # Check if this BWP satisfies latency requirement
                if L_j_i <= L_i:
                    eligible_bwps.append((j, L_j_i))
            
            # SPECIAL CASE: No eligible BWP found
            if not eligible_bwps:
                # If even highest numerology BWP doesn't satisfy requirement,
                # keep using the highest numerology BWP stored in X[i]
                selected_bwp = X_i
            else:
                # Select BWP with maximum latency among eligible ones
                # This efficiently uses BWPs - saves higher numerology for stricter requirements
                selected_bwp = max(eligible_bwps, key=lambda x: x[1])[0]
                
                # DISAMBIGUATION: If multiple BWPs have same max latency,
                # choose the one with lower numerology (lower index)
                max_latency = max(lat for _, lat in eligible_bwps)
                candidates = [j for j, lat in eligible_bwps if lat == max_latency]
                selected_bwp = min(candidates)  # Choose lowest numerology
                
        else:
            # Still in transient state, delay BWP selection
            # Keep using last used BWP
            selected_bwp = X_i
        
        # Update last used BWP for this user
        self.X[user_i] = selected_bwp
        
        return selected_bwp
    
    def update_statistics(self, user_i, bwp_j, latency, L_B_i, P_B_i):
        """
        Helper method to update latency and packet statistics
        
        Args:
            user_i: User index
            bwp_j: BWP used for transmission
            latency: Measured latency for this transmission
            L_B_i: Dict to update with latency statistics
            P_B_i: Dict to update with packet counts
        """
        # Initialize if needed
        if bwp_j not in L_B_i:
            L_B_i[bwp_j] = []
        if bwp_j not in P_B_i:
            P_B_i[bwp_j] = 0
        
        # Update latency (maintain running average)
        L_B_i[bwp_j].append(latency)
        
        # Update packet count
        P_B_i[bwp_j] += 1
    
    def get_average_latency(self, L_B_i):
        """
        Calculate average latency per BWP for user i
        
        Args:
            L_B_i: Dict {j: [list of latency measurements]}
            
        Returns:
            Dict {j: average_latency}
        """
        avg_latency = {}
        for j, latencies in L_B_i.items():
            if len(latencies) > 0:
                avg_latency[j] = sum(latencies) / len(latencies)
            else:
                avg_latency[j] = 0.0
        return avg_latency

