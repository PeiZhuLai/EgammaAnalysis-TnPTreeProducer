# import FWCore.ParameterSet.Config as cms

# isoForEle = cms.EDProducer("PatElectronVariableHelper",
#     src = cms.InputTag("slimmedElectrons"),
#     relative = cms.bool(False),
#     doQuadratic = cms.bool(False),
#     rho_MiniIso = cms.InputTag("fixedGridRhoFastjetAll"),
#     rho_PFIso = cms.InputTag("fixedGridRhoFastjetAll"),
#     # EAFile_MiniIso = cms.FileInPath("RecoEgamma/ElectronIdentification/data/Run3_Winter22/effAreaElectrons_cone03_pfNeuHadronsAndPhotons_122X.txt"),
#     EAFile_MiniIso = cms.FileInPath("/eos/user/h/haozhong/diele_HLT_sf/effAreaElectrons_cone03_pfNeuHadronsAndPhotons_122X.txt"),
#     EAFile_PFIso = cms.FileInPath("/eos/user/h/haozhong/diele_HLT_sf/effAreaElectrons_cone03_pfNeuHadronsAndPhotons_122X.txt"),
# )
#画蛇添足