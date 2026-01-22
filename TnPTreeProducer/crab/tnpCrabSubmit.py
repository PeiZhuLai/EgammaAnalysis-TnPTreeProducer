#!/bin/env python
import os

#
# Example script to submit TnPTreeProducer to crab
#
submitVersion = "2026_01haozhong" # add some date here
doL1matching  = False

defaultArgs   = ['doEleID=False','doPhoID=False','doTrigger=True']
path = "/eos/user/h/haozhong/diele_HLT_sf/Ntuples/"

# mainOutputDir = '/store/group/phys_egamma/tnpTuples/%s/%s' % (os.environ['USER'], submitVersion)
mainOutputDir = '%s%s' % (path,submitVersion)
# Logging the current version of TnpTreeProducer here, such that you can find back what the actual code looked like when you were submitting

os.system('mkdir -p %s' % mainOutputDir)#######################
# os.system('(git log -n 1;git diff) &> /eos/cms/%s/git.log' % mainOutputDir)
os.system('(git log -n 1;git diff) &> %s/git.log' % mainOutputDir)
# path = '/store/group/phys_egamma/tnpTuples/%s/%s' % (os.environ['USER'], submitVersion)
# mainOutputDir = '%s%s' % (path,submitVersion)
# os.system('mkdir -p /eos/cms%s' % mainOutputDir)
# os.system('(git log -n 1;git diff) &> %s/git.log' % mainOutputDir)
#
# Common CRAB settings
#
from CRABClient.UserUtilities import config
config = config()

config.General.requestName             = ''
config.General.transferLogs            = False
config.General.workArea                = '%scrab_%s' % (path,submitVersion)

config.JobType.pluginName              = 'Analysis'
config.JobType.psetName                = '../python/TnPTreeProducer_cfg.py'
config.JobType.sendExternalFolder      = True
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset               = ''
config.Data.inputDBS                   = 'global'
config.Data.publication                = False
config.Data.allowNonValidInputDataset  = True
config.Site.storageSite                = 'T2_CH_CERN'


#
# Certified lumis for the different eras
#   (seems the JSON for UL2017 is slightly different from rereco 2017, it's not documented anywhere though)
#
def getLumiMask(era):
  if   era=='2016':   return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
  elif era=='2017':   return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt'
  elif era=='2018':   return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
  elif era=='UL2016preVFP': return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt'
  elif era=='UL2016postVFP': return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt'
  elif era=='UL2017': return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
  elif era=='UL2018': return 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt'
  elif era=='2022': return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json'

  elif era=='2023': return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'
  # elif era=='2024': return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'#tmp
  # elif era=='2024': return '/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json'
  elif era=='2024': return 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json'

#
# Submit command
#
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from http.client import HTTPException

crab_sub = open("crab_sub.sh", "w")
crab_status = open("crab_status.sh", "w")
crab_resub = open("crab_resub.sh", "w")
crab_merge = open("crab_merge.sh", "w")

# path = "/eos/user/h/haozhong/diele_HLT_sf/Ntuples/"
def submit(config, requestName, sample, era, json, extraParam=[]):
  isMC                        = 'SIM' in sample
  dMC = "data"
  if isMC: dMC = "mc"
  config.General.requestName  = '%s_%s' % (dMC, requestName)
  config.Data.inputDataset    = sample
  config.Data.outLFNDirBase   = f'/eos/user/h/haozhong/diele_HLT_sf/Ntuples/{submitVersion}/{era}/{dMC}'#'%s/%s/%s/' % (mainOutputDir, era, dMC)
  config.Data.splitting       = 'FileBased' if isMC else 'LumiBased'
  config.Data.lumiMask        = None if isMC else json
  config.Data.unitsPerJob     = 5 if isMC else 20
  config.JobType.pyCfgParams  = defaultArgs + ['isMC=True' if isMC else 'isMC=False', 'era=%s' % era] + extraParam
  outF = open('crab_submit_%s.py'%requestName, 'w')
  #outF.write(config)
  print( config, file=outF)
  outF.close()
  crab_sub.write("crab submit crab_submit_%s.py &\n"%requestName)
