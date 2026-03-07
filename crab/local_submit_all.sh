#!/bin/bash

# Local submission script for 2026_01haozhong
# Generated on 2026-01-22 17:56:16

echo '=========================================='
echo 'Local job submission'
echo '=========================================='
echo ''
echo 'This script will run jobs locally using parallel execution'
echo 'Make sure you are in a CMSSW environment with proper setup'
echo ''
read -p 'Do you want to continue? (y/n): ' -n 1 -r
echo ''
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo 'Aborted.'
    exit 1
fi

echo '=========================================='
echo 'Local submission for EGamma_Run2022B'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022_EGamma_Run2022B/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma_Run2022C'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022_EGamma_Run2022C/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma_Run2022D'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022_EGamma_Run2022D/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma_Run2022E'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022_EGamma_Run2022E/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma_Run2022F'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022_EGamma_Run2022F/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma_Run2022G'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022_EGamma_Run2022G/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_LO_2022preEE'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022preEE_DY_LO_2022preEE/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_LO_2022postEE'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022postEE_DY_LO_2022postEE/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_NLO_2022preEE'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022preEE_DY_NLO_2022preEE/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_NLO_2022postEE'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2022postEE_DY_NLO_2022postEE/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma0_Run2023Cv1'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma0_Run2023Cv1/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma0_Run2023Cv2'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma0_Run2023Cv2/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma0_Run2023Cv3'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma0_Run2023Cv3/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma0_Run2023Cv4'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma0_Run2023Cv4/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma1_Run2023Cv1'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma1_Run2023Cv1/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma1_Run2023Cv2'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma1_Run2023Cv2/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma1_Run2023Cv3'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma1_Run2023Cv3/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma1_Run2023Cv4'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma1_Run2023Cv4/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma0_Run2023Dv1'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma0_Run2023Dv1/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma0_Run2023Dv2'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma0_Run2023Dv2/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma1_Run2023Dv1'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma1_Run2023Dv1/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for EGamma1_Run2023Dv2'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023_EGamma1_Run2023Dv2/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_LO_2023preBPIX'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023preBPIX_DY_LO_2023preBPIX/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_LO_2023postBPIX'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023postBPIX_DY_LO_2023postBPIX/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_NLO_2023preBPIX'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023preBPIX_DY_NLO_2023preBPIX/configs
./run_job_local.sh
echo ''
echo '=========================================='
echo 'Local submission for DY_NLO_2023postBPIX'
echo '=========================================='
cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_2026_01haozhong/2023postBPIX_DY_NLO_2023postBPIX/configs
./run_job_local.sh
echo ''
