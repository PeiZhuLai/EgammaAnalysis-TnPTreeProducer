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
# Submit function for HTCondor (单个作业提交版本)
#
def submit_htcondor_single(requestName, sample, era, extraParam=[]):
    """Submit individual jobs to HTCondor (one job per output file)"""
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
    
    # Create job script for single job execution
    job_script = f'''#!/bin/bash

# 获取参数
JOB_INDEX=$1
MAX_CONCURRENT_JOBS=$2
JOB_LIST_FILE=$3

cd {cmssw_base}
eval `scramv1 runtime -sh`
cd -

# 从job_list.txt读取第JOB_INDEX行的内容
# job_list.txt格式: outputfile,inputfile1,inputfile2,...
LINE=$(sed -n "${{JOB_INDEX}}p" "$JOB_LIST_FILE")
IFS=',' read -r OUTPUT_FILE INPUT_FILES <<< "$LINE"

echo "Starting job at: $(date)"
echo "Job index: $JOB_INDEX"
echo "Input files: $INPUT_FILES"
echo "Output file: $OUTPUT_FILE"
echo "Current directory: $(pwd)"

# 将逗号分隔的输入文件转换为空格分隔
INPUT_FILES_SPACE=$(echo "$INPUT_FILES" | tr ',' ' ')

# Run the analysis
cmsRun {cmssw_base}/src/EgammaAnalysis/TnPTreeProducer/python/TnPTreeProducer_cfg.py {' '.join(args_list)} inputFiles="$INPUT_FILES_SPACE" outputFile="$OUTPUT_FILE"
'''
    
    job_script_path = f'{config_dir}/run_single_job.sh'
    with open(job_script_path, 'w') as f:
        f.write(job_script)
    os.system(f'chmod +x {job_script_path}')
    
    # Create local batch submission script
    batch_script = f'''#!/bin/bash
# 本地批处理提交脚本
# 用法: ./submit_batch.sh [起始作业索引] [结束作业索引] [并行作业数]

JOB_LIST_FILE="${{1:-{config_dir}/job_list.txt}}"
START_INDEX="${{2:-1}}"
END_INDEX="${{3:-$(wc -l < "$JOB_LIST_FILE")}}"
MAX_CONCURRENT="${{4:-2}}"

echo "============================================="
echo "本地批处理提交"
echo "作业列表文件: $JOB_LIST_FILE"
echo "作业范围: $START_INDEX 到 $END_INDEX"
echo "并行作业数: $MAX_CONCURRENT"
echo "============================================="

# 创建日志目录
mkdir -p {log_dir}

# 创建condor提交文件（单个作业）
create_condor_job() {{
    local JOB_INDEX=$1
    local LOG_PREFIX="{log_dir}/job_$JOB_INDEX"
    
    cat > {config_dir}/condor_job_$JOB_INDEX.sub << EOF
universe = vanilla
executable = {job_script_path}
arguments = $JOB_INDEX $MAX_CONCURRENT $JOB_LIST_FILE
output = $LOG_PREFIX.out
error = $LOG_PREFIX.err
log = $LOG_PREFIX.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = $(sed -n "${{JOB_INDEX}}p" "$JOB_LIST_FILE" | cut -d',' -f1)
+JobFlavour = "testmatch"
request_cpus = 1
request_memory = 3GB
request_disk = 5GB
queue
EOF
}}

# 提交指定范围的作业
submit_jobs() {{
    local current_pids=()
    local job_count=0
    
    for (( JOB_INDEX=START_INDEX; JOB_INDEX<=END_INDEX; JOB_INDEX++ )); do
        echo "准备提交作业 $JOB_INDEX"
        
        # 创建condor提交文件
        create_condor_job $JOB_INDEX
        
        # 提交到HTCondor
        condor_submit {config_dir}/condor_job_$JOB_INDEX.sub &
        condor_pid=$!
        current_pids+=($condor_pid)
        job_count=$((job_count + 1))
        
        echo "已提交作业 $JOB_INDEX (PID: $condor_pid)"
        
        # 如果达到最大并行数，等待部分作业完成
        if [[ ${{#current_pids[@]}} -ge $MAX_CONCURRENT ]]; then
            echo "达到最大并行作业数 ($MAX_CONCURRENT)，等待..."
            
            # 等待任意一个作业完成
            while true; do
                for i in "${{!current_pids[@]}}"; do
                    if ! kill -0 "${{current_pids[i]}}" 2>/dev/null; then
                        echo "作业 $((i+1)) 已完成"
                        unset 'current_pids[i]'
                        current_pids=("${{current_pids[@]}}")
                        break 2
                    fi
                done
                sleep 5
            done
        fi
        
        sleep 1  # 避免过于频繁提交
    done
    
    # 等待剩余作业完成
    echo "等待剩余作业完成..."
    for pid in "${{current_pids[@]}}"; do
        if [[ -n "$pid" ]]; then
            wait $pid
            echo "作业完成 (PID: $pid)"
        fi
    done
    
    echo "============================================="
    echo "所有作业提交完成！"
    echo "总提交作业数: $job_count"
    echo "输出目录: {output_dir}"
    echo "日志目录: {log_dir}"
    echo "============================================="
}}

# 执行提交
submit_jobs
'''
    
    batch_script_path = f'{config_dir}/submit_batch.sh'
    with open(batch_script_path, 'w') as f:
        f.write(batch_script)
    os.system(f'chmod +x {batch_script_path}')
    
    # 创建快速提交脚本（简化版本）
    quick_submit_script = f'''#!/bin/bash
# 快速提交脚本 - 提交单个作业
# 用法: ./submit_quick.sh [作业索引]

JOB_INDEX="${{1:-1}}"
JOB_LIST_FILE="{config_dir}/job_list.txt"

if [[ ! -f "$JOB_LIST_FILE" ]]; then
    echo "错误: 作业列表文件不存在: $JOB_LIST_FILE"
    exit 1
fi

TOTAL_JOBS=$(wc -l < "$JOB_LIST_FILE")
if [[ $JOB_INDEX -lt 1 ]] || [[ $JOB_INDEX -gt $TOTAL_JOBS ]]; then
    echo "错误: 作业索引超出范围 (1-$TOTAL_JOBS)"
    exit 1
fi

# 创建condor提交文件
cat > {config_dir}/condor_single.sub << EOF
universe = vanilla
executable = {job_script_path}
arguments = $JOB_INDEX 1 $JOB_LIST_FILE
output = {log_dir}/single_$JOB_INDEX.out
error = {log_dir}/single_$JOB_INDEX.err
log = {log_dir}/single_$JOB_INDEX.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = $(sed -n "${{JOB_INDEX}}p" "$JOB_LIST_FILE" | cut -d',' -f1)
+JobFlavour = "testmatch"
request_cpus = 1
request_memory = 3GB
request_disk = 5GB
queue
EOF

echo "提交作业 $JOB_INDEX/$TOTAL_JOBS..."
condor_submit {config_dir}/condor_single.sub
echo "作业 $JOB_INDEX 已提交！"
'''
    
    quick_submit_path = f'{config_dir}/submit_quick.sh'
    with open(quick_submit_path, 'w') as f:
        f.write(quick_submit_script)
    os.system(f'chmod +x {quick_submit_path}')
    
    # Create job list file
    job_list_file = f'{config_dir}/job_list.txt'
    jobs_per_submission = 8 if isMC else 8
    
    with open(job_list_file, 'w') as f:
        for i, file in enumerate(files):
            if isMC:
                # Group MC files
                if i % jobs_per_submission == 0:
                    file_group = files[i:i+jobs_per_submission]
                    output_file = f'{output_dir}/output_{i//jobs_per_submission}.root'
                    f.write(f'{output_file},{",".join(file_group)}\n')
            else:
                # Group data files
                if i % jobs_per_submission == 0:
                    file_group = files[i:i+jobs_per_submission]
                    output_file = f'{output_dir}/output_{i//jobs_per_submission}.root'
                    f.write(f'{output_file},{",".join(file_group)}\n')
    
    # 创建管理脚本
    manage_script = f'''#!/bin/bash
# 作业管理脚本
# 用法: ./manage_jobs.sh [command] [options]

JOB_LIST_FILE="{config_dir}/job_list.txt"
TOTAL_JOBS=$(wc -l < "$JOB_LIST_FILE" 2>/dev/null || echo "0")

case "$1" in
    "status")
        echo "作业状态:"
        echo "作业总数: $TOTAL_JOBS"
        echo "输出目录: {output_dir}"
        echo "日志目录: {log_dir}"
        
        # 检查已完成作业
        COMPLETED=0
        for ((i=1; i<=TOTAL_JOBS; i++)); do
            OUTPUT_FILE=$(sed -n "${{i}}p" "$JOB_LIST_FILE" | cut -d',' -f1)
            if [[ -f "$OUTPUT_FILE" ]]; then
                COMPLETED=$((COMPLETED + 1))
            fi
        done
        
        echo "已完成作业: $COMPLETED/$TOTAL_JOBS"
        ;;
        
    "submit")
        START="${{2:-1}}"
        END="${{3:-$TOTAL_JOBS}}"
        CONCURRENT="${{4:-2}}"
        
        if [[ $TOTAL_JOBS -eq 0 ]]; then
            echo "错误: 没有作业可提交"
            exit 1
        fi
        
        {batch_script_path} "$JOB_LIST_FILE" "$START" "$END" "$CONCURRENT"
        ;;
        
    "submit-one")
        JOB_INDEX="${{2:-1}}"
        {quick_submit_path} "$JOB_INDEX"
        ;;
        
    "list")
        echo "作业列表 (共 $TOTAL_JOBS 个作业):"
        for ((i=1; i<=TOTAL_JOBS; i++)); do
            LINE=$(sed -n "${{i}}p" "$JOB_LIST_FILE")
            OUTPUT_FILE=$(echo "$LINE" | cut -d',' -f1)
            INPUT_COUNT=$(echo "$LINE" | tr ',' '\n' | wc -l)
            INPUT_COUNT=$((INPUT_COUNT - 1))
            
            if [[ -f "$OUTPUT_FILE" ]]; then
                STATUS="✓"
            else
                STATUS=" "
            fi
            
            echo "[$STATUS] $i: $OUTPUT_FILE (输入文件: $INPUT_COUNT)"
        done
        ;;
        
    "clean")
        echo "清理临时文件..."
        rm -f {config_dir}/condor_job_*.sub
        rm -f {config_dir}/condor_single.sub
        echo "临时文件已清理"
        ;;
        
    *)
        echo "用法: $0 [command]"
        echo ""
        echo "可用命令:"
        echo "  status             显示作业状态"
        echo "  submit [start] [end] [concurrent]  提交批处理作业"
        echo "  submit-one [index] 提交单个作业"
        echo "  list               列出所有作业"
        echo "  clean              清理临时文件"
        echo ""
        echo "示例:"
        echo "  $0 status"
        echo "  $0 submit 1 10 2    # 提交作业1-10，并行2个"
        echo "  $0 submit-one 5     # 提交单个作业5"
        echo "  $0 list"
        ;;
esac
'''
    
    manage_script_path = f'{config_dir}/manage_jobs.sh'
    with open(manage_script_path, 'w') as f:
        f.write(manage_script)
    os.system(f'chmod +x {manage_script_path}')
    
    print(f"创建了HTCondor独立作业提交配置：")
    print(f"  数据集: {sample}")
    print(f"  总作业数: 根据文件数自动分组")
    print(f"  输出目录: {output_dir}")
    print(f"")
    print(f"管理脚本: {manage_script_path}")
    print(f"  查看状态: {manage_script_path} status")
    print(f"  列出作业: {manage_script_path} list")
    print(f"  批量提交: {manage_script_path} submit [起始] [结束] [并行数]")
    print(f"  单作业提交: {manage_script_path} submit-one [作业索引]")
    
    return manage_script_path

