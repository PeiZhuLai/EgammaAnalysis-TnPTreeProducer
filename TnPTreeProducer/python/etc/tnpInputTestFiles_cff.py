import FWCore.ParameterSet.Config as cms

# Some miniAOD testfiles, about 1000 events copied to our eos storage
# (not running directly on datasets because they get moved around all the time and xrootd sucks)
filesMiniAOD_2018 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIIAutumn18MiniAOD-DYJetsToLL_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/Egamma-Run2018A-17Sep2018-v2.root'),
}

filesMiniAOD_2022 = {
    'data' : cms.untracked.vstring('root://cmsxrootd.fnal.gov//store/data/Run2022C/EGamma/MINIAOD/27Jun2023-v1/2530000/5907ab2b-e68f-474c-80aa-e5057c23cf7b.root'),
    #'data' :   cms.untracked.vstring('file:/afs/cern.ch/work/r/rverma/public/cms-egamma-hlt/bpix/CMSSW_13_0_9/src/step3_inMINIAOD.root'),
}
filesMiniAOD_2022preEE = {
    'mc' : cms.untracked.vstring('/store/mc/Run3Summer22MiniAODv4/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/MINIAODSIM/forPOG_130X_mcRun3_2022_realistic_v5-v2/60000/b577d7c0-f980-4534-822b-2da67e1424d2.root')
}
filesMiniAOD_2022postEE = {
    'mc' : cms.untracked.vstring('/store/mc/Run3Summer22EEMiniAODv4/DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8/MINIAODSIM/forPOG_130X_mcRun3_2022_realistic_postEE_v6-v2/30000/02e5dc07-abcd-43ca-a273-cbe4b6b53a73.root')
}

filesMiniAOD_2023 = {
    'data' : cms.untracked.vstring('root://cms-xrd-global.cern.ch//store/data/Run2023D/EGamma0/MINIAOD/PromptReco-v2/000/370/776/00000/2744e097-88da-4e48-9740-d0bfe1d54fce.root'),
}
filesMiniAOD_2023preBPIX = {
    'mc' : cms.untracked.vstring('/store/mc/Run3Summer23MiniAODv4/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v1/70002/1e07f519-3a32-4eda-85f2-2da221f43e7f.root')
}
filesMiniAOD_2023postBPIX = {
    'mc' : cms.untracked.vstring('/store/mc/Run3Summer23BPixMiniAODv4/DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/50001/9ffc5afa-1d8c-4370-a9dd-5464a372770b.root')
}
filesMiniAOD_2024 = {
    'mc' : cms.untracked.vstring('/store/mc/Run3Winter24MiniAOD/DYto2L_M-50_TuneCP5_13p6TeV_pythia8/MINIAODSIM/KeepSi_133X_mcRun3_2024_realistic_v8-v2/2560000/7c936ae9-2ac8-409c-b7ac-3e9f7b05ddae.root')
}

filesMiniAOD_2017 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIIFall17MiniAODv2-DYJetsToLL_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2017B-31Mar2018-v1.root'),
}

filesMiniAOD_2016 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer16MiniAODv3-DYJetsToLL_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2016B-17Jul2018_ver2-v1.root'),
}


# Some miniAOD UL testfiles, which are available now and hopefully don't get deleted too soon
filesMiniAOD_UL2016preVFP = {
    'mc':   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer19UL16MiniAODAPV-DYJetsToLL_M-50.root'),
    'data': cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2016E-21Feb2020_UL2016_HIPM.root'),
}

filesMiniAOD_UL2016postVFP = {
    'mc':   cms.untracked.vstring(''),
    'data': cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2016F-21Feb2020_UL2016-postVFP.root'),
}

filesMiniAOD_UL2018 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer19UL18MiniAOD-DYJetsToEE_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/Egamma-Run2018D-12Nov2019_UL2018.root'),
}

filesMiniAOD_UL2017 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer19UL17MiniAOD-DYJetsToLL_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2017F-09Aug2019_UL2017.root'),
}


# AOD UL testfiles
filesAOD_UL2016preVFP = {
    'mc':   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer19UL16RECOAPV-DYJetsToLL_M-50.root'),
    'data': cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2016E-21Feb2020_UL2016_HIPM-AOD.root'),
}

filesAOD_UL2016postVFP = {
    'mc':   cms.untracked.vstring(''),
    'data': cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2016F-21Feb2020_UL2016-postVFP-AOD.root'),
}

filesAOD_UL2018 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer19UL18RECO-DYToEE_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/Egamma-Run2018D-12Nov2019_UL2018-AOD.root'),
}

filesAOD_UL2017 = {
    'mc' :   cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/RunIISummer19UL17RECO-DYToEE_M-50.root'),
    'data' : cms.untracked.vstring('file:/eos/cms/store/group/phys_egamma/tnpTuples/testFiles/SingleElectron-Run2017F-09Aug2019_UL2017-AOD.root'),
}

filesAOD_2022 = {
    'mc':   cms.untracked.vstring('file:../test/data/f10037a7-aa8b-4c35-9c7a-be28ecf22736.root'),
    'data': cms.untracked.vstring('file:../test/data/10037a7-aa8b-4c35-9c7a-be28ecf22736.root')
}
