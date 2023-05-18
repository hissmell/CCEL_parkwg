from common import load_path_node, find_describe_path,\
    read_describe_txt, write_run_slurm_sh, load_path_describe_dict,str_to_list, save_path_describe_dict
from argparse import ArgumentParser
import os, subprocess



parser = ArgumentParser()
parser.add_argument("-d","--describe_str_list",type=str_to_list,required=True,default=[])
parser.add_argument("-n","--node",type=int,required=True)
parser.add_argument("-r","--restart_false",default=True,action="store_false")
parser.add_argument("-i","--index",type=int,default=False)
args = parser.parse_args()

node = args.node
describe_str_list = args.describe_str_list
restart_false = args.restart_false
index = args.index

root_dir = os.getcwd()
save_path_describe_dict()
path_describe_dict = load_path_describe_dict()

for dir_path,dir_names,file_names in os.walk(root_dir):
    if "POSCAR" in dir_path.split("/")[-1]:
        continue
    for f in file_names:
        if "POSCAR" not in f:
            continue
        if not f[0].isdigit():
            continue
        if not index:
            if not (index != int(f[0])):
                continue

        poscar_path = os.path.join(dir_path, f)
        describe = path_describe_dict[poscar_path]
        if not all(d in describe for d in describe_str_list):
            continue

        index = int(f.split('_')[0])
        """ run_slurm 작성 및 실행 """
        run_slurm_path,working_dir = write_run_slurm_sh(dir_path,describe,index,node,poscar_path,restart_false)
        subprocess.call(["sbatch",f"{run_slurm_path}"],shell=False)

