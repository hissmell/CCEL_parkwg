from common import load_path_node, find_describe_path,\
    read_describe_txt, write_run_slurm_sh, move_dir, check_restart
from argparse import ArgumentParser
from ase.calculators.vasp import Vasp
from ase.io import read
import os, subprocess

parser = ArgumentParser()
parser.add_argument("-p","--poscar_path",type=str,required=True)
parser.add_argument("-w","--working_dir",type=str,required=True)
parser.add_argument("-r","--restart_false",default=True,action="store_false")
parser.add_argument("-pp","--potcar",type=str,required=True)
args = parser.parse_args()

poscar_path = args.poscar_path
working_dir = args.working_dir
potcar = args.potcar
move_dir(working_dir)

RESTART = check_restart(args.restart_false,working_dir=working_dir)

''' write calculation setting! '''
atoms = read(poscar_path)

# set initial magmom
magmom = {'Sc':'1','Ti':'2','V':'3','Cr':'6'
        ,'Mn':'5','Fe':'4','Co':'3','Ni':'2'
        ,'Cu':'1','Zn':'0','Y':'1','Zr':'2'
        ,'Nb':'5','Mo':'6','Tc':'5','Ru':'4'
        ,'Rh':'3','Pd':'0','Ag':'1','Cd':'0'
        ,'La':'1','Hf':'2','Ta':'3','W':'4'
        ,'Re':'5','Os':'4','Ir':'3','Pt':'2'
        ,'Au':'1'}

atoms_symbol_list = [atom.symbol for atom in atoms]
init_magmom_list = [0.0] * len(atoms)
for atom_idx in range(len(atoms)):
    try:
        m = float(magmom[atoms_symbol_list[atom_idx]])
    except:
        m = 0.0
    init_magmom_list[atom_idx] = m

atoms.set_initial_magnetic_moments(init_magmom_list)

# set detailed potcar setting if you want
setups = {"base" : potcar, "W" : "_sv"} # {"Atom symbol" : "suffix" | "Atom integer index" : "Atom symbol + suffix"}

# set incar setting
calc = Vasp(
        directory=working_dir,
        kpts=(3, 3, 1),
        istart=0,
        icharg=2,
        ispin=2,
        idipol=3,
        encut=400,
        ediff=1E-04,
        xc='rpbe',
        lreal='Auto',
        nsw=600,
        ibrion=2,
        isif=2,
        ediffg=-.03,
        npar=4,
        lwave=".FALSE.",
        lcharg=".FALSE.",
        setups=potcar,
        atoms=atoms,
        restart=RESTART
    )

# do calculation!
_ = atoms.get_potential_energy()

