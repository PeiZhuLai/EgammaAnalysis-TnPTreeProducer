// #ifndef _ELECTRONVARIABLEHELPER_H
// #define _ELECTRONVARIABLEHELPER_H

// #include "FWCore/Framework/interface/one/EDProducer.h"
// #include "FWCore/Framework/interface/Event.h"
// #include "FWCore/ParameterSet/interface/ParameterSet.h"
// #include "FWCore/Utilities/interface/InputTag.h"

// #include "DataFormats/Common/interface/ValueMap.h"

// #include "DataFormats/VertexReco/interface/Vertex.h"
// #include "DataFormats/VertexReco/interface/VertexFwd.h"

// #include "DataFormats/L1Trigger/interface/L1EmParticle.h"
// #include "DataFormats/L1Trigger/interface/L1EmParticleFwd.h"
// #include "DataFormats/L1Trigger/interface/EGamma.h"
// #include "DataFormats/HLTReco/interface/TriggerFilterObjectWithRefs.h"

// #include "DataFormats/Math/interface/deltaR.h"

// #include "DataFormats/PatCandidates/interface/PackedCandidate.h"
// #include "DataFormats/Candidate/interface/CandidateFwd.h"
// #include "DataFormats/Candidate/interface/Candidate.h"

// #include <DataFormats/PatCandidates/interface/Electron.h>

// #include "DataFormats/EgammaCandidates/interface/Conversion.h"
// //#include "RecoEgamma/EgammaTools/interface/ConversionTools.h" //outdated
// #include "CommonTools/Egamma/interface/ConversionTools.h"

// #include "EgammaAnalysis/TnPTreeProducer/plugins/WriteValueMap.h"
// #include "EgammaAnalysis/TnPTreeProducer/plugins/isolations.h"

// #include "TMath.h"

// //Since this is supposed to run both with CMSSW_10_2_X and CMSSW_10_6_X
// //but some of the methods changed and are not compatible, we use this check
// //on the compiler version to establish whether we are in a 102X or 106X release.
// //102X still have a 7.3.X version of gcc, while 106X have 7.4.X 
// #define GCC_VERSION ( 10000 * __GNUC__ + 100 * __GNUC_MINOR__ + __GNUC_PATCHLEVEL__ )

// #if GCC_VERSION > 70400
// #define CMSSW_106plus
// #endif

// template <class T>
// class ElectronVariableHelper : public edm::one::EDProducer<>{
//  public:
//   explicit ElectronVariableHelper(const edm::ParameterSet & iConfig);
//   virtual ~ElectronVariableHelper() ;

//   virtual void produce(edm::Event & iEvent, const edm::EventSetup & iSetup) override;

// private:
//   edm::EDGetTokenT<std::vector<T> > probesToken_;
//   edm::EDGetTokenT<reco::VertexCollection> vtxToken_;
//   edm::EDGetTokenT<BXVector<l1t::EGamma> > l1EGToken_;
//   edm::EDGetTokenT<reco::ConversionCollection> conversionsToken_;
//   edm::EDGetTokenT<reco::BeamSpot> beamSpotToken_;
//   edm::EDGetTokenT<edm::View<reco::Candidate>> pfCandidatesToken_;
//   edm::EDGetTokenT<EcalRecHitCollection> recHitsEBToken_;
//   edm::EDGetTokenT<EcalRecHitCollection> recHitsEEToken_;

//   bool isMiniAODformat;
// };

// template<class T>
// ElectronVariableHelper<T>::ElectronVariableHelper(const edm::ParameterSet & iConfig) :
//   probesToken_(consumes<std::vector<T> >(iConfig.getParameter<edm::InputTag>("probes"))),
//   vtxToken_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertexCollection"))),
//   l1EGToken_(consumes<BXVector<l1t::EGamma> >(iConfig.getParameter<edm::InputTag>("l1EGColl"))),
//   conversionsToken_(consumes<reco::ConversionCollection>(iConfig.getParameter<edm::InputTag>("conversions"))),
//   beamSpotToken_(consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("beamSpot"))),
//   pfCandidatesToken_(consumes<edm::View<reco::Candidate>>(iConfig.getParameter<edm::InputTag>("pfCandidates"))),
//   recHitsEBToken_(consumes<EcalRecHitCollection>(iConfig.getParameter<edm::InputTag>("ebRecHits"))),
//   recHitsEEToken_(consumes<EcalRecHitCollection>(iConfig.getParameter<edm::InputTag>("eeRecHits")))
// {

