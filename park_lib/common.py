import os, pickle
import shutil

def write_run_slurm_sh(dir_path,describe,index,node,poscar_path,restart_false):
    working_dir = os.path.join(dir_path,f"{index}_{describe}_POSCAR")
    os.makedirs(working_dir,exist_ok=True)
    node_dict = {1:12,2:20,3:20,4:24,5:32}
    run_slurm_path = os.path.join(working_dir,f"{index}_{describe}_run_slurm.sh")
    with open(run_slurm_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --nodes=1\n")
        f.write(f"#SBATCH --ntasks-per-node={node_dict[node]:d}\n")
        f.write(f"#SBATCH --partition=g{node}\n")
        f.write("##\n")
        f.write(f"#SBATCH --job-name=\"{index:d}_{describe:s}\"\n")
        f.write("#SBATCH --time=05-00:00          # Runtime limit: Day-HH:MM\n")
        f.write("#SBATCH -o stdout.%N.%j.out         # STDOUT, %N : nodename, %j : JobID\n")
        f.write("#SBATCH -e STDERR.%N.%j.err         # STDERR, %N : nodename, %j : JobID\n")
        f.write("\n")
        f.write("## HPC ENVIRONMENT DON'T REMOVE THIS PART\n")
        f.write(". /etc/profile.d/TMI.sh\n")
        f.write("##\n")
        f.write("export VASP_PP_PATH=/home1/pn50212/POTCAR_dir/\n")
        f.write(f"export VASP_SCRIPT={working_dir}/run_vasp.py\n")
        f.write(f"echo \"import os\" > {working_dir}/run_vasp.py\n")
        f.write(
            f"echo \"exitcode = os.system('mpiexec.hydra -genv I_MPI_DEBUG 5 -np $SLURM_NTASKS  /TGM/Apps/VASP/VASP_BIN/6.3.2/vasp.6.3.2.beef.std.x')\" >> {working_dir}/run_vasp.py \n")
        f.write("\n")
        if restart_false == False:
            f.write(f"python ./run_poscar.py --poscar_path={poscar_path} --working_dir={working_dir} --restart_false\n")
        else:
            f.write(f"python ./run_poscar.py --poscar_path={poscar_path} --working_dir={working_dir}\n")
    return run_slurm_path, working_dir

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
        raise Exception("There is no describe you entered!")

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

            path_describe_dict[path] = describe

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

if __name__ == "__main__":
    save_path_describe_dict()
