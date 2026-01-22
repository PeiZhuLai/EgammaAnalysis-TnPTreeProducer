#!/bin/env python
import os
import sys
import json
import subprocess
from datetime import datetime

#
# Example script to submit TnPTreeProducer to HTCondor
#
submitVersion = "2026_01haozhong" # add some date here
doL1matching  = False

defaultArgs   = ['doEleID=False','doPhoID=False','doTrigger=True']
path = "/eos/user/h/haozhong/diele_HLT_sf/Ntuples/"

mainOutputDir = '%s%s' % (path, submitVersion)

# Logging the current version of TnPTreeProducer here
os.system('mkdir -p %s' % mainOutputDir)
os.system('(git log -n 1;git diff) &> %s/git.log' % mainOutputDir)

#
# HTCondor job template
#
condor_template = '''universe = vanilla
executable = $(executable)
arguments = $(arguments)
output = $(logdir)/$(jobname).out
error = $(logdir)/$(jobname).err
log = $(logdir)/$(jobname).log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = $(inputfiles)
transfer_output_files = $(outputfiles)
+JobFlavour = "workday"
+AccountingGroup = "group_u_CMST3.all"
request_cpus = 1
request_memory = 2000
request_disk = 2000
queue
'''

#
# Local job runner script
#
local_runner_script = '''#!/bin/bash

# Local job runner for TnPTreeProducer
# Usage: ./run_job_local.sh [start_line] [end_line]


cd /eos/home-h/haozhong/diele_HLT_sf/CMSSW_14_0_19
eval `scramv1 runtime -sh`
cd -
JOB_LIST_FILE="job_list.txt"
OUTPUT_SUFFIX="_local"



# Default: process all lines
START_LINE=${1:-1}
END_LINE=${2:-$(wc -l < "$JOB_LIST_FILE")}

echo "=========================================="
echo "Local job runner for TnPTreeProducer"
echo "Job list file: $JOB_LIST_FILE"
echo "Processing lines: $START_LINE to $END_LINE"
echo "Output suffix: $OUTPUT_SUFFIX"
echo "=========================================="

# Check if job list file exists
if [ ! -f "$JOB_LIST_FILE" ]; then
    echo "Error: Job list file $JOB_LIST_FILE not found!"
    exit 1
fi

# Get number of lines
TOTAL_LINES=$(wc -l < "$JOB_LIST_FILE")
echo "Total lines in job list: $TOTAL_LINES"

# Validate line range
if [ $START_LINE -lt 1 ]; then
    START_LINE=1
fi
if [ $END_LINE -gt $TOTAL_LINES ]; then
    END_LINE=$TOTAL_LINES
fi

# Counter for jobs
JOB_COUNT=0
COMPLETED_JOBS=0
FAILED_JOBS=0

# Function to run a single job
run_single_job() {
    local line_number=$1
    local line_content=$2
    
    # Parse the line (format: outputfile,inputfile1,inputfile2,...)
    IFS=',' read -r -a parts <<< "$line_content"
    
    if [ ${#parts[@]} -lt 2 ]; then
        echo "Warning: Line $line_number has invalid format: $line_content"
        return 1
    fi
    
    OUTPUT_FILE="${parts[0]}"
    # Add suffix before .root extension
    OUTPUT_FILE_LOCAL="${OUTPUT_FILE%.root}${OUTPUT_SUFFIX}.root"
    
    # Collect input files
    INPUT_FILES="${parts[1]}"
    for ((i=2; i<${#parts[@]}; i++)); do
        INPUT_FILES="$INPUT_FILES,${parts[$i]}"
    done
    
    echo "--------------------------------------------------"
    echo "Job $line_number:"
    echo "  Input files: $INPUT_FILES"
    echo "  Output file: $OUTPUT_FILE_LOCAL"
    
    # Run the cmsRun command
    echo "  Starting at: $(date)"
    START_TIME=$(date +%s)
    
    # Actual cmsRun command
    cmsRun {cmssw_base}/src/EgammaAnalysis/TnPTreeProducer/python/TnPTreeProducer_cfg.py \
        {args_str} \
        inputFiles=$INPUT_FILES \
        outputFile=$OUTPUT_FILE_LOCAL
    
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "  Completed successfully in ${DURATION}s"
        return 0
    else
        echo "  Failed with exit code $EXIT_CODE after ${DURATION}s"
        return 1
    fi
}

# Process jobs
echo "Starting job processing..."
echo ""

for ((LINE_NUM=START_LINE; LINE_NUM<=END_LINE; LINE_NUM++)); do
    # Read the line
    LINE_CONTENT=$(sed -n "${LINE_NUM}p" "$JOB_LIST_FILE")
    
    if [ -z "$LINE_CONTENT" ]; then
        echo "Warning: Line $LINE_NUM is empty, skipping..."
        continue
    fi
    
    # Run job in background
    echo "Submitting job from line $LINE_NUM..."
    run_single_job $LINE_NUM "$LINE_CONTENT" &
    
    JOB_COUNT=$((JOB_COUNT + 1))
    
    # Limit number of concurrent jobs (adjust as needed)
    MAX_CONCURRENT_JOBS=35
    RUNNING_JOBS=$(jobs -rp | wc -l)
    
    # Wait if we have too many jobs running
    while [ $RUNNING_JOBS -ge $MAX_CONCURRENT_JOBS ]; do
        sleep 1
        RUNNING_JOBS=$(jobs -rp | wc -l)
    done
done

# Wait for all background jobs to complete
echo ""
echo "Waiting for all jobs to complete..."
wait

# Count completed and failed jobs
for job in $(jobs -p); do
    if wait $job; then
        COMPLETED_JOBS=$((COMPLETED_JOBS + 1))
    else
        FAILED_JOBS=$((FAILED_JOBS + 1))
    fi
done

echo ""
echo "=========================================="
echo "Job processing complete!"
echo "Total jobs submitted: $JOB_COUNT"
echo "Successfully completed: $COMPLETED_JOBS"
echo "Failed: $FAILED_JOBS"
echo "=========================================="

if [ $FAILED_JOBS -gt 0 ]; then
    exit 1
else
    exit 0
fi
'''

