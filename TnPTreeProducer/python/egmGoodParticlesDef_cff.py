import FWCore.ParameterSet.Config as cms



def calibrateEGM(process, options ):
    
    ### apply 80X regression
    from EgammaAnalysis.ElectronTools.regressionWeights_cfi import regressionWeights
    process = regressionWeights(process)

    process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
                                                       calibratedPatElectrons  = cms.PSet( initialSeed = cms.untracked.uint32(81),
                                                                                           engineName = cms.untracked.string('TRandom3'),                
                                                                                           ),
                                                       calibratedPatPhotons    = cms.PSet( initialSeed = cms.untracked.uint32(81),
                                                                                           engineName = cms.untracked.string('TRandom3'),                
                                                                                           ),
                                                       )

    process.load('EgammaAnalysis.ElectronTools.regressionApplication_cff')
    process.load('EgammaAnalysis.ElectronTools.calibratedPatElectronsRun2_cfi')
    process.load('EgammaAnalysis.ElectronTools.calibratedPatPhotonsRun2_cfi')

    process.calibratedPatElectrons.electrons = cms.InputTag(options['ELECTRON_COLL'])
    process.calibratedPatPhotons.photons     = cms.InputTag(options['PHOTON_COLL']  )
    if options['isMC']:
        process.calibratedPatElectrons.isMC = cms.bool(True)
        process.calibratedPatPhotons.isMC   = cms.bool(True)
    else :
        process.calibratedPatElectrons.isMC = cms.bool(False)
        process.calibratedPatPhotons.isMC   = cms.bool(False)


    
    process.selectElectronsBase = cms.EDFilter("PATElectronSelector",
                                               src = cms.InputTag('calibratedPatElectrons'),
                                               cut = cms.string(  options['ELECTRON_CUTS']),
                                               )

    process.selectPhotonsBase   = cms.EDFilter("PATPhotonSelector",
                                               src = cms.InputTag('calibratedPatPhotons' ),
                                               cut = cms.string(options['PHOTON_CUTS']),
                                               )

    ### change the input collection to be the calibrated energy one for all other modules from now on
    options['ELECTRON_COLL'] = 'selectElectronsBase'
    options['PHOTON_COLL']   = 'selectPhotonsBase'




