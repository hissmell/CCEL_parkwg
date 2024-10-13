from .common import load_path_node, find_describe_path,\
    read_describe_txt, write_run_slurm_sh, load_path_describe_dict,str_to_list, save_path_describe_dict\
    ,write_run_slurm_sh_linux, read_incar_file, read_kpoints_file, poscar_file_check,set_magmom,set_potcar
from argparse import ArgumentParser
import os, subprocess
from ase.calculators.vasp import Vasp
from ase.io import read


def vasp(args):
    working_dir = args.working_dir
    node = args.node
    cont = args.cont
    poscar = args.poscar
    potcar = args.potcar
    poscar_type = args.poscar_type
    magmom = args.magmom

    # POSCAR path check
    if poscar == None:
        for root, dirnames, filenames in os.walk(working_dir):
            for filename in filenames:
                if poscar_file_check(filename,poscar_type):
                    if poscar_type != "POSCAR":
                        poscar_file_path = os.path.join(root,filename)
                    else:
                        if cont:
                            poscar_file_path = os.path.join(root,'CONTCAR')
                        else:
                            poscar_file_path = os.path.join(root,'POSCAR')

                    """ run_slurm 작성 및 실행 """
                    run_dir = root
                    run_slurm_path,working_dir = write_run_slurm_sh(run_dir,node,poscar_file_path,potcar,magmom,cont,poscar_type)
                    _, _ = write_run_slurm_sh_linux(run_dir,node,poscar_file_path,potcar,magmom,cont,poscar_type)
                    subprocess.call(["sbatch",f"{run_slurm_path}"],shell=False)
    else:
        poscar_file_path = os.path.join(working_dir,poscar)
        """ run_slurm 작성 및 실행 """
        run_dir = working_dir
        run_slurm_path,working_dir = write_run_slurm_sh(run_dir,node,poscar_file_path,potcar,magmom,cont,poscar_type)
        _, _ = write_run_slurm_sh_linux(run_dir,node,poscar_file_path,potcar,magmom,cont,poscar_type)
        subprocess.call(["sbatch",f"{run_slurm_path}"],shell=False)


def main():
    parser = ArgumentParser(description="Calculator commands")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    parser_vasp = subparsers.add_parser('vasp', help='for convinient vasp calculation')

    parser_vasp.add_argument("-d","--working_dir",type=str,default=os.getcwd(),help="working directory")
    parser_vasp.add_argument("-n","--node",required=True,help="running node, ['1', '2', '3', '4', 'test']")
    parser_vasp.add_argument("-c","--cont",default=False,action="store_true",help="if continue is specified, the computation will continue calculation")
    parser_vasp.add_argument("-pos","--poscar",type=str,default=None,help="POSCAR file path (default = None)")
    parser_vasp.add_argument("-pot","--potcar",type=str,default="recommended",help="POTCAR setup (default = 'recommended') : 'minimal', 'recommended', 'GW'")
    parser_vasp.add_argument("-t","--poscar_type",type=str,default="POSCAR",help="POSCAR file type setup (default = 'POSCAR') : 'POSCAR', 'xyz', 'cif' ...")
    parser_vasp.add_argument("-m","--magmom",type=str,default="recommended",help="Magnetic moment setting")


    args = parser.parse_args()

    if args.command == 'vasp':
        vasp(args=args)


