import numpy as np
from src import Params

class Instance:

    def __init__(self, name):
        
        self.name = name
        self.params = Params.Params()        
        
        self.col_data = {}      #---data of all columns in the mps file
        self.row_data = {}      #---data of all rows in the mps file
        self.leaderRow = None   #---name of the objective function row in the mps file
        self.follower = {}      #---data of the follower: objective function, columns and rows in the aux file        
        
        self.nLcol = 0
        self.nLrow = 0
        self.nFcol = 0
        self.nFrow = 0
        
        self.read_mps()
        self.read_aux()
        
        #print("1",len(self.col_data))
        #print("1",len(self.row_data))
        
        self.format_model()
        
        #print("2",len(self.col_data))
        #print("2",len(self.row_data))
        
    def read_mps(self):    
        
        file = "data/" + self.name + ".mps"
        data = open(file, "r")
        lines_data = data.readlines()
        data.close()

        col_data = {}
        row_data = {}
        
        reading_rows = False
        reading_columns = False
        reading_rhs = False
        reading_bounds = False
        reading_integers = False

        for line in lines_data:
            ls = line.split()

            '''
            if ls[0] == 'NAME':
                instance_name = ls[1]
                continue
            '''

            if ls[0] == 'ROWS':
                reading_rows = True
                #cnt_row = 0
                continue

            if ls[0] == 'COLUMNS':
                reading_rows = False
                reading_columns = True
                #cnt_col = 0
                continue

            if ls[0] == 'RHS' and len(ls) == 1:
                reading_columns = False
                reading_rhs = True
                continue

            if ls[0] == 'BOUNDS':
                reading_rhs = False
                reading_bounds = True
                continue

            if ls[0] == 'ENDATA':
                reading_rhs = False
                reading_bounds = False
                continue

            if reading_rows == True:
                row = ls[1]                

                if ls[0] == 'N':
                    #---create dict for leader obj assuming minimization
                    row_data[row] = {'col': [], 'coef': []}
                    self.leaderRow = row

                elif (ls[0] == 'G' or ls[0] == 'L' or ls[0] == 'E'):                
                    #---create dict for constraint, default RHS is 0                    
                    row_data[row] = {'dir': ls[0], 'col': [], 'coef': [], 'rhs': 0}

            if reading_columns == True:

                if ls[2] == "'INTORG'":
                    reading_integers = True
                    continue

                elif ls[2] == "'INTEND'":
                    reading_integers = False
                    continue

                col = ls[0]                
                
                if reading_integers == False:
                    col_data[col] = {'lb': self.params.default_lb_var, 'ub': None, 'int': False}

                else:
                    col_data[col] = {'lb': self.params.default_lb_var, 'ub': None, 'int': True}

                if len(ls) == 3:
                    
                    row = ls[1]
                    
                    row_data[row]['col'].append(col)
                    row_data[row]['coef'].append(float(ls[2]))

                elif len(ls) == 5:
                    
                    row = ls[1]
                    row2 = ls[3]
                    
                    row_data[row]['col'].append(col)
                    row_data[row]['coef'].append(float(ls[2]))
                    row_data[row2]['col'].append(col)
                    row_data[row2]['coef'].append(float(ls[4]))

                else:
                    print('>>> unknown line length (columns)')

            if reading_rhs == True:

                if len(ls) == 3:
                    
                    row = ls[1]
                    
                    row_data[row]['rhs'] = float(ls[2])

                elif len(ls) == 5:
                    
                    row = ls[1]
                    row2 = ls[3]
                    
                    row_data[row]['rhs'] = float(ls[2])
                    row_data[row2]['rhs'] = float(ls[4])

                else:
                    print('>>> unknown line length (rhs)')

            if reading_bounds == True:
                    
                col = ls[2]

                if ls[0] == 'UP':
                    col_data[col]['ub'] = float(ls[3])

                elif ls[0] == 'LO':
                    col_data[col]['lb'] = float(ls[3])

                elif ls[0] == 'UI':
                    col_data[col]['ub'] = float(ls[3])
                    col_data[col]['int'] = True

                elif ls[0] == 'LI':
                    col_data[col]['lb'] = float(ls[3])
                    col_data[col]['int'] = True

                elif ls[0] == 'BV':
                    col_data[col]['ub'] = float(1.0)
                    col_data[col]['int'] = True

                else:
                    print('>>> unknown line type (bounds)')

        self.col_data = col_data
        self.row_data = row_data
        
    def read_aux(self):
        
        file = "data/" + self.name + ".aux"
        data = open(file, 'r')
        lines_data = data.readlines()
        data.close()

        obj_follower = []
        col_follower = []
        row_follower = []
        
        reading_ncol = False
        reading_nrow = False
        reading_cols = False
        reading_rows = False

        for line in lines_data:
            ls = line.split()
            if len(ls) == 0:
                continue
            
            if ls[0] == '@NUMVARS':
                reading_ncol = True
                continue
                
            if ls[0] == '@NUMCONSTRS':
                reading_ncol = False
                reading_nrow = True
                continue
                
            if ls[0] == '@VARSBEGIN':
                reading_nrow = False
                reading_cols = True
                continue
                
            if ls[0] == '@VARSEND':
                reading_cols = False
                continue                
                
            if ls[0] == '@CONSTRSBEGIN':
                reading_rows = True
                continue
                
            if ls[0] == '@CONSTRSEND':
                reading_rows = False
                continue
                
            if reading_ncol == True:
                self.nFcol = int(ls[0])
            if reading_nrow == True:
                self.nFrow = int(ls[0])
                
            if reading_cols == True:
                col_follower.append(ls[0])
                obj_follower.append(float(ls[1]))
                
            if reading_rows == True:
                row_follower.append(ls[0]) 

        self.follower = {'col': col_follower, 'row': row_follower, 'obj': obj_follower}
        
    def format_model(self):
      
        #---determine model features
        self.nLcol = len(self.col_data) - self.nFcol
        self.nLrow = len(self.row_data) - self.nFrow - 1        
         
        #for row in self.row_data: ---cannot be used because dict may change size
        for row in list(self.row_data.keys()):
          
            if row == self.leaderRow: 
                continue
            
            #---make all constraints >= inequalities
            if self.row_data[row]['dir'] == 'L':
                self.row_data[row]['dir'] = 'G'
                self.row_data[row]['coef'] = [coef*(-1.0) for coef in self.row_data[row]['coef']]
                self.row_data[row]['rhs'] = self.row_data[row]['rhs']*(-1.0)
            
            elif self.row_data[row]['dir'] == 'E':
                self.row_data[row]['dir'] = 'G'
                
                rowbis = row + "_bis"            
                self.row_data[rowbis] = {'dir': 'G', 'col': self.row_data[row]['col'], 'coef': [], 'rhs': self.row_data[row]['rhs']*(-1.0)}
                self.row_data[rowbis]['coef'] = [coef*(-1.0) for coef in self.row_data[row]['coef']]                
          
        for col in self.col_data:
            
            #---make all variables continuous (follower only?)
            if self.col_data[col]['int'] == True:
                self.col_data[col]['int'] = False
                       
            #---add rows for bound constraints of follower variables
            if col in self.follower['col']:
                #print(col, self.col_data[col]['lb'], self.col_data[col]['ub'])
            
                if self.col_data[col]['ub'] != None: # < default_ub - 1e-4:
                    colub = col + "_ub"
                    self.row_data[colub] = {'dir': 'G', 'col': [col], 'coef': [-1.0], 'rhs': (-1.0)*self.col_data[col]['ub']}
                    self.follower['row'].append(colub)
                    
                if self.col_data[col]['lb'] != None: #> -default_ub + 1e-4:
                    collb = col + "_lb"
                    self.row_data[collb] = {'dir': 'G', 'col': [col], 'coef': [1.0], 'rhs': self.col_data[col]['lb']}
                    self.follower['row'].append(collb)               
 