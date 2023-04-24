from common import write_describe_txt, find_describe_path
from common import move_dir, set_path_node, save_path_node
from common import set_poscar_dir, save_path_describe_dict
from common import PathNode
import os

atoms = ["Pt","Fe","Co","Ni","Cu","Zn"] #
ads = ["MgOH2","CaOH2","CuOH2"] #

root_dir = os.getcwd()
write_describe_txt("R")

root_path_node = PathNode(describe="R",path=root_dir)
for ii, atom in enumerate(atoms):
    atom_dir,node_atom = set_poscar_dir(root_dir,ii,atom,root_path_node,atom)

    for jj, ad in enumerate(ads):
        ad_dir,node_ad = set_poscar_dir(atom_dir,jj,ad,node_atom,ad)

save_path_node(root_path_node)
save_path_describe_dict()


