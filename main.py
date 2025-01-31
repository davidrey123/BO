from src import Instance
from src import Optim

name = "bmilplib_310_6"
name = "general30-20-10-20-20-4"
name = "eil33-2_0_100"
name = "xuLarge1000-9"
print(name)

ins = Instance.Instance(name)

print("leader cols",ins.nLcol)
print("leader rows",ins.nLrow)
print("follower cols",ins.nFcol)
print("follower rows",ins.nFrow)
print("total cols",len(ins.col_data))
print("total rows",len(ins.row_data))

optim = Optim.Optim(ins)

optim.create_MPCC()
optim.solve_MPCC(True)