#
# Wrapping the submit command
#
def submitWrapper(requestName, sample, era, extraParam=[]):
    """Wrapper for submission"""
    if doL1matching:
        from getLeg1ThresholdForDoubleEle import getLeg1ThresholdForDoubleEle
        for leg1Threshold, json in getLeg1ThresholdForDoubleEle(era.replace("UL","").replace("preVFP","").replace("postVFP","")):
            print(f'Submitting for leg 1 threshold {leg1Threshold}')
            manage_script = submit_htcondor_single(f'{requestName}_leg1Threshold{leg1Threshold}', sample, era, 
                          extraParam + [f'L1Threshold={leg1Threshold}'])
    else:
        manage_script = submit_htcondor_single(requestName, sample, era, extraParam)
        
        # Write to submission scripts
        with open("htcondor_submit_all.sh", "a") as f:
            f.write(f"echo '============================================='\n")
            f.write(f"echo '处理 {requestName}'\n")
            f.write(f"echo '============================================='\n")
            f.write(f"cd $(dirname {manage_script})\n")
            f.write(f"./manage_jobs.sh status\n")
            f.write(f"echo ''\n")

#
# Main submission
#
if __name__ == "__main__":
    # Create submission script
    with open("htcondor_submit_all.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"# HTCondor独立作业提交管理脚本 for {submitVersion}\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"echo '使用独立作业提交模式'\n")
        f.write(f"echo '每个作业独立提交，避免参数过长问题'\n")
        f.write(f"echo '使用 manage_jobs.sh 脚本进行作业管理'\n\n")
    
    # Check CMSSW version and submit samples
    from EgammaAnalysis.TnPTreeProducer.cmssw_version import isReleaseAbove
    
    if isReleaseAbove(12,4):
        era = '2022'
        eraPre = '2022preEE'
        eraPost = '2022postEE'
        
        # Data samples
        # submitWrapper('', '', era)
        submitWrapper('EGamma_Run2022B', '/EGamma/Run2022B-27Jun2023-v2/MINIAOD', era)
        submitWrapper('EGamma_Run2022C', '/EGamma/Run2022C-27Jun2023-v1/MINIAOD', era)
        submitWrapper('EGamma_Run2022D', '/EGamma/Run2022D-27Jun2023-v2/MINIAOD', era)
        submitWrapper('EGamma_Run2022E', '/EGamma/Run2022E-27Jun2023-v1/MINIAOD', era)
        # submitWrapper('EGamma_Run2022F', '/EGamma/Run2022F-PromptReco-v1/MINIAOD', era)
        
        submitWrapper('EGamma_Run2022F', '/EGamma/Run2022F-22Sep2023-v1/MINIAOD', era)
        submitWrapper('EGamma_Run2022G', '/EGamma/Run2022G-22Sep2023-v2/MINIAOD', era)
        # submitWrapper('EGamma_Run2022G', '/EGamma/Run2022G-PromptReco-v1/MINIAOD', era)
        
        # MC samples
        submitWrapper(f'DY_LO_{eraPre}', '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22MiniAODv4-forPOG_130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_LO_{eraPost}', '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22EEMiniAODv4-forPOG_130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)
        # submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v5/MINIAODSIM', eraPre)
        submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v5/MINIAODSIM', eraPost)
        # submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)

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
        # submitWrapper(f'DY_LO_{eraPre}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v1/MINIAODSIM', eraPre)
        submitWrapper(f'DY_LO_{eraPre}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_LO_{eraPost}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v4/MINIAODSIM', eraPost)
        submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM', eraPre)
        submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v4/MINIAODSIM', eraPost)
        # submitWrapper(f'DY_LO_{eraPost}', '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v3/MINIAODSIM', eraPost)
        # submitWrapper(f'DY_NLO_{eraPre}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v1/MINIAODSIM', eraPre)
        # submitWrapper(f'DY_NLO_{eraPost}', '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v3/MINIAODSIM', eraPost)

        era = '2024'
        submitWrapper('', '/EGamma0/Run2024B-PromptReco-v1/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024B-PromptReco-v1/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024C-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024C-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024D-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024D-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024E-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024E-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024F-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024F-MINIv6NANOv15-v1/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024G-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024G-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024H-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024H-MINIv6NANOv15-v2/MINIAOD', era)
        submitWrapper('', '/EGamma0/Run2024I-MINIv6NANOv15_v2-v1/MINIAOD', era)
        submitWrapper('', '/EGamma1/Run2024I-MINIv6NANOv15_v2-v1/MINIAOD', era)
        ##/EGamma0/Run2024C-2024CDEReprocessing-v1/MINIAOD
        ### /EGamma0/Run2024G-PromptReco-v1/MINIAOD
        ### /EGamma1/Run2024G-PromptReco-v1/MINIAOD
        submitWrapper('DY_LO_MLL50_2024', '/DYTo2L_MLL-50_TuneCP5_13p6TeV_pythia8/Run3Winter24MiniAOD-KeepSi_133X_mcRun3_2024_realistic_v8-v2/MINIAODSIM', era)
        submitWrapper('DY_LO_M50_2024', '/DYto2L_M-50_TuneCP5_13p6TeV_pythia8/Run3Winter24MiniAOD-KeepSi_133X_mcRun3_2024_realistic_v8-v2/MINIAODSIM', era)
    
    print("\n" + "="*80)
    print("HTCondor独立作业提交配置完成！")
    print("")
    print("每个数据集都有独立的管理脚本：")
    print("  manage_jobs.sh      - 作业管理脚本")
    print("  submit_batch.sh     - 批量提交脚本")
    print("  submit_quick.sh     - 单作业提交脚本")
    print("  job_list.txt        - 作业列表文件")
    print("")
    print("常用命令：")
    print("  ./manage_jobs.sh status          # 查看作业状态")
    print("  ./manage_jobs.sh list            # 列出所有作业")
    print("  ./manage_jobs.sh submit 1 10 2   # 提交作业1-10，并行2个")
    print("  ./manage_jobs.sh submit-one 5    # 提交单个作业5")
    print("")
    print("要查看所有配置状态，运行：bash htcondor_submit_all.sh")
    print(f"输出将保存在：{mainOutputDir}")
    print("="*80)