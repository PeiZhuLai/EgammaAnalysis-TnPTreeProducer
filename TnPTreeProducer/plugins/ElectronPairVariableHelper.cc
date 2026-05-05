#include <cmath>
#include <vector>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/one/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Candidate/interface/ShallowCloneCandidate.h"
#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/PatCandidates/interface/Electron.h"

#include "EgammaAnalysis/TnPTreeProducer/plugins/WriteValueMap.h"

class ElectronPairVariableHelper : public edm::one::EDProducer<> {
 public:
  explicit ElectronPairVariableHelper(const edm::ParameterSet& config)
      : pairsToken_(consumes<edm::View<reco::Candidate>>(config.getParameter<edm::InputTag>("pairs"))) {
    produces<edm::ValueMap<float>>("leadPt");
    produces<edm::ValueMap<float>>("subleadPt");
    produces<edm::ValueMap<float>>("leadScEt");
    produces<edm::ValueMap<float>>("subleadScEt");
  }

  void produce(edm::Event& event, const edm::EventSetup&) override {
    edm::Handle<edm::View<reco::Candidate>> pairs;
    event.getByToken(pairsToken_, pairs);

    std::vector<float> leadPt;
    std::vector<float> subleadPt;
    std::vector<float> leadScEt;
    std::vector<float> subleadScEt;
    leadPt.reserve(pairs->size());
    subleadPt.reserve(pairs->size());
    leadScEt.reserve(pairs->size());
    subleadScEt.reserve(pairs->size());

    for (const auto& pair : *pairs) {
      if (pair.numberOfDaughters() < 2) {
        leadPt.push_back(invalidValue());
        subleadPt.push_back(invalidValue());
        leadScEt.push_back(invalidValue());
        subleadScEt.push_back(invalidValue());
        continue;
      }

      const auto* first = pair.daughter(0);
      const auto* second = pair.daughter(1);
      const bool firstIsLeading = first->pt() >= second->pt();
      const auto* leading = firstIsLeading ? first : second;
      const auto* subleading = firstIsLeading ? second : first;

      leadPt.push_back(leading->pt());
      subleadPt.push_back(subleading->pt());
      leadScEt.push_back(superClusterEt(*leading));
      subleadScEt.push_back(superClusterEt(*subleading));
    }

    writeValueMap(event, pairs, leadPt, "leadPt");
    writeValueMap(event, pairs, subleadPt, "subleadPt");
    writeValueMap(event, pairs, leadScEt, "leadScEt");
    writeValueMap(event, pairs, subleadScEt, "subleadScEt");
  }

 private:
  static float invalidValue() { return -999.f; }

  static const reco::Candidate* masterClone(const reco::Candidate& candidate) {
    const auto* shallowClone = dynamic_cast<const reco::ShallowCloneCandidate*>(&candidate);
    if (shallowClone != nullptr && shallowClone->hasMasterClone()) {
      return shallowClone->masterClone().get();
    }
    return &candidate;
  }

  static float superClusterEt(const reco::Candidate& candidate) {
    const auto* original = masterClone(candidate);
    const auto* patElectron = dynamic_cast<const pat::Electron*>(original);
    if (patElectron != nullptr && patElectron->superCluster().isNonnull()) {
      const auto& position = patElectron->superCluster()->position();
      return patElectron->superCluster()->energy() * std::sin(position.theta());
    }

    const auto* gsfElectron = dynamic_cast<const reco::GsfElectron*>(original);
    if (gsfElectron != nullptr && gsfElectron->superCluster().isNonnull()) {
      const auto& position = gsfElectron->superCluster()->position();
      return gsfElectron->superCluster()->energy() * std::sin(position.theta());
    }

    return invalidValue();
  }

  edm::EDGetTokenT<edm::View<reco::Candidate>> pairsToken_;
};

DEFINE_FWK_MODULE(ElectronPairVariableHelper);