//   produces<edm::ValueMap<float>>("dz");
//   produces<edm::ValueMap<float>>("dxy");
//   produces<edm::ValueMap<float>>("sip");
//   produces<edm::ValueMap<float>>("missinghits");
//   produces<edm::ValueMap<float>>("gsfhits");
//   produces<edm::ValueMap<float>>("l1e");
//   produces<edm::ValueMap<float>>("l1et");
//   produces<edm::ValueMap<float>>("l1eta");
//   produces<edm::ValueMap<float>>("l1phi");
//   produces<edm::ValueMap<float>>("pfPt");
//   produces<edm::ValueMap<float>>("convVtxFitProb");
//   produces<edm::ValueMap<float>>("kfhits");
//   produces<edm::ValueMap<float>>("kfchi2");
//   produces<edm::ValueMap<float>>("ioemiop");
//   produces<edm::ValueMap<float>>("5x5circularity");
//   produces<edm::ValueMap<float>>("pfLeptonIsolation");
//   produces<edm::ValueMap<float>>("hasMatchedConversion");
//   produces<edm::ValueMap<float>>("seedGain");

//   isMiniAODformat = true;
// }

// template<class T>
// ElectronVariableHelper<T>::~ElectronVariableHelper()
// {}


// template<class T>
// void ElectronVariableHelper<T>::produce(edm::Event & iEvent, const edm::EventSetup & iSetup) {

//   // read input
//   edm::Handle<std::vector<T>> probes;
//   edm::Handle<reco::VertexCollection> vtxH;

//   iEvent.getByToken(probesToken_, probes);
//   iEvent.getByToken(vtxToken_, vtxH);
//   const reco::VertexRef vtx(vtxH, 0);

//   edm::Handle<BXVector<l1t::EGamma>> l1Cands;
//   iEvent.getByToken(l1EGToken_, l1Cands);

//   edm::Handle<reco::ConversionCollection> conversions;
//   iEvent.getByToken(conversionsToken_, conversions);

//   edm::Handle<reco::BeamSpot> beamSpotHandle;
//   iEvent.getByToken(beamSpotToken_, beamSpotHandle);
//   const reco::BeamSpot* beamSpot = &*(beamSpotHandle.product());

//   edm::Handle<edm::View<reco::Candidate>> pfCandidates;
//   iEvent.getByToken(pfCandidatesToken_, pfCandidates);

//   // prepare vector for output
//   std::vector<float> dzVals;
//   std::vector<float> dxyVals;
//   std::vector<float> sipVals;
//   std::vector<float> mhVals;

//   std::vector<float> l1EVals;
//   std::vector<float> l1EtVals;
//   std::vector<float> l1EtaVals;
//   std::vector<float> l1PhiVals;
//   std::vector<float> pfPtVals;
//   std::vector<float> convVtxFitProbVals;
//   std::vector<float> kfhitsVals;
//   std::vector<float> kfchi2Vals;
//   std::vector<float> ioemiopVals;
//   std::vector<float> ocVals;

//   std::vector<float> gsfhVals;

//   std::vector<float> hasMatchedConversionVals;

//   std::vector<float> seedGains; // seed gain for scales

//   const auto& recHitsEBProd = iEvent.get(recHitsEBToken_);
//   const auto& recHitsEEProd = iEvent.get(recHitsEEToken_);

//   typename std::vector<T>::const_iterator probe, endprobes = probes->end();

//   for (probe = probes->begin(); probe != endprobes; ++probe) {

//     //---Clone the pat::Electron
//     pat::Electron l((pat::Electron)*probe);

//     dzVals.push_back(probe->gsfTrack()->dz(vtx->position()));
//     dxyVals.push_back(probe->gsfTrack()->dxy(vtx->position()));

//     // SIP
//     float IP      = fabs(l.dB(pat::Electron::PV3D));
//     float IPError = l.edB(pat::Electron::PV3D);
//     sipVals.push_back(IP/IPError);

//     mhVals.push_back(float(probe->gsfTrack()->hitPattern().numberOfLostHits(reco::HitPattern::MISSING_INNER_HITS)));
//     gsfhVals.push_back(float(probe->gsfTrack()->hitPattern().trackerLayersWithMeasurement()));
//     float l1e = 999999.;
//     float l1et = 999999.;
//     float l1eta = 999999.;
//     float l1phi = 999999.;
//     float pfpt = 999999.;
//     float dRmin = 0.3;

