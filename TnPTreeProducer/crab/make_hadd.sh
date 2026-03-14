#!/bin/bash
# /eos/project/h/htozg-dy-privatemc/pelai/root_make_TnP_ntuple

baseInputDir=/eos/home-p/pelai/HZa/root_make_TnP_ntuple/eTnP_ntuple/2024
baseOutputDir=/eos/project/h/htozg-dy-privatemc/pelai/root_make_TnP_ntuple


# DY_LO_2024
mkdir -p "$baseOutputDir/mc/DY_LO_2024"
hadd -f $baseOutputDir/mc/DY_LO_2024/DY_LO_2024.root $baseInputDir/mc/DY_LO_2024/*.root

# DY_NLO_2024
mkdir -p "$baseOutputDir/mc/DY_NLO_2024"
hadd -f $baseOutputDir/mc/DY_NLO_2024/DY_NLO_2024.root $baseInputDir/mc/DY_NLO_2024/*.root

# Data 2024
dataRuns=(EGamma0_Run2024B EGamma0_Run2024E EGamma0_Run2024H \
          EGamma1_Run2024C EGamma1_Run2024F EGamma1_Run2024I \
          EGamma0_Run2024C EGamma0_Run2024F EGamma0_Run2024I \
          EGamma1_Run2024D EGamma1_Run2024G \
          EGamma0_Run2024D EGamma0_Run2024G \
          EGamma1_Run2024B EGamma1_Run2024E EGamma1_Run2024H)

files=()

for run in "${dataRuns[@]}"; do
    files+=("$baseInputDir/data/$run/"*.root)
done

mkdir -p "$baseOutputDir/data"
hadd -f "$baseOutputDir/data/Data_2024.root" "${files[@]}"