###################################################################################
################  --- GOOD particles MiniAOD
################################################################################### 
def setGoodParticlesMiniAOD(process, options):

    if options['UseCalibEn']:  calibrateEGM( process, options )


    ########################### Extra variables for SUSY IDs ############
    if options['addSUSY']: 
        import EgammaAnalysis.TnPTreeProducer.electronsExtrasSUSY_cff  as eleSusyID
        eleSusyID.addSusyIDs( process, options )
        options['ELECTRON_COLL']        = "slimmedElectronsWithUserData"
    proc = "PAT"# PAT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  only your using /EGamma0/Run2024F-MINIv6NANOv15-v1/MINIAOD
    if options['isMC']:
        proc = "PAT"
        ########################### common electron prob ############
    process.eleVarHelper = cms.EDProducer("PatElectronVariableHelper",
                                          probes           = cms.InputTag(options['ELECTRON_COLL']),
                                          l1EGColl         = cms.InputTag('caloStage2Digis:EGamma'),
                                          vertexCollection = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                          beamSpot         = cms.InputTag("offlineBeamSpot"),
                                          conversions      = cms.InputTag("reducedEgamma:reducedConversions"),
                                          pfCandidates     = cms.InputTag("packedPFCandidates"),
                                          ebRecHits        = cms.InputTag("reducedEgamma","reducedEBRecHits",proc),
                                          eeRecHits        = cms.InputTag("reducedEgamma","reducedEERecHits",proc),
                                          rho_MiniIso     = cms.InputTag("fixedGridRhoFastjetAll"),
                                          rho_PFIso       = cms.InputTag("fixedGridRhoFastjetAll"),
                                          )

    # 双电子trigger leg1
    process.hltLeg1DR = cms.EDProducer("PatElectronHLTDRHelper",
        probes = cms.InputTag(options['ELECTRON_COLL']),  # 输入电子集合
        triggerBits = cms.InputTag("TriggerResults", "", "HLT"),  # TriggerResults标签
        triggerObjects = cms.InputTag("slimmedPatTrigger"),  # pat::TriggerObjectStandAlone集合
        filterLabel = cms.string("hltEle23Ele12CaloIdLTrackIdLIsoVLTrackIsoLeg1Filter"),  # 要匹配的filter名称
        outputDRName = cms.untracked.string("hltLeg1DR"),  # output ValueMap name
        dR = cms.double(9),  # ΔR匹配阈值
        useSuperCluster = cms.untracked.bool(False),  # 使用superCluster位置
        debug = cms.untracked.bool(False)  # 是否输出调试信息
    )

    # 双电子trigger leg2
    process.hltLeg2DR = cms.EDProducer("PatElectronHLTDRHelper",
        probes = cms.InputTag(options['ELECTRON_COLL']),
        triggerBits = cms.InputTag("TriggerResults", "", "HLT"),
        triggerObjects = cms.InputTag("slimmedPatTrigger"),
        filterLabel = cms.string("hltEle23Ele12CaloIdLTrackIdLIsoVLTrackIsoLeg2Filter"),  # leg2 filter
        outputDRName = cms.untracked.string("hltLeg2DR"),
        dR = cms.double(9),
        useSuperCluster = cms.untracked.bool(False),
        debug = cms.untracked.bool(False)
    )

    # 单电子trigger
    process.hltSingleDR = cms.EDProducer("PatElectronHLTDRHelper",
        probes = cms.InputTag(options['ELECTRON_COLL']),
        triggerBits = cms.InputTag("TriggerResults", "", "HLT"),
        triggerObjects = cms.InputTag("slimmedPatTrigger"),
        filterLabel = cms.string("hltEle30WPTightGsfTrackIsoFilter"),  # 单电子filter
        outputDRName = cms.untracked.string("hltSingleDR"),
        dR = cms.double(9),
        useSuperCluster = cms.untracked.bool(False),
        debug = cms.untracked.bool(False)
    )

    
    # 双电子trigger路径 - 同时输出leg1和leg2的ΔR
    process.HltDoubleLegDR = cms.EDProducer("PatElectronHLTPathDRHelper",
        probes = cms.InputTag(options['ELECTRON_COLL']),  # 输入电子集合
        triggerBits = cms.InputTag("TriggerResults", "", "HLT"),  # TriggerResults标签
        triggerObjects = cms.InputTag("slimmedPatTrigger"),  # pat::TriggerObjectStandAlone集合
        hltPath = cms.string("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v*"),  # HLT路径名称（注意不是filterLabel）
        outputDRNameLeg1 = cms.untracked.string("HltLeg1DR"),  # leg1的ΔR输出名称
        outputDRNameLeg2 = cms.untracked.string("HltLeg2DR"),  # leg2的ΔR输出名称
        dR = cms.double(9),  # ΔR匹配阈值
        useSuperCluster = cms.untracked.bool(False),  # 使用superCluster位置
        debug = cms.untracked.bool(False)  # 是否输出调试信息
    )

    ####################  Electron collection
    process.goodElectrons = cms.EDFilter("PATElectronRefSelector",
                                         src = cms.InputTag( options['ELECTRON_COLL'] ),
                                         cut = cms.string(   options['ELECTRON_CUTS'] ),
                                         )
    
    ####################  Photon collection
    process.goodPhotons   =  cms.EDFilter("PATPhotonRefSelector",
                                            src = cms.InputTag( options['PHOTON_COLL'] ),
                                            cut = cms.string(   options['PHOTON_CUTS'] )
                                            )

    
    #################### SUPERCLUSTER collections                                                                 
    process.superClusterCands = cms.EDProducer("ConcreteEcalCandidateProducer",
                                               src = cms.InputTag(options['SUPERCLUSTER_COLL']),
                                               particleType = cms.int32(11),
                                               )
    
    process.goodSuperClusters = cms.EDFilter("RecoEcalCandidateRefSelector",
                                             src = cms.InputTag("superClusterCands"),
                                             cut = cms.string(options['SUPERCLUSTER_CUTS']),
                                             filter = cms.bool(True)
                                             )


    process.sc_sequenceMiniAOD = cms.Sequence(
        process.superClusterCands +
        process.goodSuperClusters 
        )

