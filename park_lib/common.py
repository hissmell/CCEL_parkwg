import os, pickle
import shutil
import re
import matplotlib.pyplot as plt
import numpy as np
import json
from treelib import Node, Tree
from collections import defaultdict

def get_filename_without_extension(file_path):
    file_name = os.path.basename(file_path)
    base_name, extension = os.path.splitext(file_name)
    return base_name if extension else file_name

def get_absolute_directory_from_path(file_path):
    absolute_path = os.path.abspath(file_path)
    directory = os.path.dirname(absolute_path)
    return directory

def write_run_slurm_sh(library_dirpath,node,poscar_file_path,potcar,magmom,cont,poscar_type,incar_path,kpoints_path,server):
    run_poscar_path = os.path.join(library_dirpath,'run_poscar.py')
    filename = get_filename_without_extension(poscar_file_path)
    poscar_dirpath = get_absolute_directory_from_path(poscar_file_path)
    if server == 'cpu':
        node_dict = {"g1":32,"g2":20,"g3":24,"g4":32,"test":20}
    elif server == 'gpu':
        node_dict = {"snu-g1":32}
    run_slurm_path = os.path.join(poscar_dirpath,f"run_slurm.sh")
    with open(run_slurm_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --nodes=1\n")
        f.write(f"#SBATCH --ntasks-per-node={node_dict[node]:d}\n")
        f.write(f"#SBATCH --partition={node}\n")
        f.write("##\n")
        f.write(f"#SBATCH --job-name=\"{filename}\"\n")
        if node != "test":
            f.write("#SBATCH --time=05-00:00          # Runtime limit: Day-HH:MM\n")
        elif node == "test":
            f.write("#SBATCH --time=00-01:00          # Runtime limit: Day-HH:MM\n")
        else:
            raise Exception("Possible node name : g1, g2, g3, g4 and 'test'")
        f.write(f"#SBATCH -o stdout_{filename}.%N.%j.out         # STDOUT, %N : nodename, %j : JobID\n")
        f.write(f"#SBATCH -e STDERR_{filename}.%N.%j.err         # STDERR, %N : nodename, %j : JobID\n")
        f.write("\n")
        f.write("## HPC ENVIRONMENT DON'T REMOVE THIS PART\n")
        f.write(". /etc/profile.d/TMI.sh\n")
        f.write("##\n")
        f.write("export VASP_PP_PATH=/home/pn50212/POTCAR_dir/\n")
        f.write(f"export VASP_SCRIPT={poscar_dirpath}/run_vasp.py\n")
        f.write(f"echo \"import os\" > {poscar_dirpath}/run_vasp.py\n")
        f.write(
            f"echo \"exitcode = os.system('mpiexec.hydra -genv I_MPI_DEBUG 5 -np $SLURM_NTASKS  /TGM/Apps/VASP/VASP_BIN/6.3.2/vasp.6.3.2.beef.std.x')\" >> {poscar_dirpath}/run_vasp.py \n")
        f.write("\n")
        if cont:
            f.write(f"python {run_poscar_path} --working_dir {poscar_dirpath}  --poscar={poscar_file_path} --poscar_type {poscar_type} --potcar={potcar} --magmom {magmom} --incar {incar_path} --kpoints {kpoints_path} --cont\n")
        else:
            f.write(f"python {run_poscar_path} --working_dir {poscar_dirpath}  --poscar={poscar_file_path} --poscar_type {poscar_type} --potcar={potcar} --magmom {magmom} --incar {incar_path} --kpoints {kpoints_path}\n")
    return run_slurm_path, poscar_dirpath

def write_run_slurm_sh_linux(library_dirpath,node,poscar_file_path,potcar,magmom,cont,poscar_type,incar_path,kpoints_path,server):
    filename = get_filename_without_extension(poscar_file_path)
    poscar_dirpath = get_absolute_directory_from_path(poscar_file_path)
    if server == 'cpu':
        node_dict = {"g1":32,"g2":20,"g3":24,"g4":32,"test":20}
    elif server == 'gpu':
        node_dict = {"snu-g1":32}
    run_slurm_path = os.path.join(poscar_dirpath,f"run_slurm_linux.sh")
    with open(run_slurm_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --nodes=1\n")
        f.write(f"#SBATCH --ntasks-per-node={node_dict[node]:d}\n")
        f.write(f"#SBATCH --partition={node}\n")
        f.write("##\n")
        f.write(f"#SBATCH --job-name=\"{filename}\"\n")
        if node != "test":
            f.write("#SBATCH --time=05-00:00          # Runtime limit: Day-HH:MM\n")
        elif node == "test":
            f.write("#SBATCH --time=00-01:00          # Runtime limit: Day-HH:MM\n")
        else:
            raise Exception("Possible node name : g1, g2, g3, g4 and 'test'")
        f.write(f"#SBATCH -o stdout_{filename}.%N.%j.out         # STDOUT, %N : nodename, %j : JobID\n")
        f.write(f"#SBATCH -e STDERR_{filename}.%N.%j.err         # STDERR, %N : nodename, %j : JobID\n")
        f.write("\n")
        f.write("## HPC ENVIRONMENT DON'T REMOVE THIS PART\n")
        f.write(". /etc/profile.d/TMI.sh\n")
        f.write("##\n")
        f.write(
            f"mpiexec.hydra -genv I_MPI_DEBUG 5 -np $SLURM_NTASKS /TGM/Apps/VASP/VASP_BIN/6.3.2/vasp.6.3.2.beef.std.x\n")
        f.write("\n")
    return run_slurm_path, poscar_dirpath

def check_dict(x=[]):
    if (type(x) != list) and (type(x) != dict):
        raise Exception("List or Dictionaty type must be put")

    if type(x) == list:
        d = dict()
        for l in x:
            d[l] = l
    else:
        d = x

    return d
def write_describe_txt(describe=""):
    with open(os.path.join(os.getcwd(),"describe.txt"),mode="w") as f:
        f.write(describe)
    return

def read_describe_txt(dir_path):
    with open(os.path.join(dir_path,"describe.txt"),mode='r') as f:
        d = f.readline()
        d.replace("\n","")
    return d

def find_describe_path(root_path_node,describe='R'):
    search_list = [root_path_node]
    while len(search_list) >= 1:
        node = search_list.pop(0)
        if node.describe == describe:
            flag = False
            break
        search_list.extend(node.child)
        flag = True

    if flag:
        raise Exception("There is no describe.txt you entered!")

    return_path = node.path
    return_describe = node.describe
    while node.parent != None and node.parent.describe != "R":
        return_describe = node.parent.describe + "_" + return_describe
        node = node.parent
    return return_describe, return_path

def move_dir(dir_path):
    os.makedirs(dir_path,exist_ok=True)
    os.chdir(dir_path)
    return

def set_path_node(parent_node=None,describe="R",path=None):
    node_atom = PathNode(describe=describe, path=path)
    parent_node.add_child(node_atom)
    return node_atom

def save_path_node(path_node):
    with open(os.path.join(path_node.path,"root_path_node.pickle"),mode="wb") as f:
        pickle.dump(path_node,f)

def load_path_node(path=os.path.join(os.getcwd(),"root_path_node.pickle")):
    with open(path,mode='rb') as f:
        path_node = pickle.load(f)
    return path_node

def load_path_describe_dict(path=os.path.join(os.getcwd(),"path_describe_dict.pickle")):
    with open(path,mode="rb") as f:
        path_describe_dict = pickle.load(f)
    return path_describe_dict

def set_poscar_dir(parent_dir_path,index,dir_name,parent_node,describe):
    new_dir = os.path.join(parent_dir_path,f"{index}_"+dir_name)
    move_dir(new_dir)
    write_describe_txt(dir_name)
    node_new = set_path_node(parent_node,describe=describe,path=new_dir)
    return new_dir, node_new

def save_path_describe_dict(str_dir = os.getcwd()):
    path_describe_dict = dict()
    for dir_path, dir_names, file_names in os.walk(str_dir):
        for f in file_names:
            current_dir = dir_path
            if "POSCAR" not in f:
                continue
            if not f[0].isdigit():
                continue
            if "." in f:
                continue

            index = int(f.split("_")[0])
            path = os.path.join(current_dir,f)
            d = read_describe_txt(current_dir)
            describe = d
            parent_dir = "/".join(current_dir.split("/")[:-1])
            while os.path.isfile(os.path.join(parent_dir,"describe.txt")) and (read_describe_txt(parent_dir) != "R"):
                d = read_describe_txt(parent_dir)
                describe = d + "_" + describe
                current_dir = parent_dir
                if len(current_dir) < len(str_dir):
                    raise Exception("Searching process goes over the root directory!")
                parent_dir = "/".join(current_dir.split("\\")[:-1])

            path_describe_dict[path] = "R_" + describe

    with open(os.path.join(str_dir,"path_describe_dict.pickle"),"wb") as g:
        pickle.dump(path_describe_dict,g)
    return

def str_to_list(s):
    return s.split()

def check_restart(restart_flag,working_dir):
    if restart_flag:
        if os.path.isfile(os.path.join(working_dir,"CONTCAR")):
            return True
        else:
            raise Exception("There's no file to continue (CONTCAR file)")
    return False


class PathNode:
    def __init__(self,describe='R',path=None):
        self.describe = describe
        self.parent = None
        self.child = []
        self.path = path

    def add_child(self,node=None):
        self.child.append(node)
        node.parent = self
        return



def copy_main():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    destination = os.path.join(os.getcwd(), "main.py")

    if os.path.exists(source):
        shutil.copy(source, destination)
        print(f"Successfully copied {source} to {destination}")
    else:
        print(f"{source} not found")

def copy_make_poscar():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_poscar.py")
    destination = os.path.join(os.getcwd(), "make_poscar.py")

    if os.path.exists(source):
        shutil.copy(source, destination)
        print(f"Successfully copied {source} to {destination}")
    else:
        print(f"{source} not found")

def copy_run_poscar():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_poscar.py")
    destination = os.path.join(os.getcwd(), "run_poscar.py")

    if os.path.exists(source):
        shutil.copy(source, destination)
        print(f"Successfully copied {source} to {destination}")
    else:
        print(f"{source} not found")

def copy_common():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")
    destination = os.path.join(os.getcwd(), "common.py")

    if os.path.exists(source):
        shutil.copy(source, destination)
        print(f"Successfully copied {source} to {destination}")
    else:
        print(f"{source} not found")
def start():
    copy_main()
    copy_make_poscar()
    copy_run_poscar()
    copy_common()
    return

def get_relative_energy():
    data = {}
    for dir_path, dir_name, file_name in os.walk(os.getcwd()):
        OSZICAR_path = os.path.join(dir_path,"OSZICAR")
        if not os.path.isfile(OSZICAR_path):
            continue

        E0_value = np.inf

        with open(OSZICAR_path, 'r') as file:
            for line in file:
                # 각 줄에서 "DAV" 문자가 없는지 확인합니다.
                if 'DAV' not in line:
                    # E0 값을 찾습니다.
                    match = re.search(r"E0=\s+[-+]?\d*\.\d+([eE][-+]?\d+)?", line)
                    if match:
                        E0_value = float(match.group(0)[3:].strip()) if E0_value > float(match.group(0)[3:].strip()) else E0_value

        data[dir_path.split("/")[-1]] = E0_value

    # 가장 작은 value를 가진 key를 찾기
    min_key = min(data, key=data.get)

    output = {"minimum" : data[min_key]}
    for k in data.keys():
        output[k + "_rel"] = data[k] - data[min_key]
        output[k + "_abs"] = data[k]

    with open(os.path.join(os.getcwd(),"rel_abs_energies.json"),"w") as f:
        json.dump(output,f)
    return

def json2tree(tree, json_obj, parent_node=None):
    for k, v in json_obj.items():
        child_node = tree.create_node(tag=k, parent=parent_node)
        if isinstance(v, dict):
            json2tree(v, child_node.identifier)
        else:
            tree.create_node(tag=f"{k}: {v}", parent=child_node.identifier)

def print_relaxed_energy():
    get_relative_energy()
    # Load JSON data into a Python dictionary
    with open("rel_abs_energies.json","r") as f:
        json_data = json.load(f)

    # Initialize a new tree
    tree = Tree()

    # Create root node
    root = tree.create_node("Root")

    # Convert JSON object to tree
    json2tree(tree,json_data, root.identifier)

    # Print the tree
    tree.show()



def plot_energy():
    for dir_path, dir_name, file_name in os.walk(os.getcwd()):
        OSZICAR_path = os.path.join(dir_path,"OSZICAR")
        if not os.path.isfile(OSZICAR_path):
            continue

        E0_values = []

        with open(OSZICAR_path, 'r') as file:
            for line in file:
                # 각 줄에서 "DAV" 문자가 없는지 확인합니다.
                if 'DAV' not in line:
                    # E0 값을 찾습니다.
                    match = re.search(r"E0=\s+[-+]?\d*\.\d+([eE][-+]?\d+)?", line)
                    if match:
                        # E0 값의 시작과 끝을 찾아서 리스트에 추가합니다.
                        E0_values.append(float(match.group(0)[3:].strip()))

        # x 축 값 설정 (1부터 E0_values의 길이까지)
        x = np.arange(1, len(E0_values) + 1)

        plt.figure(figsize=(10, 6))
        plt.plot(x, E0_values, marker='o')
        plt.title(dir_path.split("/")[-1] + ' | E0 Values (absolute)')
        plt.xlabel('Iteration')
        plt.ylabel('E0 Value')

        # png 파일로 저장
        plt.savefig(os.path.join(dir_path,dir_path.split("/")[-1]+'_E0_values_abs.png'))
        plt.close()

        plt.figure(figsize=(10, 6))
        plt.plot(x, [e - min(E0_values) for e in E0_values], marker='o')
        plt.title(dir_path.split("/")[-1] + ' | E0 Values (relative)')
        plt.xlabel('Iteration')
        plt.ylabel('E0 Value')

        plt.savefig(os.path.join(dir_path,dir_path.split("/")[-1]+'_E0_values_rel.png'))
        plt.close()
    return

def plot_energies():
    root_dir = os.getcwd()
    for dir_path, dir_name, file_name in os.walk(root_dir):
        if not os.path.isfile(os.path.join(dir_path,"OSZICAR")):
            continue
        os.chdir(dir_path)
        plot_energy()
    return


def read_incar_file(file_path):
    incar_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            key = key.lower()
            value = value.strip()
            if value.upper() == '.TRUE.':
                value = True
            elif value.upper() == '.FALSE.':
                value = False
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass 
            incar_dict[key] = value
    return incar_dict

def read_kpoints_file(file_path):
    kpoints_dict = {}

    with open(file_path, 'r') as file:
        lines = file.readlines()

        # 3번째 줄에서 'Monkhorst-Pack' 또는 'Gamma' 확인
        if 'Monkhorst-Pack' in lines[2]:
            kpoints_dict['gamma'] = False
        elif 'Gamma' in lines[2]:
            kpoints_dict['gamma'] = True

        # 4번째 줄에서 kpts 값을 추출
        kpoints_dict['kpts'] = tuple(map(int, lines[3].strip().split()))

    return kpoints_dict

def poscar_file_check(filename,target_exp,is_continue):
    if (filename.endswith('CONTCAR')) and (is_continue):
        return True

    if target_exp != 'POSCAR':
        if filename.endswith(target_exp):
            return True
        return False
    else:
        if (filename.endswith('POSCAR')) and (not is_continue):
            return True
        elif (filename.endswith('CONTCAR')) and (is_continue):
            return True
        else:
            return False
        
def set_magmom(magmom):
    if magmom == 'recommended':
        magmom_dict = {'Sc':'1','Ti':'2','V':'3','Cr':'6'
            ,'Mn':'5','Fe':'4','Co':'3','Ni':'2'
            ,'Cu':'1','Zn':'0','Y':'1','Zr':'2'
            ,'Nb':'5','Mo':'6','Tc':'5','Ru':'4'
            ,'Rh':'3','Pd':'0','Ag':'1','Cd':'0'
            ,'La':'1','Hf':'2','Ta':'3','W':'4'
            ,'Re':'5','Os':'4','Ir':'3','Pt':'2'
            ,'Au':'1'}
    elif magmom == "zeros":
        magmom_dict = defaultdict(int)
    elif magmom == "ones":
        magmom_dict = defaultdict(lambda: 1)
    elif magmom.endswith('json'):
        with open(magmom,'r') as f:
            magmom_dict = json.load(f)
    else:
        raise Exception(f"Supported magmom ['recommended' (default), 'zeros', 'ones', 'json_file_path'] // Entered : {magmom}")
    return magmom_dict

def set_potcar(potcar):
    potcar_dict = {"base" : 'recommended', "W" : "_sv"}
    if potcar.endswith('json'):
        with open(potcar,'r') as f:
            new_potcar_dict = json.load(f)
        potcar_dict.update(new_potcar_dict)
    return potcar_dict

if __name__ == "__main__":
    save_path_describe_dict()