//     for (std::vector<l1t::EGamma>::const_iterator l1Cand = l1Cands->begin(0); l1Cand != l1Cands->end(0); ++l1Cand) {

//       float dR = deltaR(l1Cand->eta(), l1Cand->phi() , probe->superCluster()->eta(), probe->superCluster()->phi());
//       if (dR < dRmin) {
//         dRmin = dR;
//         l1e = l1Cand->energy();
//         l1et = l1Cand->et();
//         l1eta = l1Cand->eta();
//         l1phi = l1Cand->phi();
//       }
//     }

//     for( size_t ipf = 0; ipf < pfCandidates->size(); ++ipf ) {
//       auto pfcand = pfCandidates->ptrAt(ipf);
//       if(abs(pfcand->pdgId()) != 11) continue;
//       float dR = deltaR(pfcand->eta(), pfcand->phi(), probe->eta(), probe->phi());
//       if(dR < 0.0001) pfpt = pfcand->pt();
//     }

//     l1EVals.push_back(l1e);
//     l1EtVals.push_back(l1et);
//     l1EtaVals.push_back(l1eta);
//     l1PhiVals.push_back(l1phi);
//     pfPtVals.push_back(pfpt);

//     // Store hasMatchedConversion (currently stored as float instead of bool, as it allows to implement it in the same way as other variables)
//     #ifdef CMSSW_106plus
//     hasMatchedConversionVals.push_back((float)ConversionTools::hasMatchedConversion(*probe, *conversions, beamSpot->position()));
//     #else
//     hasMatchedConversionVals.push_back((float)ConversionTools::hasMatchedConversion(*probe, conversions, beamSpot->position()));
//     #endif

//     // Conversion vertex fit
//     float convVtxFitProb = -1.;

//     #ifdef CMSSW_106plus
//     reco::Conversion const* convRef = ConversionTools::matchedConversion(*probe,*conversions, beamSpot->position());
//     if(!convRef==0) {
//         const reco::Vertex &vtx = convRef->conversionVertex();
//         if (vtx.isValid()) {
//             convVtxFitProb = TMath::Prob( vtx.chi2(),  vtx.ndof());
//         }
//     }
//     #else
//     reco::ConversionRef convRef = ConversionTools::matchedConversion(*probe, conversions, beamSpot->position());
//     if(!convRef.isNull()) {
//       const reco::Vertex &vtx = convRef.get()->conversionVertex();
//       if (vtx.isValid()) {
// 	convVtxFitProb = TMath::Prob( vtx.chi2(),  vtx.ndof());
//       }
//     }
//     #endif
//     convVtxFitProbVals.push_back(convVtxFitProb);


//     // kf track related variables
//     bool validKf=false;
//     reco::TrackRef trackRef = probe->closestCtfTrackRef();
//     validKf = trackRef.isAvailable();
//     validKf &= trackRef.isNonnull();
//     float kfchi2 = validKf ? trackRef->normalizedChi2() : 0 ; //ielectron->track()->normalizedChi2() : 0 ;
//     float kfhits = validKf ? trackRef->hitPattern().trackerLayersWithMeasurement() : -1. ;

//     kfchi2Vals.push_back(kfchi2);
//     kfhitsVals.push_back(kfhits);

//     // 5x5circularity
//     float oc = probe->full5x5_e5x5() != 0. ? 1. - (probe->full5x5_e1x5() / probe->full5x5_e5x5()) : -1.;
//     ocVals.push_back(oc);

//     // 1/E - 1/p
//     float ele_pin_mode  = probe->trackMomentumAtVtx().R();
//     float ele_ecalE     = probe->ecalEnergy();
//     float ele_IoEmIop   = -1;
//     if(ele_ecalE != 0 || ele_pin_mode != 0) {
//         ele_IoEmIop = 1.0 / ele_ecalE - (1.0 / ele_pin_mode);
//     }

//     ioemiopVals.push_back(ele_IoEmIop);

//     // seed gain loop

//     auto detid = probe->superCluster()->seed()->seed();
//     const auto& coll = probe->isEB() ? recHitsEBProd : recHitsEEProd;
//     auto seed = coll.find(detid);
//     float tmpSeedVal = 12.0;
//     if (seed != coll.end()){
//         if (seed->checkFlag(EcalRecHit::kHasSwitchToGain6)) tmpSeedVal = 6.0;
//         if (seed->checkFlag(EcalRecHit::kHasSwitchToGain1)) tmpSeedVal = 1.0;
//     }
//     seedGains.push_back(tmpSeedVal);
//   }

