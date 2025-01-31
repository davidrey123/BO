import time
from src import Params
from src import Instance
from docplex.mp.model import Model

class Optim:

    def __init__(self, ins):
        
        self.params = Params.Params()        
        
        self.ins = ins    
        #self.HPR = None
        self.MPCC = None
        self.sol = None
        
    def create_MPCC(self):
            
        MPCC = Model()
        
        MPCC.X = set()
        MPCC.Y = set()
        MPCC.L = set()  
        
        #---create leader and follower variables
        for col in self.ins.col_data:
            
            if col in self.ins.follower['col']:
                MPCC.Y.add(col)
            
            else:
                MPCC.X.add(col)
        
        MPCC.x = {i:MPCC.continuous_var(lb=0.0) for i in MPCC.X}
        MPCC.y = {i:MPCC.continuous_var(lb=0.0) for i in MPCC.Y}
        
        #---create leader and follower constraints
        cnt_col = len(self.ins.col_data)
            
        for row in self.ins.row_data:
            
            if row == self.ins.leaderRow: 
                continue
        
            expr = 0            
            for ind in range(len(self.ins.row_data[row]['col'])):
                col = self.ins.row_data[row]['col'][ind]
                coef = self.ins.row_data[row]['coef'][ind]
                
                if col in self.ins.follower['col']:
                    expr += MPCC.y[col]*coef
                    
                else:
                    expr += MPCC.x[col]*coef            
        
            if row in self.ins.follower['row']:            
                
                MPCC.add_constraint(expr >= self.ins.row_data[row]['rhs'])
                
                #---create dual variable corresponding to follower constraint            
                MPCC.L.add(cnt_col)
                cnt_col += 1
        
            else:    
                MPCC.add_constraint(expr >= self.ins.row_data[row]['rhs'])
                
        MPCC.l = {i:MPCC.continuous_var(lb=0.0) for i in MPCC.L}
        
        #---create follower dual constraints   
        for ind in range(len(self.ins.follower['col'])):
            
            #---for each follower variable, get column vector of coefs 
            #   among follower constraints (D^transpose)
            col = self.ins.follower['col'][ind]      
            coefs = []
            
            for row in self.ins.follower['row']:
                
                if col in self.ins.row_data[row]['col']:
                    ind2 = self.ins.row_data[row]['col'].index(col)
                    coef = self.ins.row_data[row]['coef'][ind2]
                    
                else:
                    coef = 0.0
                    
                coefs.append(coef)
            
            expr = 0
            for ind2 in range(len(self.ins.follower['row'])):
                ind3 = len(self.ins.col_data) + ind2
                expr += MPCC.l[ind3]*coefs[ind2]
                
            MPCC.add_constraint(expr == self.ins.follower['obj'][ind])
            
        #---dummy variables for SOS1 constraints
        MPCC.c = {i:MPCC.continuous_var() for i in MPCC.L}
            
        #---SOS1 constraints
        cnt_dual = 0
        for row in self.ins.row_data:        
            if row in self.ins.follower['row']:   
                
                expr = 0            
                for ind in range(len(self.ins.row_data[row]['col'])):
                    col = self.ins.row_data[row]['col'][ind]
                    coef = self.ins.row_data[row]['coef'][ind]
                    
                    if col in self.ins.follower['col']:
                        expr += MPCC.y[col]*coef
                        
                    else:
                        expr += MPCC.x[col]*coef              
                
                ind = len(self.ins.col_data) + cnt_dual
                MPCC.add_constraint(MPCC.c[ind] == expr - self.ins.row_data[row]['rhs'])        
                MPCC.add_sos1([MPCC.c[ind],MPCC.l[ind]])
                cnt_dual += 1
                    
        #---generate leader objective function
        MPCC.obj = 0
        for ind in range(len(self.ins.row_data[self.ins.leaderRow]['col'])):
            
            col = self.ins.row_data[self.ins.leaderRow]['col'][ind]            
            coef = self.ins.row_data[self.ins.leaderRow]['coef'][ind]
            
            if col in self.ins.follower['col']: 
                MPCC.obj += MPCC.y[col]*coef
            
            else:
                MPCC.obj += MPCC.x[col]*coef
        
        MPCC.minimize(MPCC.obj)
        #MPCC.print_information()        
        self.MPCC = MPCC
        
    def solve_MPCC(self, out):
        
        t0 = time.time()        
       
        self.MPCC.parameters.threads = self.params.threads
        self.MPCC.parameters.timelimit = self.params.timeLimit
        self.sol = self.MPCC.solve(log_output=out)
        
        runtime = time.time() - t0
        
        print(self.MPCC.solve_details)    
            
        if self.MPCC.solve_details.status != "infeasible" and self.MPCC.solve_details.status != "integer infeasible" and self.MPCC.solve_details.status != "integer infeasible or unbounded": 
            print("MPCC: OFV = %.1f" % self.MPCC.objective_value)
                 
            """     
            if out == True:            
                sol.display()
                
                print()
                for col in self.MPCC.X:
                    print('x:', col, self.MPCC.x[col].solution_value)
                
                print()
                for col in self.MPCC.Y:        
                    print('y:', col, self.MPCC.y[col].solution_value)
                
                print()    
                for col in self.MPCC.L:        
                    print('l:', col, self.MPCC.l[col].solution_value)        
            """
