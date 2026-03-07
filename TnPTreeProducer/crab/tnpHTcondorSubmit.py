#!/bin/env python
import os
import sys
import json
import subprocess
from datetime import datetime

#
# Example script to submit TnPTreeProducer to HTCondor
#
submitVersion = "260307" # add some date here
doL1matching  = False

defaultArgs   = ['doEleID=True','doPhoID=False','doTrigger=True']
path = "/eos/home-p/pelai/HZa/root_make_TnP_ntuple/"

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
+JobFlavour = "workday"
request_cpus = 1
request_memory = 2000
request_disk = 2000
queue
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
    # job_dir = f"{path}/crab_{submitVersion}/{era}_{requestName}"
    job_dir = f"/afs/cern.ch/work/p/pelai/HZa/make_TnP_ntuple/CMSSW_15_0_2/src/EgammaAnalysis/TnPTreeProducer/crab_{submitVersion}/{era}_{requestName}"
    log_dir = f"{job_dir}/logs"
    config_dir = f"{job_dir}/configs"
    output_dir = f"{mainOutputDir}/{era}/{dMC}/{requestName}" #直接使用requestNam##########################
    
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
    
    # if not isMC:
    #     json_file = getLumiMask(era)
    #     if json_file:
    #         args_list.append(f'jsonFile={json_file}')
    
    # Create job script
    job_script = f'''#!/bin/bash

cd {cmssw_base}
eval `scramv1 runtime -sh`
cd -
export X509_USER_PROXY=/eos/user/h/haozhong/my_x509_user_proxy
# 获取参数
INPUT_FILES=$1
OUTPUT_FILE=$2

# 调试信息
echo "Starting job at: $(date)"
echo "Input files: $INPUT_FILES"
echo "Output file: $OUTPUT_FILE"
echo "Current directory: $(pwd)"
echo "PATH: $PATH"
# Run the analysis
cmsRun {cmssw_base}/src/EgammaAnalysis/TnPTreeProducer/python/TnPTreeProducer_cfg.py {' '.join(args_list)} inputFiles=$1 outputFile=$2
'''
    
    job_script_path = f'{config_dir}/run_job.sh'
    with open(job_script_path, 'w') as f:
        f.write(job_script)
    os.system(f'chmod +x {job_script_path}')
    
    # Submit jobs - one per file for MC, grouped for data
    jobs_per_submission = 16 if isMC else 32  # Group data files############################################
    
    condor_submit_file = f'{config_dir}/condor_submit.sub'
    
    with open(condor_submit_file, 'w') as f:
        f.write('executable = ' + job_script_path + '\n')
        f.write('arguments = $(inputfile) $(outputfile)\n')
        f.write('output = ' + log_dir + '/$(ClusterId).$(ProcId).out\n')
        f.write('error = ' + log_dir + '/$(ClusterId).$(ProcId).err\n')
        f.write('log = ' + log_dir + '/$(ClusterId).log\n')
        f.write('should_transfer_files = YES\n')
        f.write('when_to_transfer_output = ON_EXIT\n')
        # f.write('transfer_input_files = \n')
        # f.write('transfer_output_files = $(outputfile)\n')
        f.write('+JobFlavour = "testmatch"\n')
        # f.write('+AccountingGroup = "group_u_CMST3.all"\n')#do not need it
        f.write('request_cpus = 1\n')
        f.write('request_memory = 2.3GB\n')#1.5 is ok
        f.write('request_disk = 0.5GB\n')#0.05 is ok but too small
        f.write('queue outputfile,inputfile from job_list.txt\n')
    
    # Create job list
    job_list_file = f'{config_dir}/job_list.txt'
    with open(job_list_file, 'w') as f:
        for i, file in enumerate(files):
            if isMC:
                # One output file per input file for MC
                # output_file = f'{output_dir}/output_{i}.root'
                # f.write(f'inputfile={file} outputfile={output_file}\n')
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
    
    # Create submission script
    submit_script = f'''#!/bin/bash
cd {config_dir}
condor_submit -batch-name {era}_{requestName} -file job_list.txt condor_submit.sub
'''
    
    submit_script_path = f'{config_dir}/submit_jobs.sh'
    with open(submit_script_path, 'w') as f:
        f.write(submit_script)
    os.system(f'chmod +x {submit_script_path}')
    
    print(f"Created HTCondor submission for {requestName}")
    print(f"  Dataset: {sample}")
    print(f"  Files: {len(files)}")
    print(f"  Output dir: {output_dir}")
    print(f"  To submit: {submit_script_path}")
    
    return submit_script_path

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
        submit_script = submit_htcondor(requestName, sample, era, extraParam)
        
        # Write to submission scripts
        with open("htcondor_submit_all.sh", "a") as f:
            f.write(f"echo 'Submitting {requestName}'\n")
            f.write(f"{submit_script}\n")
            f.write(f"echo 'Submitted {requestName}'\n")
            f.write(f"sleep 5\n\n")