//   // convert into ValueMap and store
//   writeValueMap(iEvent, probes, dzVals, "dz");
//   writeValueMap(iEvent, probes, dxyVals, "dxy");
//   writeValueMap(iEvent, probes, sipVals, "sip");
//   writeValueMap(iEvent, probes, mhVals, "missinghits");
//   writeValueMap(iEvent, probes, gsfhVals, "gsfhits");
//   writeValueMap(iEvent, probes, l1EVals, "l1e");
//   writeValueMap(iEvent, probes, l1EtVals, "l1et");
//   writeValueMap(iEvent, probes, l1EtaVals, "l1eta");
//   writeValueMap(iEvent, probes, l1PhiVals, "l1phi");
//   writeValueMap(iEvent, probes, pfPtVals, "pfPt");
//   writeValueMap(iEvent, probes, convVtxFitProbVals, "convVtxFitProb");
//   writeValueMap(iEvent, probes, kfhitsVals, "kfhits");
//   writeValueMap(iEvent, probes, kfchi2Vals, "kfchi2");
//   writeValueMap(iEvent, probes, ioemiopVals, "ioemiop");
//   writeValueMap(iEvent, probes, ocVals, "5x5circularity");
//   writeValueMap(iEvent, probes, hasMatchedConversionVals, "hasMatchedConversion");
//   writeValueMap(iEvent, probes, seedGains, "seedGain");

//   // PF lepton isolations (will only work in miniAOD)
//   if(isMiniAODformat){
//     try {
//       auto pfLeptonIsolations = computePfLeptonIsolations(*probes, *pfCandidates);
//       for(unsigned int i = 0; i < probes->size(); ++i){
// 	pfLeptonIsolations[i] /= (*probes)[i].pt();
//       }
//       writeValueMap(iEvent, probes, pfLeptonIsolations, "pfLeptonIsolation");
//     } catch (std::bad_cast const&){
//       isMiniAODformat = false;
//     }
//   }
// }

// #endif
#ifndef _ELECTRONVARIABLEHELPER_H
#define _ELECTRONVARIABLEHELPER_H

#include "FWCore/Framework/interface/one/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/Common/interface/ValueMap.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/L1Trigger/interface/L1EmParticle.h"
#include "DataFormats/L1Trigger/interface/L1EmParticleFwd.h"
#include "DataFormats/L1Trigger/interface/EGamma.h"
#include "DataFormats/HLTReco/interface/TriggerFilterObjectWithRefs.h"

#include "DataFormats/Math/interface/deltaR.h"

#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/Candidate/interface/CandidateFwd.h"
#include "DataFormats/Candidate/interface/Candidate.h"

#include <DataFormats/PatCandidates/interface/Electron.h>

#include "DataFormats/EgammaCandidates/interface/Conversion.h"
#include "CommonTools/Egamma/interface/ConversionTools.h"

#include "EgammaAnalysis/TnPTreeProducer/plugins/WriteValueMap.h"
#include "EgammaAnalysis/TnPTreeProducer/plugins/isolations.h"


// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/global/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "CommonTools/Egamma/interface/EffectiveAreas.h"

#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/Photon.h"
#include "DataFormats/PatCandidates/interface/IsolatedTrack.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/PatCandidates/interface/Isolation.h"
#include "DataFormats/Common/interface/View.h"

#include "TMath.h"

//Since this is supposed to run both with CMSSW_10_2_X and CMSSW_10_6_X
//but some of the methods changed and are not compatible, we use this check
//on the compiler version to establish whether we are in a 102X or 106X release.
//102X still have a 7.3.X version of gcc, while 106X have 7.4.X 
#define GCC_VERSION ( 10000 * __GNUC__ + 100 * __GNUC_MINOR__ + __GNUC_PATCHLEVEL__ )

#if GCC_VERSION > 70400
#define CMSSW_106plus
#endif

template <class T>
class ElectronVariableHelper : public edm::one::EDProducer<>{
 public:
  explicit ElectronVariableHelper(const edm::ParameterSet & iConfig);
  virtual ~ElectronVariableHelper() ;