###################################################################################
################  --- GOOD particles AOD
################################################################################### 
def setGoodParticlesAOD(process, options):


    process.eleVarHelper = cms.EDProducer("GsfElectronVariableHelper",
                                          probes           = cms.InputTag(options['ELECTRON_COLL']),
                                          vertexCollection = cms.InputTag("offlinePrimaryVertices"),
                                          l1EGColl         = cms.InputTag("caloStage2Digis:EGamma"),
                                          beamSpot         = cms.InputTag("offlineBeamSpot"),
                                          conversions      = cms.InputTag("allConversions"),
                                          pfCandidates     = cms.InputTag("particleFlow"),
                                          ebRecHits        = cms.InputTag("reducedEgamma","reducedEBRecHits","RECO"),
                                          eeRecHits        = cms.InputTag("reducedEgamma","reducedEERecHits","RECO")
                                          )

    process.hltVarHelper = cms.EDProducer("GsfElectronHLTVariableHelper",
                                            probes = cms.InputTag(options['ELECTRON_COLL']),
                                            hltCandidateCollection = cms.InputTag("hltEgammaCandidates"),
                                            mapOutputNames = cms.vstring("hltsieie",
                                                                        "hltecaliso",
                                                                        "hlthcaliso",
                                                                        "hlthoe",
                                                                        "hlttkiso",
                                                                        "hltdeta",
                                                                        "hltdetaseed",
                                                                        "hltdphi",
                                                                        "hlteop",
                                                                        "hltmishits"),
                                            mapInputTags = cms.VInputTag("hltEgammaClusterShape:sigmaIEtaIEta5x5",
                                                                        "hltEgammaEcalPFClusterIso",
                                                                        "hltEgammaHcalPFClusterIso",
                                                                        "hltEgammaHoverE", 
                                                                        "hltEgammaEleGsfTrackIso",
                                                                        "hltEgammaGsfTrackVars:Deta",
                                                                        "hltEgammaGsfTrackVars:DetaSeed",
                                                                        "hltEgammaGsfTrackVars:Dphi",
                                                                        "hltEgammaGsfTrackVars:OneOESuperMinusOneOP",
                                                                        "hltEgammaGsfTrackVars:MissingHits")
                                            )




   

    ####################  Electron collection
    process.goodElectrons = cms.EDFilter("GsfElectronRefSelector",
                                         src = cms.InputTag(options['ELECTRON_COLL']),
                                         cut = cms.string(options['ELECTRON_CUTS'])
                                         )

    ####################  Photon collection
    ### dummy in AOD (use miniAOD for photons)
    process.goodPhotons    =  cms.EDFilter("PhotonRefSelector",
                                            src = cms.InputTag( options['PHOTON_COLL'] ),
                                            cut = cms.string(   options['PHOTON_CUTS'] )
                                            )
    
    #################### SUPERCLUSTER collections                                                                 
    process.superClusterMerger =  cms.EDProducer("EgammaSuperClusterMerger",
                                                 src = cms.VInputTag(cms.InputTag("particleFlowSuperClusterECAL:particleFlowSuperClusterECALBarrel"),
                                                                     cms.InputTag("particleFlowSuperClusterECAL:particleFlowSuperClusterECALEndcapWithPreshower"),
#                                                                     cms.InputTag("particleFlowEGamma"),
                                                                     ),
                                                 )
    
    
    process.superClusterCands = cms.EDProducer("ConcreteEcalCandidateProducer",
                                               src = cms.InputTag("superClusterMerger"),
                                               particleType = cms.int32(11),
                                               )
    
    process.goodSuperClusters = cms.EDFilter("RecoEcalCandidateRefSelector",
                                             src = cms.InputTag("superClusterCands"),
                                             cut = cms.string(options['SUPERCLUSTER_CUTS']),
                                             filter = cms.bool(True)
                                             )


    process.recoEcalCandidateHelper = cms.EDProducer("RecoEcalCandidateVariableHelper",
                                                     probes = cms.InputTag("superClusterCands"),
                                                     countTracks = cms.bool( False ),
                                                     trkIsoPtMin = cms.double( 0.5 ),
                                                     trkIsoStripEndcap = cms.double( 0.03 ),
                                                     trackProducer = cms.InputTag( "generalTracks" ),
                                                     trkIsoStripBarrel = cms.double( 0.03 ),
                                                     trkIsoConeSize = cms.double( 0.4 ),
                                                     trkIsoVetoConeSize = cms.double( 0.06 ),
                                                     trkIsoRSpan = cms.double( 999999.0 ),
                                                     trkIsoZSpan = cms.double( 999999. )
                                                     )
    process.sc_sequenceAOD = cms.Sequence(
        process.superClusterMerger      +
        process.superClusterCands       +
        process.recoEcalCandidateHelper +
        process.goodSuperClusters     
        )
