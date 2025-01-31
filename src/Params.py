class Params:           
        
    def __init__(self):
    
        #---instance params
        self.default_lb_var = 0.0
        self.default_ub_var = 1e9
               
        #---optimization params
        self.timeLimit = 300
        self.threads = 1
        self.inf = 1e9 
        self.optGap = 1e-4
        self.intTol = 1e-4       