#
# Main submission
#
if __name__ == "__main__":
    # Create submission script
    with open("htcondor_submit_all.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"# HTCondor submission script for {submitVersion}\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Check CMSSW version and submit samples
    from EgammaAnalysis.TnPTreeProducer.cmssw_version import isReleaseAbove
    
    if isReleaseAbove(12,4):
        # era = '2022'
        # eraPre = '2022preEE'
        # eraPost = '2022postEE'
        
        # # Data samples
        # # submitWrapper('', '', era)
        # submitWrapper('EGamma_Run2022B', '/EGamma/Run2022B-27Jun2023-v2/MINIAOD', era)
        # submitWrapper('EGamma_Run2022C', '/EGamma/Run2022C-27Jun2023-v1/MINIAOD', era)
        # submitWrapper('EGamma_Run2022D', '/EGamma/Run2022D-27Jun2023-v2/MINIAOD', era)
        # submitWrapper('EGamma_Run2022E', '/EGamma/Run2022E-27Jun2023-v1/MINIAOD', era)
        # # submitWrapper('EGamma_Run2022F', '/EGamma/Run2022F-PromptReco-v1/MINIAOD', era)
        
        # submitWrapper('EGamma_Run2022F', '/EGamma/Run2022F-22Sep2023-v1/MINIAOD', era)
        # submitWrapper('EGamma_Run2022G', '/EGamma/Run2022G-22Sep2023-v2/MINIAOD', era)
        # # submitWrapper('EGamma_Run2022G', '/EGamma/Run2022G-PromptReco-v1/MINIAOD', era)
        
        # # MC samples
        # submitWrapper(f'DY_LO_{eraPre}', '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22MiniAODv4-forPOG_130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_LO_{eraPost}', '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22EEMiniAODv4-forPOG_130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)
        # # submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v5/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v5/MINIAODSIM', eraPost)
        # # submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)

        # era = '2023'
        # eraPre = '2023preBPIX'
        # eraPost = '2023postBPIX'
        
        # # # Data samples
        # # submitWrapper('EGamma0_Run2023Cv1', '/EGamma0/Run2023C-PromptReco-v1/MINIAOD', era)
        # # submitWrapper('EGamma0_Run2023Cv2', '/EGamma0/Run2023C-PromptReco-v2/MINIAOD', era)
        # # submitWrapper('EGamma0_Run2023Cv3', '/EGamma0/Run2023C-PromptReco-v3/MINIAOD', era)
        # # submitWrapper('EGamma0_Run2023Cv4', '/EGamma0/Run2023C-PromptReco-v4/MINIAOD', era)
        # # submitWrapper('EGamma1_Run2023Cv1', '/EGamma1/Run2023C-PromptReco-v1/MINIAOD', era)
        # # submitWrapper('EGamma1_Run2023Cv2', '/EGamma1/Run2023C-PromptReco-v2/MINIAOD', era)
        # # submitWrapper('EGamma1_Run2023Cv3', '/EGamma1/Run2023C-PromptReco-v3/MINIAOD', era)
        # # submitWrapper('EGamma1_Run2023Cv4', '/EGamma1/Run2023C-PromptReco-v4/MINIAOD', era)
        # # submitWrapper('EGamma0_Run2023Dv1', '/EGamma0/Run2023D-PromptReco-v1/MINIAOD', era)
        # # submitWrapper('EGamma0_Run2023Dv2', '/EGamma0/Run2023D-PromptReco-v2/MINIAOD', era)
        # # submitWrapper('EGamma1_Run2023Dv1', '/EGamma1/Run2023D-PromptReco-v1/MINIAOD', era)
        # # submitWrapper('EGamma1_Run2023Dv2', '/EGamma1/Run2023D-PromptReco-v2/MINIAOD', era)
        
        # # MC samples
        # # submitWrapper(f'DY_LO_{eraPre}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v1/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_LO_{eraPre}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_LO_{eraPost}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v4/MINIAODSIM', eraPost)
        # submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v4/MINIAODSIM', eraPost)
        # # submitWrapper(f'DY_LO_{eraPost}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v3/MINIAODSIM', eraPost)
        # # submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v1/MINIAODSIM', eraPre)
        # # submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v3/MINIAODSIM', eraPost)

        era = '2024'
        # # # Data samples
        submitWrapper('EGamma0_Run2024B', '/EGamma0/Run2024B-PromptReco-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2024B', '/EGamma1/Run2024B-PromptReco-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2024C', '/EGamma0/Run2024C-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2024C', '/EGamma1/Run2024C-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2024D', '/EGamma0/Run2024D-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2024D', '/EGamma1/Run2024D-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2024E', '/EGamma0/Run2024E-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2024E', '/EGamma1/Run2024E-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2024F', '/EGamma0/Run2024F-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2024F', '/EGamma1/Run2024F-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2024G', '/EGamma0/Run2024G-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('EGamma1_Run2024G', '/EGamma1/Run2024G-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('EGamma0_Run2024H', '/EGamma0/Run2024H-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('EGamma1_Run2024H', '/EGamma1/Run2024H-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('EGamma0_Run2024I', '/EGamma0/Run2024I-MINIv6NANOv15_v2-v1/MINIAOD', era)
        submitWrapper('EGamma1_Run2024I', '/EGamma1/Run2024I-MINIv6NANOv15_v2-v1/MINIAOD', era)
        ##/EGamma0/Run2024C-2024CDEReprocessing-v1/MINIAOD
        ### /EGamma0/Run2024G-PromptReco-v1/MINIAOD
        ### /EGamma1/Run2024G-PromptReco-v1/MINIAOD
        # # MC samples
        submitWrapper('DY_LO_2024', '/DYto2E-4Jets_Bin-MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v3/MINIAODSIM', era)
        submitWrapper('DY_NLO_2024', '/DYto2E-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v4/MINIAODSIM', era)


    
    print("\n" + "="*80)
    print("HTCondor submission setup complete!")
    print("To submit all jobs, run: bash htcondor_submit_all.sh")
    print(f"Output will be in: {mainOutputDir}")
    print("="*80)