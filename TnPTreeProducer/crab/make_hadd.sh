#!/bin/bash

set -euo pipefail

baseInputDir2024=/eos/project/h/htozg-dy-privatemc/pelai/root_make_eTnP_ntuple/eTnP_ntuple/2024
baseInputDir2025=/eos/project/h/htozg-dy-privatemc/pelai/root_make_eTnP_ntuple/eTnP_ntuple/2025
baseOutputDir=/eos/project/h/htozg-dy-privatemc/pelai/root_merged_eTnP_ntuple

hadd_sample() {
    local input_dir="$1"
    local output_file="$2"
    local take_divisor="${3:-}"
    local output_dir
    local files=()
    local n_files
    local n_take

    if [[ ! -d "$input_dir" ]]; then
        echo "WARNING: missing input directory: $input_dir" >&2
        return 0
    fi

    mapfile -t files < <(find "$input_dir" -maxdepth 1 -type f -name '*.root' | sort)
    if (( ${#files[@]} == 0 )); then
        echo "WARNING: no ROOT files found in $input_dir" >&2
        return 0
    fi

    if [[ -n "$take_divisor" ]]; then
        n_files=${#files[@]}
        n_take=$(( n_files / take_divisor ))
        if (( n_take == 0 )); then
            echo "WARNING: only $n_files ROOT files found in $input_dir; n/$take_divisor is 0" >&2
            return 0
        fi
        files=("${files[@]:0:n_take}")
    fi

    output_dir=$(dirname "$output_file")
    mkdir -p "$output_dir"

    echo "Merging ${#files[@]} files into $output_file"
    hadd -f "$output_file" "${files[@]}"
}

hadd_data() {
    local year="$1"
    local input_base="$2"
    shift 2

    local runs=("$@")
    local files=()
    local run
    local run_dir
    local run_files=()

    for run in "${runs[@]}"; do
        run_dir="$input_base/data/$run"
        if [[ ! -d "$run_dir" ]]; then
            echo "WARNING: missing input directory: $run_dir" >&2
            continue
        fi

        mapfile -t run_files < <(find "$run_dir" -maxdepth 1 -type f -name '*.root' | sort)
        if (( ${#run_files[@]} == 0 )); then
            echo "WARNING: no ROOT files found in $run_dir" >&2
            continue
        fi

        files+=("${run_files[@]}")
    done

    if (( ${#files[@]} == 0 )); then
        echo "WARNING: no ROOT files found for ${year} data" >&2
        return 0
    fi

    mkdir -p "$baseOutputDir/data"
    echo "Merging ${#files[@]} files into $baseOutputDir/data/Data_${year}.root"
    hadd -f "$baseOutputDir/data/Data_${year}.root" "${files[@]}"
}

# MC samples listed under 2024/mc in eTnP_ntuple_structure.txt.
# For DY samples, use the first n/10 files after sorting all ROOT files in each directory.
hadd_sample "$baseInputDir2024/mc/DY_LO_2024" "$baseOutputDir/mc/DY_LO_2024/DY_LO_2024.root" 10
hadd_sample "$baseInputDir2024/mc/DY_NLO_2024" "$baseOutputDir/mc/DY_NLO_2024/DY_NLO_2024.root" 10

# Data samples listed under 2024/data in eTnP_ntuple_structure.txt.
dataRuns2024=(
    EGamma0_Run2024B
    EGamma0_Run2024C
    EGamma0_Run2024D
    EGamma0_Run2024E
    EGamma0_Run2024F
    EGamma0_Run2024G
    EGamma0_Run2024H
    EGamma0_Run2024I
    EGamma1_Run2024B
    EGamma1_Run2024C
    EGamma1_Run2024D
    EGamma1_Run2024E
    EGamma1_Run2024F
    EGamma1_Run2024G
    EGamma1_Run2024H
    EGamma1_Run2024I
)
hadd_data 2024 "$baseInputDir2024" "${dataRuns2024[@]}"

# Data samples listed under 2025/data in eTnP_ntuple_structure.txt.
dataRuns2025=(
    EGamma0_Run2025C_v1
    EGamma0_Run2025C_v2
    EGamma0_Run2025D_v1
    EGamma0_Run2025E_v1
    EGamma0_Run2025F_v1
    EGamma0_Run2025F_v2
    EGamma0_Run2025G_v1
    EGamma1_Run2025C_v1
    EGamma1_Run2025C_v2
    EGamma1_Run2025D_v1
    EGamma1_Run2025E_v1
    EGamma1_Run2025F_v1
    EGamma1_Run2025F_v2
    EGamma1_Run2025G_v1
)
hadd_data 2025 "$baseInputDir2025" "${dataRuns2025[@]}"