#######mkdir#############
  # os.system('mkdir -p %s/%s/%s/' % (mainOutputDir, era, dMC))
  crab_status.write("crab status -d %s/crab_%s/crab_%s_%s &\n"%(path,submitVersion, era, requestName))
  crab_resub.write("crab resubmit -d %s/crab_%s/crab_%s_%s &\n"%(path,submitVersion, era, requestName))
  haddIn = "%s/%s/%s/%s/%s/crab_%s_%s/*/*/*.root"%(path, submitVersion, era, dMC, sample.split("/")[1], era, requestName)
  haddOut = "%s/%s/%s_%s.root"%(path, submitVersion, dMC, requestName)
  print(haddOut)
  crab_merge.write('hadd -f %s %s & \n\n'%(haddOut, haddIn))
  #try:                           crabCommand('submit', config = config)
  #except HTTPException as hte:   print( "Failed submitting task: %s" % (hte.headers))
  #except ClientException as cle: print( "Failed submitting task: %s" % (cle))

#
# Wrapping the submit command
# In case of doL1matching=True, vary the L1Threshold and use sub-json
#
from multiprocessing import Process
def submitWrapper(requestName, sample, era, extraParam=[]):
  if doL1matching:
    from getLeg1ThresholdForDoubleEle import getLeg1ThresholdForDoubleEle
    for leg1Threshold, json in getLeg1ThresholdForDoubleEle(era.replace("UL","").replace("preVFP","").replace("postVFP","")):
      print( 'Submitting for leg 1 threshold %s' % (leg1Threshold))
      p = Process(target=submit, args=(config, '%s_leg1Threshold%s' % (requestName, leg1Threshold), sample, era, json, extraParam + ['L1Threshold=%s' % leg1Threshold]))
      p.start()
      p.join()
  else:
    #p = Process(target=submit, args=(config, requestName, sample, era, getLumiMask(era), extraParam))
    #p.start()
    #p.join()
    submit(config, requestName, sample, era, getLumiMask(era), extraParam) # print the config files


#
# List of samples to submit, with eras
# Here the default data/MC for UL and rereco are given (taken based on the release environment)
# If you would switch to AOD, don't forget to add 'isAOD=True' to the defaultArgs!
#
from EgammaAnalysis.TnPTreeProducer.cmssw_version import isReleaseAbove

