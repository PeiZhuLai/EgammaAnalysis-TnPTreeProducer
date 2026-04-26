#!/bin/bash
# /eos/project/h/htozg-dy-privatemc/pelai/root_make_TnP_ntuple

# baseInputDir=/eos/home-p/pelai/HZa/root_make_TnP_ntuple/eTnP_ntuple/2024
baseInputDir2024=/eos/project/h/htozg-dy-privatemc/pelai/root_make_eTnP_ntuple/eTnP_ntuple/2024
baseInputDir2025=/eos/project/h/htozg-dy-privatemc/pelai/root_make_eTnP_ntuple/eTnP_ntuple/2025
baseOutputDir=/eos/project/h/htozg-dy-privatemc/pelai/root_merged_eTnP_ntuple

# DY_LO_2024
mkdir -p "$baseOutputDir/mc/DY_LO_2024"
mapfile -t dy_lo_files < <(find "$baseInputDir2024/mc/DY_LO_2024" -maxdepth 1 -name '*.root' | sort)
n_lo=${#dy_lo_files[@]}
half_lo=$(( n_lo / 10 ))
hadd -f "$baseOutputDir/mc/DY_LO_2024/DY_LO_2024.root" "${dy_lo_files[@]:0:half_lo}"

# DY_NLO_2024
mkdir -p "$baseOutputDir/mc/DY_NLO_2024"
mapfile -t dy_nlo_files < <(find "$baseInputDir2024/mc/DY_NLO_2024" -maxdepth 1 -name '*.root' | sort)
n_nlo=${#dy_nlo_files[@]}
half_nlo=$(( n_nlo / 10 ))
hadd -f "$baseOutputDir/mc/DY_NLO_2024/DY_NLO_2024.root" "${dy_nlo_files[@]:0:half_nlo}"

# # DY_LO_2024
# mkdir -p "$baseOutputDir/mc/DY_LO_2024"
# hadd -f $baseOutputDir/mc/DY_LO_2024/DY_LO_2024.root $baseInputDir2024/mc/DY_LO_2024/*.root

# # DY_NLO_2024
# mkdir -p "$baseOutputDir/mc/DY_NLO_2024"
# hadd -f $baseOutputDir/mc/DY_NLO_2024/DY_NLO_2024.root $baseInputDir2024/mc/DY_NLO_2024/*.root

# Data 2024
dataRuns=(EGamma0_Run2024B EGamma0_Run2024E EGamma0_Run2024H \
          EGamma1_Run2024C EGamma1_Run2024F EGamma1_Run2024I \
          EGamma0_Run2024C EGamma0_Run2024F EGamma0_Run2024I \
          EGamma1_Run2024D EGamma1_Run2024G \
          EGamma0_Run2024D EGamma0_Run2024G \
          EGamma1_Run2024B EGamma1_Run2024E EGamma1_Run2024H)

files=()

for run in "${dataRuns[@]}"; do
    files+=("$baseInputDir2024/data/$run/"*.root)
done

# mkdir -p "$baseOutputDir/data"
# hadd -f "$baseOutputDir/data/Data_2024.root" "${files[@]}"

# Data 2025
dataRuns=(EGamma0_Run2025B EGamma0_Run2025E EGamma0_Run2025H \

files=()

for run in "${dataRuns[@]}"; do
    files+=("$baseInputDir2025/data/$run/"*.root)
done

# mkdir -p "$baseOutputDir/data"
# hadd -f "$baseOutputDir/data/Data_2024.root" "${files[@]}"
