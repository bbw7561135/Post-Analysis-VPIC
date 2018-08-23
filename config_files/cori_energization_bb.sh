#!/bin/bash
#
#SBATCH -q premium
#SBATCH -N 64
#SBATCH -t 12:00:00
#SBATCH -C haswell
#SBATCH -o energization%j.out
#SBATCH -e energization%j.err
#SBATCH -J energization
##SBATCH -A m3122
#SBATCH -A m2407
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=phyxiaolee@gmail.com
#SBATCH -L SCRATCH,project

##DW jobdw capacity=204800GB access_mode=striped type=scratch pool=wlm_pool
#DW persistentdw name=reconnection
##DW stage_in source=/global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/particle destination=$DW_PERSISTENT_STRIPED_reconnection/particle type=directory
##DW stage_in source=/global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/data destination=$DW_PERSISTENT_STRIPED_reconnection/data type=directory
##DW stage_in source=/global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/Makefile destination=$DW_PERSISTENT_STRIPED_reconnection/Makefile type=file
##DW stage_in source=/global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/reconnection.cc destination=$DW_PERSISTENT_STRIPED_reconnection/reconnection.cc type=file
##DW stage_in source=/global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/info destination=$DW_PERSISTENT_STRIPED_reconnection/info type=file
##DW stage_in source=/global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/info.bin destination=$DW_PERSISTENT_STRIPED_reconnection/info.bin type=file

##### These are shell commands
date
# module swap craype-haswell craype-mic-knl
# module load lustre-default
module load dws
module load cray-hdf5-parallel
module list

#sbcast --compress --force --fanout=8 -t 240 ./untar.sh /tmp/untar.sh &  # Untar after stage in.
#sbcast --compress --force --fanout=8 -t 240 ./reconnection.Linux /tmp/reconnection.Linux &
#sbcast --compress --force --fanout=8 -t 240 ./tar.sh /tmp/tar.sh &
#wait

#cd $DW_JOB_STRIPED
##chmod +x ./ff-coll.Linux
##cd $DW_PERSISTENT_STRIPED_FFCOLL
#mkdir KNL64-PROP
#cd KNL64-PROP

# mkdir particle
# lfs setstripe -S 8388608 -c 72 particle
# mkdir spectrum
# lfs setstripe -S 8388608 -c 72 spectrum

#cd $DW_PERSISTENT_STRIPED_reconnection/input
#cd $SLURM_SUBMIT_DIR 

# export OMP_NUM_THREADS=4
# export OMP_PLACES=threads
# export OMP_PROC_BIND=spread

# time srun -n 2048 -N 64 -c 2 --cpu_bind=cores ./translate.exec -rp /global/cscratch1/sd/xiaocan/3D-Lx150-bg0.2-150ppc-2048KNL/ -fd -sd -nf 32
# time srun -n 2048 -N 64 -c 2 --cpu_bind=cores ./translate.exec -rp $DW_PERSISTENT_STRIPED_reconnection/input/ -fd -sd -nf 32
# wait
./energization_cori.sh

date
echo 'Done'