  virtual void produce(edm::Event & iEvent, const edm::EventSetup & iSetup) override;

private:
  edm::EDGetTokenT<std::vector<T> > probesToken_;
  edm::EDGetTokenT<reco::VertexCollection> vtxToken_;
  edm::EDGetTokenT<BXVector<l1t::EGamma> > l1EGToken_;
  edm::EDGetTokenT<reco::ConversionCollection> conversionsToken_;
  edm::EDGetTokenT<reco::BeamSpot> beamSpotToken_;
  edm::EDGetTokenT<edm::View<reco::Candidate>> pfCandidatesToken_;
  edm::EDGetTokenT<EcalRecHitCollection> recHitsEBToken_;
  edm::EDGetTokenT<EcalRecHitCollection> recHitsEEToken_;
  
  // 添加rho tokens
  edm::EDGetTokenT<double> rhoMiniIsoToken_;
  edm::EDGetTokenT<double> rhoPFIsoToken_;

  bool isMiniAODformat;
  
  // 添加获取有效面积的函数
  double getEffectiveAreaMiniIso(double eta, double pt) const;
  double getEffectiveAreaPFIso(double eta) const;
  double getEffectiveAreaPFIso04(double eta) const;
};

template<class T>
ElectronVariableHelper<T>::ElectronVariableHelper(const edm::ParameterSet & iConfig) :
  probesToken_(consumes<std::vector<T> >(iConfig.getParameter<edm::InputTag>("probes"))),
  vtxToken_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertexCollection"))),
  l1EGToken_(consumes<BXVector<l1t::EGamma> >(iConfig.getParameter<edm::InputTag>("l1EGColl"))),
  conversionsToken_(consumes<reco::ConversionCollection>(iConfig.getParameter<edm::InputTag>("conversions"))),
  beamSpotToken_(consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("beamSpot"))),
  pfCandidatesToken_(consumes<edm::View<reco::Candidate>>(iConfig.getParameter<edm::InputTag>("pfCandidates"))),
  recHitsEBToken_(consumes<EcalRecHitCollection>(iConfig.getParameter<edm::InputTag>("ebRecHits"))),
  recHitsEEToken_(consumes<EcalRecHitCollection>(iConfig.getParameter<edm::InputTag>("eeRecHits"))),
  // 初始化rho tokens
  rhoMiniIsoToken_(consumes<double>(iConfig.getParameter<edm::InputTag>("rho_MiniIso"))),
  rhoPFIsoToken_(consumes<double>(iConfig.getParameter<edm::InputTag>("rho_PFIso")))
{

  produces<edm::ValueMap<float>>("dz");
  produces<edm::ValueMap<float>>("dxy");
  produces<edm::ValueMap<float>>("sip");
  produces<edm::ValueMap<float>>("missinghits");
  produces<edm::ValueMap<float>>("gsfhits");
  produces<edm::ValueMap<float>>("l1e");
  produces<edm::ValueMap<float>>("l1et");
  produces<edm::ValueMap<float>>("l1eta");
  produces<edm::ValueMap<float>>("l1phi");
  produces<edm::ValueMap<float>>("pfPt");
  produces<edm::ValueMap<float>>("convVtxFitProb");
  produces<edm::ValueMap<float>>("kfhits");
  produces<edm::ValueMap<float>>("kfchi2");
  produces<edm::ValueMap<float>>("ioemiop");
  produces<edm::ValueMap<float>>("5x5circularity");
  produces<edm::ValueMap<float>>("pfLeptonIsolation");
  produces<edm::ValueMap<float>>("hasMatchedConversion");
  produces<edm::ValueMap<float>>("seedGain");
  
  // 添加隔离变量
  produces<edm::ValueMap<float>>("miniIsoChg");
  produces<edm::ValueMap<float>>("miniIsoAll");
  produces<edm::ValueMap<float>>("pfIsoChg");
  produces<edm::ValueMap<float>>("pfIsoAll");
  produces<edm::ValueMap<float>>("pfIsoAll04");

  isMiniAODformat = true;
}

template<class T>
ElectronVariableHelper<T>::~ElectronVariableHelper()
{}

// 有效面积计算函数
template<class T>
double ElectronVariableHelper<T>::getEffectiveAreaMiniIso(double eta, double pt) const {
  const std::vector<double> etaBins = {0.0, 1.000, 1.479, 2.0, 2.2, 2.3, 2.4, 999.0};
  const std::vector<double> effAreaMiniIso = {0.1243, 0.1458, 0.0992, 0.0794, 0.0762, 0.0766, 0.1003};
  
  double absEta = fabs(eta);
  double area = 0.0;
  
  for (size_t i = 0; i < etaBins.size() - 1; ++i) {
    if (absEta >= etaBins[i] && absEta < etaBins[i + 1]) {
      area = effAreaMiniIso[i];
      break;
    }
  }
  
  // 根据MiniIso公式调整有效面积
  double R = 10.0 / std::min(std::max(pt, 50.0), 200.0);
  return area * std::pow(R / 0.3, 2);
}

