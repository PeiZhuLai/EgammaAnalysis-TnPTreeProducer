#ifndef EgammaIsolationAlgos_isolations_h
#define EgammaIsolationAlgos_isolations_h

#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

#include <Math/VectorUtil.h>

template<class CandidateContainer>
std::vector<float> computePfLeptonIsolations(CandidateContainer const& targetCandidates,
                                             edm::View<reco::Candidate> const& pfCandidates){

  std::vector<float> leptonIsolations(targetCandidates.size());
  for(auto const& pfcand : pfCandidates) {
    auto absPdg = std::abs(pfcand.pdgId());
    auto pfPackedCand = dynamic_cast<const pat::PackedCandidate&>(pfcand);
    if(!(absPdg==11 || absPdg==13) || pfPackedCand.fromPV() < pat::PackedCandidate::PVTight){
      continue;
    }
    for(unsigned int i = 0; i < targetCandidates.size(); ++i) {
      auto dR = std::abs(ROOT::Math::VectorUtil::DeltaR(pfcand.p4(), targetCandidates[i].p4()));
      // lower dR threshold to avoid adding itself
      if (dR <= 0.3 && dR >= 0.0005){
        leptonIsolations[i] += pfcand.p4().pt();
      }
    }
  }

  return leptonIsolations;
}

#endif
// #ifndef EgammaIsolationAlgos_isolations_h
// #define EgammaIsolationAlgos_isolations_h

// #include "DataFormats/PatCandidates/interface/PackedCandidate.h"
// #include "DataFormats/PatCandidates/interface/Electron.h"
// #include "DataFormats/Math/interface/deltaR.h"
// #include <Math/VectorUtil.h>
// #include <cmath>
// #include <vector>

// // 定义结构体来返回所有隔离度变量
// struct IsolationResults {
//     float pfLeptonIsolation;
//     float miniIsoChg;
//     float miniIsoAll;
//     float PFIsoChg;
//     float PFIsoAll;
//     float PFIsoAll04;
// };

// // #https://indico.cern.ch/event/1204275/contributions/5064343/attachments/2529616/4353987/Electron_cutbasedID_preliminaryID.pdf
// // #   (slides 4 to 7)
// // # 
// // #  The effective areas are based on 90% efficient contours
// // #
// // # |eta| min   |eta| max   effective area
// // 0.000        1.000       0.1243
// // 1.000        1.479       0.1458
// // 1.479        2.000       0.0992
// // 2.000        2.200       0.0794
// // 2.200        2.300       0.0762
// // 2.300        2.400       0.0766
// // 2.400        2.500       0.1003
// // Effective Areas for 2022 conditions
// const std::vector<double> etaBins = {0.0, 1.000, 1.479, 2.0, 2.2, 2.3, 2.4, 999.};
// const std::vector<double> effAreaMiniIso = {0.1243,0.1458, 0.0992, 0.0794,  0.0762, 0.0766,0.1003};
// const std::vector<double> effAreaPFIso = {0.1243,0.1458, 0.0992, 0.0794,  0.0762, 0.0766,0.1003};

// // 获取Effective Area的辅助函数
// inline float getEffectiveArea(float eta, const std::vector<double>& effAreas) {
//     eta = std::fabs(eta);
//     for(size_t i = 0; i < etaBins.size() - 1; ++i) {
//         if(eta >= etaBins[i] && eta < etaBins[i+1]) {
//             return effAreas[i];
//         }
//     }
//     return effAreas.back();
// }

// template<class CandidateContainer>
// std::vector<IsolationResults> computeElectronIsolations(
//     CandidateContainer const& targetCandidates,
//     edm::View<reco::Candidate> const& pfCandidates,
//     double rho_MiniIso,
//     double rho_PFIso) {
    
//     std::vector<IsolationResults> results(targetCandidates.size());
    
//     // 首先计算原始的pfLeptonIsolation
//     for(auto const& pfcand : pfCandidates) {
//         auto absPdg = std::abs(pfcand.pdgId());
//         auto pfPackedCand = dynamic_cast<const pat::PackedCandidate&>(pfcand);
//         if(!(absPdg==11 || absPdg==13) || pfPackedCand.fromPV() < pat::PackedCandidate::PVTight){
//             continue;
//         }
//         for(unsigned int i = 0; i < targetCandidates.size(); ++i) {
//             auto dR = std::abs(ROOT::Math::VectorUtil::DeltaR(pfcand.p4(), targetCandidates[i].p4()));
//             if (dR <= 0.3 && dR >= 0.0005){
//                 results[i].pfLeptonIsolation += pfcand.p4().pt();
//             }
//         }
//     }
    
//     // 计算其他隔离度变量
//     for(unsigned int i = 0; i < targetCandidates.size(); ++i) {
//         const auto& electron = targetCandidates[i];
        
//         // 将pfLeptonIsolation转换为相对值
//         results[i].pfLeptonIsolation /= electron.pt();
        
//         // 计算miniPFIsolation (来自pat::Electron的内置方法)
//         auto miniIso = electron.miniPFIsolation();
//         results[i].miniIsoChg = miniIso.chargedHadronIso() / electron.pt();
        
//         float eta = std::fabs(electron.eta());
//         float eaMiniIso = getEffectiveArea(eta, effAreaMiniIso);
        
//         // 计算miniIsoAll (考虑rho修正)
//         float chg = miniIso.chargedHadronIso();
//         float neu = miniIso.neutralHadronIso();
//         float pho = miniIso.photonIso();
        
//         // R因子计算 (与NanoAOD一致)
//         float R = 10.0 / std::min(std::max(electron.pt(), 50.0), 200.0);
//         eaMiniIso *= std::pow(R / 0.3, 2);
        
//         float iso_all = chg + std::max(0.0f, neu + pho - static_cast<float>(rho_MiniIso * eaMiniIso));
//         results[i].miniIsoAll = iso_all / electron.pt();
        
//         // 计算PFIsoChg (dr=0.3)
//         auto pfIso = electron.pfIsolationVariables();
//         results[i].PFIsoChg = pfIso.sumChargedHadronPt / electron.pt();
        
//         // 计算PFIsoAll (dr=0.3)
//         float eaPFIso = getEffectiveArea(eta, effAreaPFIso);
//         float iso_all_pf = pfIso.sumChargedHadronPt + 
//                           std::max(0.0f, pfIso.sumNeutralHadronEt + pfIso.sumPhotonEt - 
//                                   static_cast<float>(rho_PFIso * eaPFIso));
//         results[i].PFIsoAll = iso_all_pf / electron.pt();
        
//         // 计算PFIsoAll04 (dr=0.4)
//         // 注意：electron.chargedHadronIso()等方法是dr=0.4的版本
//         float iso_all_04 = electron.chargedHadronIso() + 
//                           std::max(0.0f, electron.neutralHadronIso() + electron.photonIso() - 
//                                   static_cast<float>(rho_PFIso * eaPFIso * 16.0f / 9.0f));
//         results[i].PFIsoAll04 = iso_all_04 / electron.pt();
//     }
    
//     return results;
// }

// #endif