if isReleaseAbove(12,4):
  era       = '2022'
  eraPre  = '2022preEE'
  eraPost = '2022postEE'
  # submitWrapper('EGamma_Run2022B',     '/EGamma/Run2022C-27Jun2023-v1/MINIAOD', era)
  submitWrapper('EGamma_Run2022C',     '/EGamma/Run2022C-27Jun2023-v1/MINIAOD', era)
  submitWrapper('EGamma_Run2022D',     '/EGamma/Run2022D-27Jun2023-v2/MINIAOD', era)

  # '''
  # submitWrapper('EGamma_Run2022C',     '/EGamma/Run2022C-PromptReco-v1/MINIAOD', era)
  # submitWrapper('EGamma_Run2022Dv1',   '/EGamma/Run2022D-PromptReco-v1/MINIAOD', era)
  # submitWrapper('EGamma_Run2022Dv2',   '/EGamma/Run2022D-PromptReco-v2/MINIAOD', era)
  # submitWrapper('EGamma_Run2022E',     '/EGamma/Run2022E-PromptReco-v1/MINIAOD', era)
  # '''
  submitWrapper('EGamma_Run2022E',     '/EGamma/Run2022E-27Jun2023-v1/MINIAOD', era)
  submitWrapper('EGamma_Run2022F',     '/EGamma/Run2022F-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma_Run2022G',     '/EGamma/Run2022G-PromptReco-v1/MINIAOD', era)
  
  submitWrapper('DY_LO_%s'%eraPre, '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22MiniAODv4-forPOG_130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM',  eraPre), 
  submitWrapper('DY_LO_%s'%eraPost, '/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/Run3Summer22EEMiniAODv4-forPOG_130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)
  submitWrapper('DY_NLO_%s'%eraPre, '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM', eraPre) 
  submitWrapper('DY_NLO_%s'%eraPost, '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM', eraPost)

  era       = '2023'
  eraPre  = '2023preBPIX'
  eraPost = '2023postBPIX'
 # '''
  # submitWrapper('EGamma0_Run2023B',   '/EGamma0/Run2023B-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma0_Run2023Cv1', '/EGamma0/Run2023C-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma0_Run2023Cv2', '/EGamma0/Run2023C-PromptReco-v2/MINIAOD', era)
  submitWrapper('EGamma0_Run2023Cv3', '/EGamma0/Run2023C-PromptReco-v3/MINIAOD', era)
  submitWrapper('EGamma0_Run2023Cv4', '/EGamma0/Run2023C-PromptReco-v4/MINIAOD', era)
 # submitWrapper('EGamma1_Run2023B',   '/EGamma1/Run2023B-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma1_Run2023Cv1', '/EGamma1/Run2023C-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma1_Run2023Cv2', '/EGamma1/Run2023C-PromptReco-v2/MINIAOD', era)
  submitWrapper('EGamma1_Run2023Cv3', '/EGamma1/Run2023C-PromptReco-v3/MINIAOD', era)
  submitWrapper('EGamma1_Run2023Cv4', '/EGamma1/Run2023C-PromptReco-v4/MINIAOD', era)

  submitWrapper('EGamma0_Run2023Dv1', '/EGamma0/Run2023D-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma0_Run2023Dv2', '/EGamma0/Run2023D-PromptReco-v2/MINIAOD', era)
  submitWrapper('EGamma1_Run2023Dv1', '/EGamma1/Run2023D-PromptReco-v1/MINIAOD', era)
  submitWrapper('EGamma1_Run2023Dv2', '/EGamma1/Run2023D-PromptReco-v2/MINIAOD', era)
  # '''
  submitWrapper('DY_LO_%s'%eraPre, '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v1/MINIAODSIM', eraPre)
  submitWrapper('DY_LO_%s'%eraPost, '/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v3/MINIAODSIM', eraPost)
  submitWrapper('DY_NLO_%s'%eraPre, '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v1/MINIAODSIM', eraPre)
  submitWrapper('DY_NLO_%s'%eraPost, '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v2-v3/MINIAODSIM', eraPost)

  era       = '2024'

  #submitWrapper('EGamma1_Run2023Dv2', '/EGamma1/Run2023D-PromptReco-v2/MINIAOD', era)#BCDEFGHI
  submitWrapper('DY_LO_MLL50_%s'%era, '/DYTo2L_MLL-50_TuneCP5_13p6TeV_pythia8/Run3Winter24MiniAOD-KeepSi_133X_mcRun3_2024_realistic_v8-v2/MINIAODSIM', era)
  submitWrapper('DY_LO_M50_%s'%era, '/DYto2L_M-50_TuneCP5_13p6TeV_pythia8/Run3Winter24MiniAOD-KeepSi_133X_mcRun3_2024_realistic_v8-v2/MINIAODSIM', era)

'''
if isReleaseAbove(10,6):
  era       = 'UL2016preVFP'
  submitWrapper('Run2016B', '/SingleElectron/Run2016B-21Feb2020_ver2_UL2016_HIPM-v1/MINIAOD', era)
  submitWrapper('Run2016C', '/SingleElectron/Run2016C-21Feb2020_UL2016_HIPM-v1/MINIAOD', era)
  submitWrapper('Run2016D', '/SingleElectron/Run2016D-21Feb2020_UL2016_HIPM-v1/MINIAOD', era)
  submitWrapper('Run2016E', '/SingleElectron/Run2016E-21Feb2020_UL2016_HIPM-v1/MINIAOD', era)
  submitWrapper('Run2016F', '/SingleElectron/Run2016F-21Feb2020_UL2016_HIPM-v1/MINIAOD', era)

  submitWrapper('DY_NLO',  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL16MiniAODAPV-106X_mcRun2_asymptotic_preVFP_v8-v1/MINIAODSIM', era)
  submitWrapper('DY_LO',   '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL16MiniAODAPV-106X_mcRun2_asymptotic_preVFP_v8-v1/MINIAODSIM', era)

  era       = 'UL2016postVFP'
  submitWrapper('Run2016F', '/SingleElectron/Run2016F-21Feb2020_UL2016-v1/MINIAOD', era)
  submitWrapper('Run2016G', '/SingleElectron/Run2016G-21Feb2020_UL2016-v1/MINIAOD', era)
  submitWrapper('Run2016H', '/SingleElectron/Run2016H-21Feb2020_UL2016-v2/MINIAOD', era)

  submitWrapper('DY_NLO',  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL16MiniAOD-106X_mcRun2_asymptotic_v13-v2/MINIAODSIM', era)
  submitWrapper('DY_LO',   '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL16MiniAOD-106X_mcRun2_asymptotic_v13-v2/MINIAODSIM', era)

  era       = 'UL2017'
  submitWrapper('Run2017B', '/SingleElectron/Run2017B-09Aug2019_UL2017-v1/MINIAOD', era)
  submitWrapper('Run2017C', '/SingleElectron/Run2017C-09Aug2019_UL2017-v1/MINIAOD', era)
  submitWrapper('Run2017D', '/SingleElectron/Run2017D-09Aug2019_UL2017-v1/MINIAOD', era)
  submitWrapper('Run2017E', '/SingleElectron/Run2017E-09Aug2019_UL2017-v1/MINIAOD', era)
  submitWrapper('Run2017F', '/SingleElectron/Run2017F-09Aug2019_UL2017_EcalRecovery-v1/MINIAOD', era)

  submitWrapper('DY_NLO',  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL16MiniAODAPV-106X_mcRun2_asymptotic_preVFP_v8-v1/MINIAODSIM', era)
  submitWrapper('DY_LO',   '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL16MiniAODAPV-106X_mcRun2_asymptotic_preVFP_v8-v1/MINIAODSIM', era)

  era       = 'UL2018'
  submitWrapper('Run2018A', '/EGamma/Run2018A-12Nov2019_UL2018-v2/MINIAOD', era)
  submitWrapper('Run2018B', '/EGamma/Run2018B-12Nov2019_UL2018-v2/MINIAOD', era)
  submitWrapper('Run2018C', '/EGamma/Run2018C-12Nov2019_UL2018-v2/MINIAOD', era)
  submitWrapper('Run2018D', '/EGamma/Run2018D-12Nov2019_UL2018-v4/MINIAOD', era)

  submitWrapper('DY_NLO',   '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2/MINIAODSIM', era)
  submitWrapper('DY_LO',    '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1/MINIAODSIM', era)

else:
  era       = '2016'
  submitWrapper('Run2016B', '/SingleElectron/Run2016B-17Jul2018_ver2-v1/MINIAOD', era)
  submitWrapper('Run2016C', '/SingleElectron/Run2016C-17Jul2018-v1/MINIAOD', era)
  submitWrapper('Run2016D', '/SingleElectron/Run2016D-17Jul2018-v1/MINIAOD', era)
  submitWrapper('Run2016E', '/SingleElectron/Run2016E-17Jul2018-v1/MINIAOD', era)
  submitWrapper('Run2016F', '/SingleElectron/Run2016F-17Jul2018-v1/MINIAOD', era)
  submitWrapper('Run2016G', '/SingleElectron/Run2016G-17Jul2018-v1/MINIAOD', era)
  submitWrapper('Run2016H', '/SingleElectron/Run2016H-17Jul2018-v1/MINIAOD', era)

  submitWrapper('DY_NLO', '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM', era)
  submitWrapper('DY_LO',  '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM', era)

  era       = '2017'
  submitWrapper('Run2017B', '/SingleElectron/Run2017B-31Mar2018-v1/MINIAOD', era)
  submitWrapper('Run2017C', '/SingleElectron/Run2017C-31Mar2018-v1/MINIAOD', era)
  submitWrapper('Run2017D', '/SingleElectron/Run2017D-31Mar2018-v1/MINIAOD', era)
  submitWrapper('Run2017E', '/SingleElectron/Run2017E-31Mar2018-v1/MINIAOD', era)
  submitWrapper('Run2017F', '/SingleElectron/Run2017F-31Mar2018-v1/MINIAOD', era)

  submitWrapper('DY1_LO',     '/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM', era)
  submitWrapper('DY1_LO_ext', '/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_v3_94X_mc2017_realistic_v14_ext1-v2/MINIAODSIM', era)
  submitWrapper('DY_LO',      '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM', era)
  submitWrapper('DY_LO_ext',  '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM', era)
  submitWrapper('DY_NLO',     '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',  era)
  submitWrapper('DY_NLO_ext', '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM', era)

  era       = '2018'
  submitWrapper('Run2018A', '/EGamma/Run2018A-17Sep2018-v2/MINIAOD', era)
  submitWrapper('Run2018B', '/EGamma/Run2018B-17Sep2018-v1/MINIAOD', era)
  submitWrapper('Run2018C', '/EGamma/Run2018C-17Sep2018-v1/MINIAOD', era)
  submitWrapper('Run2018D', '/EGamma/Run2018D-22Jan2019-v2/MINIAOD', era)

  submitWrapper('DY',         '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM', era)
  submitWrapper('DY_NLO',     '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM', era)
  submitWrapper('DY_NLO_ext', '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM', era)
  submitWrapper('DY_pow',     '/DYToEE_M-50_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM', era)
  '''