template<class T>
double ElectronVariableHelper<T>::getEffectiveAreaPFIso(double eta) const {
  const std::vector<double> etaBins = {0.0, 1.000, 1.479, 2.0, 2.2, 2.3, 2.4, 999.0};
  const std::vector<double> effAreaPFIso = {0.1243, 0.1458, 0.0992, 0.0794, 0.0762, 0.0766, 0.1003};
  
  double absEta = fabs(eta);
  
  for (size_t i = 0; i < etaBins.size() - 1; ++i) {
    if (absEta >= etaBins[i] && absEta < etaBins[i + 1]) {
      return effAreaPFIso[i];
    }
  }
  
  return effAreaPFIso.back();
}

template<class T>
double ElectronVariableHelper<T>::getEffectiveAreaPFIso04(double eta) const {
  // PFIso04使用相同的有效面积
  return getEffectiveAreaPFIso(eta);
}

template<class T>
void ElectronVariableHelper<T>::produce(edm::Event & iEvent, const edm::EventSetup & iSetup) {

  // read input
  edm::Handle<std::vector<T>> probes;
  edm::Handle<reco::VertexCollection> vtxH;

  iEvent.getByToken(probesToken_, probes);
  iEvent.getByToken(vtxToken_, vtxH);
  const reco::VertexRef vtx(vtxH, 0);

  edm::Handle<BXVector<l1t::EGamma>> l1Cands;
  iEvent.getByToken(l1EGToken_, l1Cands);

  edm::Handle<reco::ConversionCollection> conversions;
  iEvent.getByToken(conversionsToken_, conversions);

  edm::Handle<reco::BeamSpot> beamSpotHandle;
  iEvent.getByToken(beamSpotToken_, beamSpotHandle);
  const reco::BeamSpot* beamSpot = &*(beamSpotHandle.product());

  edm::Handle<edm::View<reco::Candidate>> pfCandidates;
  iEvent.getByToken(pfCandidatesToken_, pfCandidates);
  
  // 读取rho值
  edm::Handle<double> rhoMiniIsoHandle;
  edm::Handle<double> rhoPFIsoHandle;
  iEvent.getByToken(rhoMiniIsoToken_, rhoMiniIsoHandle);
  iEvent.getByToken(rhoPFIsoToken_, rhoPFIsoHandle);
  double rhoMiniIso = *rhoMiniIsoHandle;
  double rhoPFIso = *rhoPFIsoHandle;

  // prepare vector for output
  std::vector<float> dzVals;
  std::vector<float> dxyVals;
  std::vector<float> sipVals;
  std::vector<float> mhVals;

  std::vector<float> l1EVals;
  std::vector<float> l1EtVals;
  std::vector<float> l1EtaVals;
  std::vector<float> l1PhiVals;
  std::vector<float> pfPtVals;
  std::vector<float> convVtxFitProbVals;
  std::vector<float> kfhitsVals;
  std::vector<float> kfchi2Vals;
  std::vector<float> ioemiopVals;
  std::vector<float> ocVals;

  std::vector<float> gsfhVals;

  std::vector<float> hasMatchedConversionVals;

  std::vector<float> seedGains; // seed gain for scales
  
  // 添加隔离变量
  std::vector<float> miniIsoChgVals;
  std::vector<float> miniIsoAllVals;
  std::vector<float> pfIsoChgVals;
  std::vector<float> pfIsoAllVals;
  std::vector<float> pfIsoAll04Vals;

  const auto& recHitsEBProd = iEvent.get(recHitsEBToken_);
  const auto& recHitsEEProd = iEvent.get(recHitsEEToken_);

  typename std::vector<T>::const_iterator probe, endprobes = probes->end();

  for (probe = probes->begin(); probe != endprobes; ++probe) {

    //---Clone the pat::Electron
    pat::Electron l((pat::Electron)*probe);

    dzVals.push_back(probe->gsfTrack()->dz(vtx->position()));
    dxyVals.push_back(probe->gsfTrack()->dxy(vtx->position()));

    // SIP
    float IP      = fabs(l.dB(pat::Electron::PV3D));
    float IPError = l.edB(pat::Electron::PV3D);
    sipVals.push_back(IP/IPError);

    mhVals.push_back(float(probe->gsfTrack()->hitPattern().numberOfLostHits(reco::HitPattern::MISSING_INNER_HITS)));
    gsfhVals.push_back(float(probe->gsfTrack()->hitPattern().trackerLayersWithMeasurement()));
    float l1e = 999999.;
    float l1et = 999999.;
    float l1eta = 999999.;
    float l1phi = 999999.;
    float pfpt = 999999.;
    float dRmin = 0.3;

    for (std::vector<l1t::EGamma>::const_iterator l1Cand = l1Cands->begin(0); l1Cand != l1Cands->end(0); ++l1Cand) {

      float dR = deltaR(l1Cand->eta(), l1Cand->phi() , probe->superCluster()->eta(), probe->superCluster()->phi());
      if (dR < dRmin) {
        dRmin = dR;
        l1e = l1Cand->energy();
        l1et = l1Cand->et();
        l1eta = l1Cand->eta();
        l1phi = l1Cand->phi();
      }
    }

    for( size_t ipf = 0; ipf < pfCandidates->size(); ++ipf ) {
      auto pfcand = pfCandidates->ptrAt(ipf);
      if(abs(pfcand->pdgId()) != 11) continue;
      float dR = deltaR(pfcand->eta(), pfcand->phi(), probe->eta(), probe->phi());
      if(dR < 0.0001) pfpt = pfcand->pt();
    }

    l1EVals.push_back(l1e);
    l1EtVals.push_back(l1et);
    l1EtaVals.push_back(l1eta);
    l1PhiVals.push_back(l1phi);
    pfPtVals.push_back(pfpt);

    // Store hasMatchedConversion (currently stored as float instead of bool, as it allows to implement it in the same way as other variables)
    #ifdef CMSSW_106plus
    hasMatchedConversionVals.push_back((float)ConversionTools::hasMatchedConversion(*probe, *conversions, beamSpot->position()));
    #else
    hasMatchedConversionVals.push_back((float)ConversionTools::hasMatchedConversion(*probe, conversions, beamSpot->position()));
    #endif

    // Conversion vertex fit
    float convVtxFitProb = -1.;

    #ifdef CMSSW_106plus
    reco::Conversion const* convRef = ConversionTools::matchedConversion(*probe,*conversions, beamSpot->position());
    if(!convRef==0) {
        const reco::Vertex &vtx = convRef->conversionVertex();
        if (vtx.isValid()) {
            convVtxFitProb = TMath::Prob( vtx.chi2(),  vtx.ndof());
        }
    }
    #else
    reco::ConversionRef convRef = ConversionTools::matchedConversion(*probe, conversions, beamSpot->position());
    if(!convRef.isNull()) {
      const reco::Vertex &vtx = convRef.get()->conversionVertex();
      if (vtx.isValid()) {
	convVtxFitProb = TMath::Prob( vtx.chi2(),  vtx.ndof());
      }
    }
    #endif
    convVtxFitProbVals.push_back(convVtxFitProb);


    // kf track related variables
    bool validKf=false;
    reco::TrackRef trackRef = probe->closestCtfTrackRef();
    validKf = trackRef.isAvailable();
    validKf &= trackRef.isNonnull();
    float kfchi2 = validKf ? trackRef->normalizedChi2() : 0 ; //ielectron->track()->normalizedChi2() : 0 ;
    float kfhits = validKf ? trackRef->hitPattern().trackerLayersWithMeasurement() : -1. ;

    kfchi2Vals.push_back(kfchi2);
    kfhitsVals.push_back(kfhits);

    // 5x5circularity
    float oc = probe->full5x5_e5x5() != 0. ? 1. - (probe->full5x5_e1x5() / probe->full5x5_e5x5()) : -1.;
    ocVals.push_back(oc);

    // 1/E - 1/p
    float ele_pin_mode  = probe->trackMomentumAtVtx().R();
    float ele_ecalE     = probe->ecalEnergy();
    float ele_IoEmIop   = -1;
    if(ele_ecalE != 0 || ele_pin_mode != 0) {
        ele_IoEmIop = 1.0 / ele_ecalE - (1.0 / ele_pin_mode);
    }

    ioemiopVals.push_back(ele_IoEmIop);
    
    // 计算隔离变量
    // MiniIso
    auto miniIso = l.miniPFIsolation();
    float miniChg = miniIso.chargedHadronIso();
    float miniNeu = miniIso.neutralHadronIso();
    float miniPho = miniIso.photonIso();
    float miniEA = getEffectiveAreaMiniIso(l.eta(), l.pt());
    float miniIsoChg = miniChg / l.pt();
    float miniIsoAll = (miniChg + std::max(0.0, miniNeu + miniPho - rhoMiniIso * miniEA)) / l.pt();
    
    // PFIso03
    auto pfIso03 = l.pfIsolationVariables();
    float pfChg03 = pfIso03.sumChargedHadronPt;
    float pfNeu03 = pfIso03.sumNeutralHadronEt;
    float pfPho03 = pfIso03.sumPhotonEt;
    float pfEA03 = getEffectiveAreaPFIso(l.eta());
    float pfIsoChg = pfChg03 / l.pt();
    float pfIsoAll = (pfChg03 + std::max(0.0, pfNeu03 + pfPho03 - rhoPFIso * pfEA03)) / l.pt();
    
    // PFIso04
    float pfChg04 = l.chargedHadronIso();
    float pfNeu04 = l.neutralHadronIso();
    float pfPho04 = l.photonIso();
    float pfEA04 = getEffectiveAreaPFIso04(l.eta());
    float pfIsoAll04 = (pfChg04 + std::max(0.0, pfNeu04 + pfPho04 - rhoPFIso * pfEA04 * 16.0/9.0)) / l.pt();
    
    miniIsoChgVals.push_back(miniIsoChg);
    miniIsoAllVals.push_back(miniIsoAll);
    pfIsoChgVals.push_back(pfIsoChg);
    pfIsoAllVals.push_back(pfIsoAll);
    pfIsoAll04Vals.push_back(pfIsoAll04);

    // seed gain loop
    auto detid = probe->superCluster()->seed()->seed();
    const auto& coll = probe->isEB() ? recHitsEBProd : recHitsEEProd;
    auto seed = coll.find(detid);
    float tmpSeedVal = 12.0;
    if (seed != coll.end()){
        if (seed->checkFlag(EcalRecHit::kHasSwitchToGain6)) tmpSeedVal = 6.0;
        if (seed->checkFlag(EcalRecHit::kHasSwitchToGain1)) tmpSeedVal = 1.0;
    }
    seedGains.push_back(tmpSeedVal);
  }

  // convert into ValueMap and store
  writeValueMap(iEvent, probes, dzVals, "dz");
  writeValueMap(iEvent, probes, dxyVals, "dxy");
  writeValueMap(iEvent, probes, sipVals, "sip");
  writeValueMap(iEvent, probes, mhVals, "missinghits");
  writeValueMap(iEvent, probes, gsfhVals, "gsfhits");
  writeValueMap(iEvent, probes, l1EVals, "l1e");
  writeValueMap(iEvent, probes, l1EtVals, "l1et");
  writeValueMap(iEvent, probes, l1EtaVals, "l1eta");
  writeValueMap(iEvent, probes, l1PhiVals, "l1phi");
  writeValueMap(iEvent, probes, pfPtVals, "pfPt");
  writeValueMap(iEvent, probes, convVtxFitProbVals, "convVtxFitProb");
  writeValueMap(iEvent, probes, kfhitsVals, "kfhits");
  writeValueMap(iEvent, probes, kfchi2Vals, "kfchi2");
  writeValueMap(iEvent, probes, ioemiopVals, "ioemiop");
  writeValueMap(iEvent, probes, ocVals, "5x5circularity");
  writeValueMap(iEvent, probes, hasMatchedConversionVals, "hasMatchedConversion");
  writeValueMap(iEvent, probes, seedGains, "seedGain");
  
  // 存储隔离变量
  writeValueMap(iEvent, probes, miniIsoChgVals, "miniIsoChg");
  writeValueMap(iEvent, probes, miniIsoAllVals, "miniIsoAll");
  writeValueMap(iEvent, probes, pfIsoChgVals, "pfIsoChg");
  writeValueMap(iEvent, probes, pfIsoAllVals, "pfIsoAll");
  writeValueMap(iEvent, probes, pfIsoAll04Vals, "pfIsoAll04");

  // PF lepton isolations (will only work in miniAOD)
  if(isMiniAODformat){
    try {
      auto pfLeptonIsolations = computePfLeptonIsolations(*probes, *pfCandidates);
      for(unsigned int i = 0; i < probes->size(); ++i){
	pfLeptonIsolations[i] /= (*probes)[i].pt();
      }
      writeValueMap(iEvent, probes, pfLeptonIsolations, "pfLeptonIsolation");
    } catch (std::bad_cast const&){
      isMiniAODformat = false;
    }
  }
}

#endif