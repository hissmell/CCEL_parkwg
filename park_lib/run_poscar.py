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
    # ASE setting
    directory=working_dir,
    atoms=atoms,
    setups=setups,  # POTCAR setting

    # KPOINT
    kpts=(1, 1, 1),

    # accuracy, speed
    prec = "normal", # recommended value, (accurate for volume optimization, phonons, ...)
    algo = "f", # 5x Davidson, then DIIS

    # start options
    istart=0,
    icharg=2,
    idipol=3,

    # spin/magnetism
    ispin=2, # spin polarized calculation? (1 no, 2 yes)

    # electronic relaxation
    encut=400, # planewave cutoff (eV)
    ediff=2e-4, # convergence criterion for wave-functions
    gga='PE', # PBE GGA
    ismear=1, # -5: tetra+Bloechl; -4: tetra;...; -1 Fermi; 0 Gaussian (Insulators!) 1..N Methfessel-Paxton (metals)
    sigma=0.2, # smearing parameter -> check that TS is smaller than 1meV per atom; metals: 0.1; insulators: 0.05
    lreal='.FALSE.', # use g-space projectors
    ivdw=12, # vdW potential correction option

    # ionic relaxation
    isym=0, # 0: no symmetry; 1: symmetry; 2: memory conserving symmetry (4 PAW)
    nsw=800,
    ibrion=2, # -1: ions not moved; 0: MD; 1: quasi-Newton 2: CG; 3: quickmin; 5: Hessian;
    potim=0.5, # timestep/scaling for forces ... not used for CG
    isif=2, # all relax ions, additionally: 1: pressure; 2: stress;
    ediffg=-.03, # neg. value: force cutoff for nuclei; pos. value: free energy change

    # etc
    emin= -10,
    emax= 10,
    nedos= 1000,

    # U
    ldau=False, # switch off or on +U
    ldautype=2, # 1/2/4
    ldau_luj={'Mn': {'L': 2, 'U': 3.9, 'J': 0}, 'Ru': {'L': -1, 'U': 0, 'J': 0}, 'O': {'L': -1, 'U': 0, 'J': 0},
              'H': {'L': -1, 'U': 0, 'J': 0}}, # l,j,u value
    ldauprint=2,
    lmaxmix=4,

    # IO options
    lwave=False,
    lcharg=False,
    laechg=False,
    npar=4,
    lorbit=11, # 0 RWIGS line required DOSCAR and PROCAR file
)

# do calculation!
_ = atoms.get_potential_energy()

