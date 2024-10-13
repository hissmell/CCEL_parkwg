from common import load_path_node, find_describe_path,\
    read_describe_txt, write_run_slurm_sh, load_path_describe_dict,str_to_list, save_path_describe_dict\
    ,write_run_slurm_sh_linux, read_incar_file, read_kpoints_file, poscar_file_check,set_magmom,set_potcar
from argparse import ArgumentParser
from ase.calculators.vasp import Vasp
from ase.io import read
import os, subprocess

parser = ArgumentParser()
parser.add_argument("-d","--working_dir",type=str,default=os.getcwd(),help="working directory")
parser.add_argument("-n","--node",required=True,help="running node, ['1', '2', '3', '4', 'test']")
parser.add_argument("-c","--cont",default=False,action="store_true",help="if continue is specified, the computation will continue calculation")
parser.add_argument("-pos","--poscar",type=str,default=None,help="POSCAR file path (default = None)")
parser.add_argument("-pot","--potcar",type=str,default="recommended",help="POTCAR setup (default = 'recommended') : 'minimal', 'recommended', 'GW'")
parser.add_argument("-t","--poscar_type",type=str,default="POSCAR",help="POSCAR file type setup (default = 'POSCAR') : 'POSCAR', 'xyz', 'cif' ...")
parser.add_argument("-m","--magmom",type=str,defsault="recommended",help="Magnetic moment setting")

args = parser.parse_args()

working_dir = args.working_dir
node = args.node
cont = args.cont
poscar_path = args.poscar
potcar = args.potcar
poscar_type = args.poscar_type
magmom = args.magmom



# INCAR, KPOINTS check
INCAR_path = os.path.join(working_dir,"INCAR")
KPOINTS_path = os.path.join(working_dir,"KPOINTS")
if not os.path.isfile(INCAR_path):
    raise Exception(f'INCAR path is not valid! \n [INCAR path] {INCAR_path}')
if not os.path.isfile(KPOINTS_path):
    raise Exception(f'KPOINTS path is not valid! \n [KPOINTS path] {KPOINTS_path}')

incar_dict = read_incar_file(INCAR_path)
kpoints_dict = read_kpoints_file(KPOINTS_path)

# magmom check
magmom_dict = set_magmom(magmom)

# potcar check
potcar_dict = set_potcar(potcar)

''' write calculation setting! '''
atoms = read(poscar_path)

# set initial magmom

atoms_symbol_list = [atom.symbol for atom in atoms]
init_magmom_list = [0.0] * len(atoms)
for atom_idx in range(len(atoms)):
    try:
        m = float(magmom_dict[atoms_symbol_list[atom_idx]])
    except:
        m = 0.0
    init_magmom_list[atom_idx] = m

atoms.set_initial_magnetic_moments(init_magmom_list)

# set detailed potcar setting if you want
vasp_input_dict = {'directory' : working_dir,
                'atoms' : atoms,
                'setups' : potcar_dict}
vasp_input_dict.update(incar_dict)
vasp_input_dict.update(kpoints_dict)

# Do calc!
calc = Vasp(**vasp_input_dict)
_ = atoms.get_potential_energy()
