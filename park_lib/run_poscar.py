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
magmom = {"Pt" : 2, "Fe" : 4, "Co" : 3, "Ni" : 2, "Cu" : 1, "Zn" : 0}

atoms = read(poscar_path)
host_atom_num = len(atoms[[atom.symbol == atoms.symbols[0] for atom in atoms]])
rest_atom_num = len(atoms) - host_atom_num

init_magmom_list = [magmom[atoms.symbols[0]]] * host_atom_num + [0.0] * rest_atom_num
atoms.set_initial_magnetic_moments(init_magmom_list)

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

_ = atoms.get_potential_energy()







