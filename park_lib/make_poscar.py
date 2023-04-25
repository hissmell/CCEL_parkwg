from common import write_describe_txt, find_describe_path
from common import move_dir, set_path_node, save_path_node
from common import set_poscar_dir, save_path_describe_dict
from common import PathNode, check_dict
import os

atoms = ["Pt","Fe","Co","Ni","Cu","Zn"] # dictionary -> key = name, value = description
ads = ["MgOH2","CaOH2","CuOH2"] # dictionary -> key = name, value = description

atoms = check_dict(atoms) # list 변수를 넣으면 key = 원소, value = 원소인 dictionary로 자동 변환
ads = check_dict(ads)

root_dir = os.getcwd()
write_describe_txt("R")

root_path_node = PathNode(describe="R",path=root_dir)
for ii, (atom_name, atom_desc) in enumerate(atoms.items()):
    atom_dir,node_atom = set_poscar_dir(root_dir,ii,atom_name,root_path_node,atom_desc)

    for jj, (ad_name, ad_desc) in enumerate(ads.items()):
        ad_dir,node_ad = set_poscar_dir(atom_dir,jj,ad_name,node_atom,ad_desc)

save_path_node(root_path_node)
save_path_describe_dict()


