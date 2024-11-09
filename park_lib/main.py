from .common import load_path_node, find_describe_path,\
    read_describe_txt, write_run_slurm_sh, load_path_describe_dict,str_to_list, save_path_describe_dict\
    ,write_run_slurm_sh_linux, read_incar_file, read_kpoints_file, poscar_file_check,set_magmom,set_potcar,get_absolute_directory_from_path
from argparse import ArgumentParser
import os, subprocess, copy
from ase.calculators.vasp import Vasp
from ase.io import read, write
from PIL import Image
import numpy as np
from scipy.spatial.transform import Rotation as R

library_dirpath = get_absolute_directory_from_path(__file__)

def vasp(args):
    working_dir = args.working_dir
    node = args.node
    cont = args.cont
    poscar = args.poscar
    potcar = args.potcar
    poscar_type = args.poscar_type
    magmom = args.magmom
    server = args.server

    # INCAR, KPOINTS check
    INCAR_path = os.path.join(working_dir,"INCAR")
    KPOINTS_path = os.path.join(working_dir,"KPOINTS")
    if not os.path.isfile(INCAR_path):
        raise Exception(f'INCAR path is not valid! \n [INCAR path] {INCAR_path}')
    if not os.path.isfile(KPOINTS_path):
        raise Exception(f'KPOINTS path is not valid! \n [KPOINTS path] {KPOINTS_path}')

    # POSCAR path check
    if poscar == None:
        for root, dirnames, filenames in os.walk(working_dir):
            for filename in filenames:
                if poscar_file_check(filename,poscar_type,cont):
                    if poscar_type != "POSCAR":
                        poscar_file_path = os.path.join(root,filename)
                    else:
                        if cont:
                            poscar_file_path = os.path.join(root,'CONTCAR')
                        else:
                            poscar_file_path = os.path.join(root,filename)

                    run_slurm_path,working_dir = write_run_slurm_sh(library_dirpath,node,poscar_file_path,potcar,magmom,cont,poscar_type,INCAR_path,KPOINTS_path,server)
                    _, _ = write_run_slurm_sh_linux(library_dirpath,node,poscar_file_path,potcar,magmom,cont,poscar_type,INCAR_path,KPOINTS_path,server)
                    subprocess.call(["sbatch",f"{run_slurm_path}"],shell=False)
                    print(f"{poscar_file_path} has been submitted")
    else:
        poscar_file_path = os.path.join(working_dir,poscar)
        run_slurm_path,working_dir = write_run_slurm_sh(library_dirpath,node,poscar_file_path,potcar,magmom,cont,poscar_type,INCAR_path,KPOINTS_path,server)
        _, _ = write_run_slurm_sh_linux(library_dirpath,node,poscar_file_path,potcar,magmom,cont,poscar_type,INCAR_path,KPOINTS_path,server)
        subprocess.call(["sbatch",f"{run_slurm_path}"],shell=False)
        print(f"{poscar_file_path} has been submitted")

def visual(args):
    input_filepath = args.input_filepath
    output_filepath = args.output_filepath
    repeat_atom = args.repeat_atom
    orientation = args.orientation
    cell_on = args.cell_on
    transmittances = args.transmittances
    heatmaps = args.heatmaps
    canvas_width = args.canvas_width
    
    structure = read(input_filepath)
    structure = structure.repeat(repeat_atom)
    if not cell_on:
        structure.cell = None

    povray_settings = {'canvas_width' : canvas_width}
    if not transmittances:
        transmittances = [0.0 for _ in range(len(structure))]
        povray_settings.update({'transmittances': transmittances})
    if heatmaps:
        mapped_colors = [
            (c, 0.0, 1.0 - c) for c in heatmaps  # (Red, Green, Blue)
        ]
        povray_settings.update({'colors': mapped_colors})


    lines = orientation.strip().split("\n")
    rotation = []
    for line in lines:
        row = list(map(float, line.split()))
        rotation.append(row)
    rotation = R.from_matrix(rotation)
    rotation = rotation.as_euler("xyz", degrees=True)
    rotation = f"{rotation[0]}x, {rotation[1]}y, {rotation[2]}z"

    renderer = write('./temp.pov', structure, rotation=rotation,povray_settings=povray_settings) 
    with open(f'./temp.ini', 'a') as file:
        file.write('Library_Path="/home/pn50212/povray-3.6/include"\n')
    povray_command = ['povray', '+L/home/pn50212/povray-3.6/include', "./temp.pov", 'temp.ini']
    subprocess.run(povray_command, check=True)
    temp_image_path = f'./temp.png'
    img = Image.open(temp_image_path)
    img.save(output_filepath)  # 이미지를 조정한 후에 저장

    os.remove("./temp.ini")
    os.remove("./temp.pov")
    os.remove("./temp.png")

def main():
    parser = ArgumentParser(description="Calculator commands")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    parser_vasp = subparsers.add_parser('vasp', help='for convinient vasp calculation')
    parser_visual = subparsers.add_parser('visual', help='for povray visualization')

    parser_vasp.add_argument("-d","--working_dir",type=str,default=os.getcwd(),help="working directory")
    parser_vasp.add_argument("-n","--node",required=True,help="running node, ['1', '2', '3', '4', 'test']")
    parser_vasp.add_argument("-c","--cont",default=False,action="store_true",help="if continue is specified, the computation will continue calculation")
    parser_vasp.add_argument("-pos","--poscar",type=str,default=None,help="POSCAR file path (default = None)")
    parser_vasp.add_argument("-pot","--potcar",type=str,default="recommended",help="POTCAR setup (default = 'recommended') : 'minimal', 'recommended', 'GW'")
    parser_vasp.add_argument("-t","--poscar_type",type=str,default="POSCAR",help="POSCAR file type setup (default = 'POSCAR') : 'POSCAR', 'xyz', 'cif' ...")
    parser_vasp.add_argument("-m","--magmom",type=str,default="recommended",help="Magnetic moment setting")
    parser_vasp.add_argument("-s","--server",type=str,default="cpu",help="Server, ['cpu' or 'gpu']")

    parser_visual.add_argument("-i","--input_filepath",type=str,required=True,help="input structure file path")
    parser_visual.add_argument("-o","--output_filepath",type=str,required=True,help="output image file path")
    parser_visual.add_argument("-r","--repeat_atom",type=int,nargs='+',default=[1,1,1],help="repeatation")
    parser_visual.add_argument("-ori","--orientation",type=str,default='+0.955480  +0.294974  -0.006949\n-0.042581  +0.161156  +0.986010\n+0.291967  -0.941817  +0.166542',help="camera orientation")
    parser_visual.add_argument("-c","--cell_on",action='store_true',help="visual cell")
    parser_visual.add_argument("-t","--transmittances",type=float,nargs='+',default=None,help="atom transmittances")
    parser_visual.add_argument("-H","--heatmaps",type=float,nargs='+',default=None,help="atom heatmaps")
    parser_visual.add_argument("-w","--canvas_width",type=int,default=960,help="pixel of width")

    args = parser.parse_args()

    if args.command == 'vasp':
        vasp(args=args)
    elif args.command == 'visual':
        visual(args=args)

if __name__ == "__main__":
    main()