#
# CMS specific paths
#
cmssw_base = os.environ['CMSSW_BASE']
cmssw_release = os.environ['CMSSW_VERSION']
arch = os.environ['SCRAM_ARCH']

#
# Certified lumis for the different eras
#
def getLumiMask(era):
  if era == '2016':   
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
  elif era == '2017':   
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt'
  elif era == '2018':   
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
  elif era == 'UL2016preVFP': 
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt'
  elif era == 'UL2016postVFP': 
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt'
  elif era == 'UL2017': 
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
  elif era == 'UL2018': 
    return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
  elif era == '2022': 
    return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json'
  elif era == '2023': 
    return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'
  elif era == '2024': 
    return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json'
  else:
    return None

#
# Get dasgoclient output for dataset files
#
def get_dataset_files(dataset):
    """Get list of files for a dataset using dasgoclient"""
    cmd = f'dasgoclient --query="file dataset={dataset}" --limit=0'
    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        files = [f.strip() for f in result.split('\n') if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        print(f"Error getting files for dataset {dataset}: {e}")
        return []

def get_dataset_nevents(dataset):
    """Get number of events in dataset using dasgoclient"""
    cmd = f'dasgoclient --query="dataset={dataset} | sum(dataset.numevents)"'
    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        return int(float(result.strip()))
    except:
        return 0

#
# Submit function for HTCondor
#
def submit_htcondor(requestName, sample, era, extraParam=[]):
    """Submit jobs to HTCondor"""
    isMC = 'SIM' in sample or 'mc' in sample.lower()
    dMC = "data"
    if isMC: 
        dMC = "mc"
    
    # Create directories
    job_dir = f"/afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_{submitVersion}/{era}_{requestName}"
    log_dir = f"{job_dir}/logs"
    config_dir = f"{job_dir}/configs"
    output_dir = f"{mainOutputDir}/{era}/{dMC}/{requestName}"
    
    os.system(f'mkdir -p {log_dir}')
    os.system(f'mkdir -p {config_dir}')
    os.system(f'mkdir -p {output_dir}')
    
    # Get dataset files
    files = get_dataset_files(sample)
    if not files:
        print(f"Warning: No files found for dataset {sample}")
        return
    
    # Prepare arguments
    args_list = defaultArgs.copy()
    args_list.append(f'isMC={isMC}')
    args_list.append(f'era={era}')
    args_list.extend(extraParam)
    
    # Create job script for HTCondor
    job_script = f'''#!/bin/bash

cd {cmssw_base}
eval `scramv1 runtime -sh`
cd -

INPUT_FILES=$1
OUTPUT_FILE=$2

echo "Starting job at: $(date)"
echo "Input files: $INPUT_FILES"
echo "Output file: $OUTPUT_FILE"
echo "Current directory: $(pwd)"
echo "PATH: $PATH"

cmsRun {cmssw_base}/src/EgammaAnalysis/TnPTreeProducer/python/TnPTreeProducer_cfg.py {' '.join(args_list)} inputFiles=$INPUT_FILES outputFile=$OUTPUT_FILE
'''
    
    job_script_path = f'{config_dir}/run_job.sh'
    with open(job_script_path, 'w') as f:
        f.write(job_script)
    os.system(f'chmod +x {job_script_path}')
    
    # Prepare arguments string for local runner
    args_str = ' '.join(args_list)
    
    # Create local runner script
    local_runner = local_runner_script.replace('{cmssw_base}', cmssw_base).replace('{args_str}', args_str)
    local_runner_path = f'{config_dir}/run_job_local.sh'
    with open(local_runner_path, 'w') as f:
        f.write(local_runner)
    os.system(f'chmod +x {local_runner_path}')
    
    # Submit jobs - one per file for MC, grouped for data
    jobs_per_submission = 100 if isMC else 100
    
    condor_submit_file = f'{config_dir}/condor_submit.sub'
    
    with open(condor_submit_file, 'w') as f:
        f.write('executable = ' + job_script_path + '\n')
        f.write('arguments = $(inputfile) $(outputfile)\n')
        f.write('output = ' + log_dir + '/$(ClusterId).$(ProcId).out\n')
        f.write('error = ' + log_dir + '/$(ClusterId).$(ProcId).err\n')
        f.write('log = ' + log_dir + '/$(ClusterId).$(ProcId).log\n')
        f.write('should_transfer_files = YES\n')
        f.write('when_to_transfer_output = ON_EXIT\n')
        f.write('+JobFlavour = "testmatch"\n')
        f.write('request_cpus = 1\n')
        f.write('request_memory = 3GB\n')
        f.write('request_disk = 5GB\n')
        f.write('queue outputfile,inputfile from job_list.txt\n')
    
    # Create job list
    job_list_file = f'{config_dir}/job_list.txt'
    with open(job_list_file, 'w') as f:
        for i, file in enumerate(files):
            if isMC:
                # One output file per input file for MC
                if i % jobs_per_submission == 0:
                    file_group = files[i:i+jobs_per_submission]
                    output_file = f'{output_dir}/output_{i//jobs_per_submission}.root'
                    f.write(f'{output_file},{",".join(file_group)}\n')
            else:
                # Group data files
                if i % jobs_per_submission == 0:
                    file_group = files[i:i+jobs_per_submission]
                    output_file = f'{output_dir}/output_{i//jobs_per_submission}.root'
                    f.write(f'{output_file},{",".join(file_group)} \n')
    
    # Create submission script for HTCondor
    submit_script = f'''#!/bin/bash
cd {config_dir}
condor_submit -batch-name {era}_{requestName} -file job_list.txt condor_submit.sub
'''
    
    submit_script_path = f'{config_dir}/submit_jobs.sh'
    with open(submit_script_path, 'w') as f:
        f.write(submit_script)
    os.system(f'chmod +x {submit_script_path}')
    
    # Create local submission script
    local_submit_script = f'''#!/bin/bash
echo "=========================================="
echo "Local submission for {requestName}"
echo "=========================================="
echo ""
echo "To run locally, use:"
echo "cd {config_dir}"
echo "./run_job_local.sh [start_line] [end_line]"
echo ""
echo "Examples:"
echo "  ./run_job_local.sh            # Run all jobs"
echo "  ./run_job_local.sh 1 10       # Run jobs 1-10"
echo "  ./run_job_local.sh 11 20      # Run jobs 11-20"
echo ""
echo "The output files will have '_local' suffix added"
echo "=========================================="
'''
    
    local_submit_path = f'{config_dir}/submit_jobs_local.sh'
    with open(local_submit_path, 'w') as f:
        f.write(local_submit_script)
    os.system(f'chmod +x {local_submit_path}')
    
    print(f"Created HTCondor submission for {requestName}")
    print(f"  Dataset: {sample}")
    print(f"  Files: {len(files)}")
    print(f"  Output dir: {output_dir}")
    print(f"  To submit to HTCondor: {submit_script_path}")
    print(f"  To run locally: {local_submit_path}")
    
    return submit_script_path, local_submit_path

#
# Wrapping the submit command
#
def submitWrapper(requestName, sample, era, extraParam=[]):
    """Wrapper for submission"""
    if doL1matching:
        from getLeg1ThresholdForDoubleEle import getLeg1ThresholdForDoubleEle
        for leg1Threshold, json in getLeg1ThresholdForDoubleEle(era.replace("UL","").replace("preVFP","").replace("postVFP","")):
            print(f'Submitting for leg 1 threshold {leg1Threshold}')
            submit_htcondor(f'{requestName}_leg1Threshold{leg1Threshold}', sample, era, 
                          extraParam + [f'L1Threshold={leg1Threshold}'])
    else:
        submit_script, local_script = submit_htcondor(requestName, sample, era, extraParam)
        
        # Write to submission scripts
        with open("htcondor_submit_all.sh", "a") as f:
            f.write(f"echo 'Submitting {requestName} to HTCondor'\n")
            f.write(f"{submit_script}\n")
            f.write(f"echo 'Submitted {requestName}'\n")
            f.write(f"sleep 5\n\n")
        
        # Write to local submission scripts
        with open("local_submit_all.sh", "a") as f:
            f.write(f"echo '=========================================='\n")
            f.write(f"echo 'Local submission for {requestName}'\n")
            f.write(f"echo '=========================================='\n")
            f.write(f"cd /afs/cern.ch/user/h/haozhong/HT_Ntuple_sub_EGamma/crab_{submitVersion}/{era}_{requestName}/configs\n")
            f.write(f"./run_job_local.sh\n")
            f.write(f"echo ''\n")

#
# Main submission
#
if __name__ == "__main__":
    # Create submission scripts
    with open("htcondor_submit_all.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"# HTCondor submission script for {submitVersion}\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    with open("local_submit_all.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"# Local submission script for {submitVersion}\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("echo '=========================================='\n")
        f.write("echo 'Local job submission'\n")
        f.write("echo '=========================================='\n")
        f.write("echo ''\n")
        f.write("echo 'This script will run jobs locally using parallel execution'\n")
        f.write("echo 'Make sure you are in a CMSSW environment with proper setup'\n")
        f.write("echo ''\n")
        f.write("read -p 'Do you want to continue? (y/n): ' -n 1 -r\n")
        f.write("echo ''\n")
        f.write("if [[ ! $REPLY =~ ^[Yy]$ ]]\n")
        f.write("then\n")
        f.write("    echo 'Aborted.'\n")
        f.write("    exit 1\n")
        f.write("fi\n\n")
    
    # Check CMSSW version and submit samples
    from EgammaAnalysis.TnPTreeProducer.cmssw_version import isReleaseAbove
    
    if isReleaseAbove(12,4):
        era = '2022'
        eraPre = '2022preEE'
        eraPost = '2022postEE'
        
        # Data samples
        submitWrapper('EGamma_Run2022B', '/EGamma/Run2022B-27Jun2023-v2/MINIAOD', era)
        submitWrapper('EGamma_Run2022C', '/EGamma/Run2022C-27Jun2023-v1/MINIAOD', era)
        submitWrapper('EGamma_Run2022D', '/EGamma/Run2022D-27Jun2023-v2/MINIAOD', era)
        submitWrapper('EGamma_Run2022E', '/EGamma/Run2022E-27Jun2023-v1/MINIAOD', era)
        submitWrapper('EGamma_Run2022F', '/EGamma/Run2022F-22Sep2023-v1/MINIAOD', era)
        submitWrapper('EGamma_Run2022G', '/EGamma/Run2022G-22Sep2023-v2/MINIAOD', era)
        
        # MC samples
        submitWrapper(f'DY_LO_{eraPre}', '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22MiniAODv4-forPOG_130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_LO_{eraPost}', '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22EEMiniAODv4-forPOG_130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)
        submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v5/MINIAODSIM', eraPre)
        submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v5/MINIAODSIM', eraPost)

        era = '2023'
        eraPre = '2023preBPIX'
        eraPost = '2023postBPIX'
        
        # Data samples
        submitWrapper('EGamma0_Run2023Cv1', '/EGamma0/Run2023C-PromptReco-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2023Cv2', '/EGamma0/Run2023C-PromptReco-v2/MINIAOD', era)
        submitWrapper('EGamma0_Run2023Cv3', '/EGamma0/Run2023C-PromptReco-v3/MINIAOD', era)
        submitWrapper('EGamma0_Run2023Cv4', '/EGamma0/Run2023C-PromptReco-v4/MINIAOD', era)
        submitWrapper('EGamma1_Run2023Cv1', '/EGamma1/Run2023C-PromptReco-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2023Cv2', '/EGamma1/Run2023C-PromptReco-v2/MINIAOD', era)
        submitWrapper('EGamma1_Run2023Cv3', '/EGamma1/Run2023C-PromptReco-v3/MINIAOD', era)
        submitWrapper('EGamma1_Run2023Cv4', '/EGamma1/Run2023C-PromptReco-v4/MINIAOD', era)
        submitWrapper('EGamma0_Run2023Dv1', '/EGamma0/Run2023D-PromptReco-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2023Dv2', '/EGamma0/Run2023D-PromptReco-v2/MINIAOD', era)
        submitWrapper('EGamma1_Run2023Dv1', '/EGamma1/Run2023D-PromptReco-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2023Dv2', '/EGamma1/Run2023D-PromptReco-v2/MINIAOD', era)
        
        # MC samples
        submitWrapper(f'DY_LO_{eraPre}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_LO_{eraPost}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v4/MINIAODSIM', eraPost)
        submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v4/MINIAODSIM', eraPost)

    print("\n" + "="*80)
    print("Submission setup complete!")
    print("="*80)
    print("\nTo submit all jobs to HTCondor, run:")
    print("  bash htcondor_submit_all.sh")
    print("\nTo run jobs locally (parallel execution), run:")
    print("  bash local_submit_all.sh")
    print("\nFor individual datasets, go to their config directory and run:")
    print("  ./run_job_local.sh [start_line] [end_line]")
    print("\nOutput files will have '_local' suffix added.")
    print("="*80)