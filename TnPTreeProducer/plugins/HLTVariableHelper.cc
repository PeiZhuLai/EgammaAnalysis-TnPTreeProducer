#include "HLTVariableHelper.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/PatCandidates/interface/Electron.h"

typedef  HLTVariableHelper<pat::Electron> PatElectronHLTVariableHelper;
DEFINE_FWK_MODULE(PatElectronHLTVariableHelper);

typedef  HLTVariableHelper<reco::GsfElectron> GsfElectronHLTVariableHelper;
DEFINE_FWK_MODULE(GsfElectronHLTVariableHelper);

//=============================================================================
// 完全模仿 PatElectronTriggerCandProducer 的 HLT ΔR 计算模块
// 只输出指定过滤器的最小ΔR，而不进行对象筛选
//=============================================================================

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/one/EDProducer.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HLTReco/interface/TriggerObject.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/Photon.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/RecoCandidate/interface/RecoEcalCandidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "EgammaAnalysis/TnPTreeProducer/plugins/WriteValueMap.h"

#include <string>
#include <vector>
#include <map>
#include <iostream>  // 添加用于debug输出

//=============================================================================
// 针对 pat::Electron 的 ΔR 计算模块 - 使用 pat::TriggerObjectStandAlone
// 完全模仿 PatElectronTriggerCandProducer 的逻辑
//=============================================================================
class PatElectronHLTDRHelper : public edm::one::EDProducer<> {
public:
  explicit PatElectronHLTDRHelper(const edm::ParameterSet& iConfig);
  virtual ~PatElectronHLTDRHelper() {}
  
  virtual void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override;

private:
  bool matchElectronWithFilter(const pat::Electron& electron, 
                               const pat::TriggerObjectStandAloneCollection& triggerObjects,
                               const std::string& filterLabel,
                               const edm::Handle<edm::TriggerResults>& triggerBits,
                               const edm::TriggerNames& triggerNames,
                               edm::Event& iEvent,
                               float& minDR);

  edm::EDGetTokenT<std::vector<pat::Electron>> probesToken_;
  edm::EDGetTokenT<edm::TriggerResults> triggerBitsToken_;
  edm::EDGetTokenT<pat::TriggerObjectStandAloneCollection> triggerObjectsToken_;
  std::string filterLabel_;
  std::string outputDRName_;
  double dRMatch_;
  bool useSuperCluster_;  // 是否使用superCluster位置（原始代码中使用）
  bool debug_;  // debug标志
  
  edm::ParameterSetID triggerNamesID_;
  std::map<std::string, unsigned int> trigger_indices;
};

PatElectronHLTDRHelper::PatElectronHLTDRHelper(const edm::ParameterSet& iConfig) :
  probesToken_(consumes<std::vector<pat::Electron>>(iConfig.getParameter<edm::InputTag>("probes"))),
  triggerBitsToken_(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerBits"))),
  triggerObjectsToken_(consumes<pat::TriggerObjectStandAloneCollection>(iConfig.getParameter<edm::InputTag>("triggerObjects"))),
  filterLabel_(iConfig.getParameter<std::string>("filterLabel")),
  outputDRName_(iConfig.getUntrackedParameter<std::string>("outputDRName", "hltDR")),
  dRMatch_(iConfig.getParameter<double>("dR")),
  useSuperCluster_(iConfig.getUntrackedParameter<bool>("useSuperCluster", true)),
  debug_(iConfig.getUntrackedParameter<bool>("debug", false))  // 默认关闭debug
{
  produces<edm::ValueMap<float>>(outputDRName_);
}

void PatElectronHLTDRHelper::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  edm::Handle<std::vector<pat::Electron>> probes;
  iEvent.getByToken(probesToken_, probes);

  edm::Handle<edm::TriggerResults> triggerBits;
  iEvent.getByToken(triggerBitsToken_, triggerBits);

  edm::Handle<pat::TriggerObjectStandAloneCollection> triggerObjects;
  iEvent.getByToken(triggerObjectsToken_, triggerObjects);

  // DEBUG: 输出trigger objects数量
  if (debug_) {
    if (triggerObjects.isValid()) {
      std::cout << "=== PatElectronHLTDRHelper Debug ===" << std::endl;
      std::cout << "Event: " << iEvent.id().run() << ":" << iEvent.id().luminosityBlock() << ":" << iEvent.id().event() << std::endl;
      std::cout << "Number of trigger objects: " << triggerObjects->size() << std::endl;
      std::cout << "Filter label: " << filterLabel_ << std::endl;
    } else {
      std::cout << "PatElectronHLTDRHelper: TriggerObjects product not valid!" << std::endl;
    }
  }

  std::vector<float> dRValues(probes->size(), 9);

  if (!triggerBits.isValid()) {
    edm::LogWarning("PatElectronHLTDRHelper") << "TriggerResults product not found";
    writeValueMap(iEvent, probes, dRValues, outputDRName_);
    return;
  }

  if (!triggerObjects.isValid()) {
    edm::LogWarning("PatElectronHLTDRHelper") << "TriggerObjects product not found";
    writeValueMap(iEvent, probes, dRValues, outputDRName_);
    return;
  }

  // 获取trigger names
  const edm::TriggerNames& triggerNames = iEvent.triggerNames(*triggerBits);

  // 对每个电子计算与指定过滤器的最小ΔR
  for (size_t i = 0; i < probes->size(); ++i) {
    const auto& probe = (*probes)[i];
    float minDR = 9;
    
    bool matched = matchElectronWithFilter(probe, *triggerObjects, filterLabel_, 
                                          triggerBits, triggerNames, iEvent, minDR);
    
    if (matched) {
      dRValues[i] = minDR;
    }
    // 如果没有匹配，保持9999
  }

  writeValueMap(iEvent, probes, dRValues, outputDRName_);
}

bool PatElectronHLTDRHelper::matchElectronWithFilter(
    const pat::Electron& electron,
    const pat::TriggerObjectStandAloneCollection& triggerObjects,
    const std::string& filterLabel,
    const edm::Handle<edm::TriggerResults>& triggerBits,
    const edm::TriggerNames& triggerNames,
    edm::Event& iEvent,
    float& minDR) {
  
  bool found = false;
  minDR = 9;
  
  // 获取电子位置（使用superCluster或直接使用eta/phi）
  float eleEta, elePhi;
  if (useSuperCluster_ && electron.superCluster().isNonnull()) {
    eleEta = electron.superCluster()->eta();
    elePhi = electron.superCluster()->phi();
  } else {
    eleEta = electron.eta();
    elePhi = electron.phi();
  }
  
  // 遍历所有trigger objects，查找属于指定过滤器的对象
  for (pat::TriggerObjectStandAlone obj : triggerObjects) {
    // 关键步骤：解包path names和filter labels
    obj.unpackPathNames(triggerNames);
    obj.unpackFilterLabels(iEvent, *triggerBits);
    
    // 检查是否属于指定的过滤器
    if (obj.hasFilterLabel(filterLabel)) {
      // 计算ΔR
      float dR = deltaR(eleEta, elePhi, obj.eta(), obj.phi());
      
      // 如果ΔR小于阈值，记录最小值
      if (dR < dRMatch_) {
        found = true;
        if (dR < minDR) {
          minDR = dR;
        }
      }
    }
  }
  
  return found;
}

//=============================================================================
// 针对 reco::GsfElectron 的 ΔR 计算模块 - 使用 trigger::TriggerEvent
// 完全模仿 GsfElectronTriggerCandProducer 的逻辑
//=============================================================================
class GsfElectronHLTDRHelper : public edm::one::EDProducer<> {
public:
  explicit GsfElectronHLTDRHelper(const edm::ParameterSet& iConfig);
  virtual ~GsfElectronHLTDRHelper() {}
  
  virtual void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override;

private:
  bool matchElectronWithFilter(const reco::GsfElectron& electron,
                               const trigger::TriggerEvent& triggerEvent,
                               const std::string& filterLabel,
                               float& minDR);

  edm::EDGetTokenT<std::vector<reco::GsfElectron>> probesToken_;
  edm::EDGetTokenT<edm::TriggerResults> triggerBitsToken_;
  edm::EDGetTokenT<trigger::TriggerEvent> triggerEventToken_;
  std::string filterLabel_;
  std::string outputDRName_;
  double dRMatch_;
  bool debug_;  // debug标志
  
  edm::ParameterSetID triggerNamesID_;
  std::map<std::string, unsigned int> trigger_indices;
};

GsfElectronHLTDRHelper::GsfElectronHLTDRHelper(const edm::ParameterSet& iConfig) :
  probesToken_(consumes<std::vector<reco::GsfElectron>>(iConfig.getParameter<edm::InputTag>("probes"))),
  triggerBitsToken_(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerBits"))),
  triggerEventToken_(consumes<trigger::TriggerEvent>(iConfig.getParameter<edm::InputTag>("triggerEvent"))),
  filterLabel_(iConfig.getParameter<std::string>("filterLabel")),
  outputDRName_(iConfig.getUntrackedParameter<std::string>("outputDRName", "hltDR")),
  dRMatch_(iConfig.getParameter<double>("dR")),
  debug_(iConfig.getUntrackedParameter<bool>("debug", false))
{
  produces<edm::ValueMap<float>>(outputDRName_);
}

void GsfElectronHLTDRHelper::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  edm::Handle<std::vector<reco::GsfElectron>> probes;
  iEvent.getByToken(probesToken_, probes);

  edm::Handle<edm::TriggerResults> triggerBits;
  iEvent.getByToken(triggerBitsToken_, triggerBits);

  edm::Handle<trigger::TriggerEvent> triggerEvent;
  iEvent.getByToken(triggerEventToken_, triggerEvent);

  // DEBUG: 输出trigger objects数量
  if (debug_) {
    if (triggerEvent.isValid()) {
      const trigger::TriggerObjectCollection& triggerObjects = triggerEvent->getObjects();
      std::cout << "=== GsfElectronHLTDRHelper Debug ===" << std::endl;
      std::cout << "Event: " << iEvent.id().run() << ":" << iEvent.id().luminosityBlock() << ":" << iEvent.id().event() << std::endl;
      std::cout << "Number of trigger objects: " << triggerObjects.size() << std::endl;
      std::cout << "Number of filters: " << triggerEvent->sizeFilters() << std::endl;
      std::cout << "Filter label: " << filterLabel_ << std::endl;
      
      // 额外输出指定过滤器的对象数量
      unsigned int filterIndex = 9999;
      for (unsigned int i = 0; i < triggerEvent->sizeFilters(); ++i) {
        if (triggerEvent->filterLabel(i) == filterLabel_) {
          filterIndex = i;
          break;
        }
      }
      if (filterIndex < triggerEvent->sizeFilters()) {
        const trigger::Keys& keys = triggerEvent->filterKeys(filterIndex);
        std::cout << "Objects in filter " << filterLabel_ << ": " << keys.size() << std::endl;
      } else {
        std::cout << "Filter " << filterLabel_ << " not found!" << std::endl;
      }
    } else {
      std::cout << "GsfElectronHLTDRHelper: TriggerEvent product not valid!" << std::endl;
    }
  }

  std::vector<float> dRValues(probes->size(), 9);

  if (!triggerBits.isValid()) {
    edm::LogWarning("GsfElectronHLTDRHelper") << "TriggerResults product not found";
    writeValueMap(iEvent, probes, dRValues, outputDRName_);
    return;
  }

  if (!triggerEvent.isValid()) {
    edm::LogWarning("GsfElectronHLTDRHelper") << "TriggerEvent product not found";
    writeValueMap(iEvent, probes, dRValues, outputDRName_);
    return;
  }

  // 对每个电子计算与指定过滤器的最小ΔR
  for (size_t i = 0; i < probes->size(); ++i) {
    const auto& probe = (*probes)[i];
    float minDR = 9;
    
    bool matched = matchElectronWithFilter(probe, *triggerEvent, filterLabel_, minDR);
    
    if (matched) {
      dRValues[i] = minDR;
    }
  }

  writeValueMap(iEvent, probes, dRValues, outputDRName_);
}

bool GsfElectronHLTDRHelper::matchElectronWithFilter(
    const reco::GsfElectron& electron,
    const trigger::TriggerEvent& triggerEvent,
    const std::string& filterLabel,
    float& minDR) {
  
  bool found = false;
  minDR = 9;
  
  // 查找过滤器的索引
  unsigned int filterIndex = 9999;
  for (unsigned int i = 0; i < triggerEvent.sizeFilters(); ++i) {
    if (triggerEvent.filterLabel(i) == filterLabel) {
      filterIndex = i;
      break;
    }
  }
  
  // 如果没找到过滤器
  if (filterIndex >= triggerEvent.sizeFilters()) {
    return false;
  }
  
  // 获取该过滤器的对象keys
  const trigger::Keys& keys = triggerEvent.filterKeys(filterIndex);
  if (keys.empty()) {
    return false;
  }
  
  // 获取所有trigger objects
  const trigger::TriggerObjectCollection& triggerObjects = triggerEvent.getObjects();
  
  // 使用superCluster位置（原始代码中GsfElectron使用superCluster）
  float eleEta = electron.superCluster()->eta();
  float elePhi = electron.superCluster()->phi();
  
  // 只遍历属于该过滤器的对象
  for (const auto& key : keys) {
    if (key < triggerObjects.size()) {
      const trigger::TriggerObject& obj = triggerObjects[key];
      
      // 计算ΔR
      float dR = deltaR(eleEta, elePhi, obj.eta(), obj.phi());
      
      // 如果ΔR小于阈值，记录最小值
      if (dR < dRMatch_) {
        found = true;
        if (dR < minDR) {
          minDR = dR;//这里是赋值，返回的是minDR的值，如果没通过这个值9。另一个类里(PatElectronTriggerCandProducer)那里是不需要这个值，只需要pass或不pass
        }
      }
    }
  }
  
  return found;
}

//=============================================================================  
// 针对 pat::Electron 的 HLT路径ΔR计算模块  
//=============================================================================  
//=============================================================================  
// 针对 pat::Electron 的 HLT路径ΔR计算模块  
//=============================================================================  
class PatElectronHLTPathDRHelper : public edm::one::EDProducer<> {  
public:  
  explicit PatElectronHLTPathDRHelper(const edm::ParameterSet& iConfig);  
  virtual ~PatElectronHLTPathDRHelper() {}  
    
  virtual void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override;  
  
private:  
  struct TriggerObjectWithPt {  
    pat::TriggerObjectStandAlone obj;  
    float pt;  
    float eta;  
    float phi;  
  };  
    
  bool matchElectronWithPathLeg(const pat::Electron& electron,  
                                const std::vector<pat::TriggerObjectStandAlone>& triggerObjects,  
                                const std::string& hltPath,  
                                const edm::Handle<edm::TriggerResults>& triggerBits,  
                                const edm::TriggerNames& triggerNames,  
                                edm::Event& iEvent,  
                                int legIndex,  
                                float& minDR,
                                std::string& matchedPathName);  // 新增：返回匹配的路径名
  
  edm::EDGetTokenT<std::vector<pat::Electron>> probesToken_;  
  edm::EDGetTokenT<edm::TriggerResults> triggerBitsToken_;  
  edm::EDGetTokenT<pat::TriggerObjectStandAloneCollection> triggerObjectsToken_;  
  std::string hltPath_;  
  std::string outputDRNameLeg1_;  
  std::string outputDRNameLeg2_;  
  double dRMatch_;  
  bool useSuperCluster_;  
  bool debug_;  
};  
  
PatElectronHLTPathDRHelper::PatElectronHLTPathDRHelper(const edm::ParameterSet& iConfig) :  
  probesToken_(consumes<std::vector<pat::Electron>>(iConfig.getParameter<edm::InputTag>("probes"))),  
  triggerBitsToken_(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerBits"))),  
  triggerObjectsToken_(consumes<pat::TriggerObjectStandAloneCollection>(iConfig.getParameter<edm::InputTag>("triggerObjects"))),  
  hltPath_(iConfig.getParameter<std::string>("hltPath")),  
  outputDRNameLeg1_(iConfig.getUntrackedParameter<std::string>("outputDRNameLeg1", "hltLeg1DR")),  
  outputDRNameLeg2_(iConfig.getUntrackedParameter<std::string>("outputDRNameLeg2", "hltLeg2DR")),  
  dRMatch_(iConfig.getParameter<double>("dR")),  
  useSuperCluster_(iConfig.getUntrackedParameter<bool>("useSuperCluster", true)),  
  debug_(iConfig.getUntrackedParameter<bool>("debug", false))  
{  
  produces<edm::ValueMap<float>>(outputDRNameLeg1_);  
  produces<edm::ValueMap<float>>(outputDRNameLeg2_);  
}  
  
void PatElectronHLTPathDRHelper::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {  
  edm::Handle<std::vector<pat::Electron>> probes;  
  iEvent.getByToken(probesToken_, probes);  
  
  // Initialize with default values  
  std::vector<float> dRValuesLeg1(probes->size(), 9);  
  std::vector<float> dRValuesLeg2(probes->size(), 9);  
  
  // Always produce the ValueMaps, even if inputs are missing  
  if (!probes.isValid()) {  
    edm::LogWarning("PatElectronHLTPathDRHelper") << "Probes product not found";  
    writeValueMap(iEvent, probes, dRValuesLeg1, outputDRNameLeg1_);  
    writeValueMap(iEvent, probes, dRValuesLeg2, outputDRNameLeg2_);  
    return;  
  }  
  
  edm::Handle<edm::TriggerResults> triggerBits;  
  iEvent.getByToken(triggerBitsToken_, triggerBits);  
  
  edm::Handle<pat::TriggerObjectStandAloneCollection> triggerObjects;  
  iEvent.getByToken(triggerObjectsToken_, triggerObjects);  
  
  // Debug output  
  if (debug_) {  
    std::cout << "=== PatElectronHLTPathDRHelper Debug ===" << std::endl;  
    std::cout << "Event: " << iEvent.id().run() << ":" << iEvent.id().luminosityBlock() << ":" << iEvent.id().event() << std::endl;  
    std::cout << "HLT Path pattern: " << hltPath_ << std::endl;  
    std::cout << "Probes: " << probes->size() << std::endl;  
      
    if (triggerObjects.isValid()) {  
      std::cout << "Trigger objects: " << triggerObjects->size() << std::endl;  
    }  
    if (triggerBits.isValid()) {  
      const edm::TriggerNames& triggerNames = iEvent.triggerNames(*triggerBits);  
      std::cout << "Trigger paths: " << triggerNames.size() << std::endl;  
        
      // Output only HLT_Ele* paths
      std::cout << "\n=== HLT_Ele* Paths ===" << std::endl;
      int elePathCount = 0;
      for (unsigned int i = 0; i < triggerNames.size(); ++i) {
        std::string pathName = triggerNames.triggerName(i);
        if (pathName.find("HLT_Ele") == 0) {  // 只输出以 HLT_Ele 开头的路径
          std::cout << "  [" << i << "] " << pathName << std::endl;
          elePathCount++;
        }
      }
      if (elePathCount == 0) {
        std::cout << "  No HLT_Ele* paths found" << std::endl;
      }
    }  
  }
  
  // Process only if all inputs are valid  
  if (triggerBits.isValid() && triggerObjects.isValid()) {  
    const edm::TriggerNames& triggerNames = iEvent.triggerNames(*triggerBits);  
      
    // Check if HLT path exists  
    bool pathFound = false;  
    std::string actualPathName;  // 存储实际匹配的路径名
    
    // 从模式中提取基础路径名（去掉_v*）
    std::string basePath = hltPath_;
    size_t vstarPos = basePath.find("_v*");
    if (vstarPos != std::string::npos) {
      basePath = basePath.substr(0, vstarPos);
    }
    
    for (unsigned int i = 0; i < triggerNames.size(); ++i) {  
      std::string pathName = triggerNames.triggerName(i);  
      
      // 检查是否以 basePath 开头，但不包含 "_DZ_"
      if (pathName.find(basePath) == 0) {
        // 确保路径名中不包含 "_DZ_"
        if (pathName.find("_DZ_") == std::string::npos) {
          pathFound = true;  
          actualPathName = pathName;  // 保存实际路径名
          if (debug_) {  
            std::cout << "Found matching path (without DZ): " << pathName << std::endl;  
          }  
          break;
        } else if (debug_) {
          std::cout << "Skipping path with DZ: " << pathName << std::endl;
        }
      }
    }  
    
    if (pathFound) {  
      // 使用 actualPathName 进行匹配，而不是 hltPath_
      for (size_t i = 0; i < probes->size(); ++i) {  
        const auto& probe = (*probes)[i];  
        float minDRLeg1 = 9;  
        float minDRLeg2 = 9;  
        std::string matchedPathLeg1, matchedPathLeg2;
        
        bool matchedLeg1 = matchElectronWithPathLeg(probe, *triggerObjects, actualPathName,   
                                                    triggerBits, triggerNames, iEvent, 1, minDRLeg1, matchedPathLeg1);  
        bool matchedLeg2 = matchElectronWithPathLeg(probe, *triggerObjects, actualPathName,   
                                                    triggerBits, triggerNames, iEvent, 2, minDRLeg2, matchedPathLeg2);  
          
        if (matchedLeg1) {  
          dRValuesLeg1[i] = minDRLeg1;  
        }  
        if (matchedLeg2) {  
          dRValuesLeg2[i] = minDRLeg2;  
        }  
      }  
    } else if (debug_) {  
      std::cout << "No matching HLT path found for pattern: " << hltPath_ << " (without DZ)" << std::endl;  
    }  
  } else {  
    edm::LogWarning("PatElectronHLTPathDRHelper") << "Trigger products not valid";  
  }  
  
  // Always write the ValueMaps  
  writeValueMap(iEvent, probes, dRValuesLeg1, outputDRNameLeg1_);  
  writeValueMap(iEvent, probes, dRValuesLeg2, outputDRNameLeg2_);  
}  
  
bool PatElectronHLTPathDRHelper::matchElectronWithPathLeg(  
    const pat::Electron& electron,  
    const std::vector<pat::TriggerObjectStandAlone>& triggerObjects,  
    const std::string& hltPath,  
    const edm::Handle<edm::TriggerResults>& triggerBits,  
    const edm::TriggerNames& triggerNames,  
    edm::Event& iEvent,  
    int legIndex,  
    float& minDR,
    std::string& matchedPathName) {  
    
  bool found = false;  
  minDR = 9;  
  matchedPathName = hltPath;  // 使用传入的实际路径名
    
  // Collect trigger objects belonging to the HLT path  
  std::vector<TriggerObjectWithPt> pathObjects;  
    
  for (pat::TriggerObjectStandAlone obj : triggerObjects) {  
    obj.unpackPathNames(triggerNames);  
    obj.unpackFilterLabels(iEvent, *triggerBits);  
      
    // Check if object belongs to the specified HLT path (精确匹配，因为现在传入的是实际路径名)
    if (obj.hasPathName(hltPath, true, true)) {  
      TriggerObjectWithPt objWithPt;  
      objWithPt.obj = obj;  
      objWithPt.pt = obj.pt();  
      objWithPt.eta = obj.eta();  
      objWithPt.phi = obj.phi();  
      pathObjects.push_back(objWithPt);  
    }  
  }  
  
  if (debug_ && legIndex == 1) {  
    std::cout << "HLT Path: " << hltPath << " - Trigger objects 1 in path: " << pathObjects.size() << std::endl;
  }
  if (debug_ && legIndex == 2) {  
    std::cout << "HLT Path: " << hltPath << " - Trigger objects 2 in path: " << pathObjects.size() << std::endl;
  }
  if (pathObjects.empty()) {  
    return false;  
  }  
    
  // Sort by pt (ascending)  
  std::sort(pathObjects.begin(), pathObjects.end(),   
            [](const TriggerObjectWithPt& a, const TriggerObjectWithPt& b) {  
              return a.pt < b.pt;  
            });  
    
  // Select target object based on legIndex  
  std::vector<TriggerObjectWithPt> targetObjects;  
    
  if (legIndex == 1) {  
    // leg1: lowest pt  
    targetObjects.push_back(pathObjects[0]);  
  } else if (legIndex == 2) {  
    // leg2: highest pt  
    targetObjects.push_back(pathObjects[pathObjects.size() - 1]);  
  } else {  
    return false;  
  }  
    
  // Get electron position  
  float eleEta, elePhi;  
  if (useSuperCluster_ && electron.superCluster().isNonnull()) {  
    eleEta = electron.superCluster()->eta();  
    elePhi = electron.superCluster()->phi();  
  } else {  
    eleEta = electron.eta();  
    elePhi = electron.phi();  
  }  
    
  // Calculate ΔR with target trigger objects  
  for (const auto& targetObj : targetObjects) {  
    float dR = deltaR(eleEta, elePhi, targetObj.eta, targetObj.phi);  
      
    if (dR < dRMatch_) {  
      found = true;  
      if (dR < minDR) {  
        minDR = dR;  
      }  
    }  
  }  
    
  return found;  
}
//=============================================================================
// 针对 reco::GsfElectron 的 HLT路径ΔR计算模块
//=============================================================================
class GsfElectronHLTPathDRHelper : public edm::one::EDProducer<> {
public:
  explicit GsfElectronHLTPathDRHelper(const edm::ParameterSet& iConfig);
  virtual ~GsfElectronHLTPathDRHelper() {}
  
  virtual void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override;

private:
  struct TriggerObjectWithPt {
    trigger::TriggerObject obj;
    float pt;
    float eta;
    float phi;
  };
  
  bool matchElectronWithPathLeg(const reco::GsfElectron& electron,
                                const trigger::TriggerEvent& triggerEvent,
                                const std::string& hltPath,
                                int legIndex,
                                float& minDR);

  edm::EDGetTokenT<std::vector<reco::GsfElectron>> probesToken_;
  edm::EDGetTokenT<edm::TriggerResults> triggerBitsToken_;
  edm::EDGetTokenT<trigger::TriggerEvent> triggerEventToken_;
  std::string hltPath_;
  std::string outputDRNameLeg1_;
  std::string outputDRNameLeg2_;
  double dRMatch_;
  bool debug_;
};

GsfElectronHLTPathDRHelper::GsfElectronHLTPathDRHelper(const edm::ParameterSet& iConfig) :
  probesToken_(consumes<std::vector<reco::GsfElectron>>(iConfig.getParameter<edm::InputTag>("probes"))),
  triggerBitsToken_(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerBits"))),
  triggerEventToken_(consumes<trigger::TriggerEvent>(iConfig.getParameter<edm::InputTag>("triggerEvent"))),
  hltPath_(iConfig.getParameter<std::string>("hltPath")),
  outputDRNameLeg1_(iConfig.getUntrackedParameter<std::string>("outputDRNameLeg1", "hltLeg1DR")),
  outputDRNameLeg2_(iConfig.getUntrackedParameter<std::string>("outputDRNameLeg2", "hltLeg2DR")),
  dRMatch_(iConfig.getParameter<double>("dR")),
  debug_(iConfig.getUntrackedParameter<bool>("debug", false))
{
  produces<edm::ValueMap<float>>(outputDRNameLeg1_);
  produces<edm::ValueMap<float>>(outputDRNameLeg2_);
}

void GsfElectronHLTPathDRHelper::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  edm::Handle<std::vector<reco::GsfElectron>> probes;
  iEvent.getByToken(probesToken_, probes);

  edm::Handle<edm::TriggerResults> triggerBits;
  iEvent.getByToken(triggerBitsToken_, triggerBits);

  edm::Handle<trigger::TriggerEvent> triggerEvent;
  iEvent.getByToken(triggerEventToken_, triggerEvent);

  // DEBUG: 输出trigger objects数量
  if (debug_) {
    if (triggerEvent.isValid() && triggerBits.isValid()) {
      const trigger::TriggerObjectCollection& triggerObjects = triggerEvent->getObjects();
      const edm::TriggerNames& triggerNames = iEvent.triggerNames(*triggerBits);
      
      std::cout << "=== GsfElectronHLTPathDRHelper Debug ===" << std::endl;
      std::cout << "Event: " << iEvent.id().run() << ":" << iEvent.id().luminosityBlock() << ":" << iEvent.id().event() << std::endl;
      std::cout << "HLT Path: " << hltPath_ << std::endl;
      std::cout << "Total trigger objects: " << triggerObjects.size() << std::endl;
      
      // 检查HLT路径是否存在并已触发
      bool pathFound = false;
      bool pathAccepted = false;
      for (unsigned int i = 0; i < triggerNames.size(); ++i) {
        if (triggerNames.triggerName(i).find(hltPath_) != std::string::npos) {
          pathFound = true;
          pathAccepted = triggerBits->accept(i);
          std::cout << "Found path: " << triggerNames.triggerName(i) << ", accept: " << pathAccepted << std::endl;
          break;
        }
      }
      
      // 注意：trigger::TriggerEvent不直接支持按路径名查询对象
      // 这里只能输出总数
      if (!pathFound) { std::cout << "HLT path " << hltPath_ << " not found in this event!" << std::endl;
      }
      std::cout << "Note: trigger::TriggerEvent doesn't support direct path-based query" << std::endl;
    }
  }

  std::vector<float> dRValuesLeg1(probes->size(), 9);
  std::vector<float> dRValuesLeg2(probes->size(), 9);

  if (!triggerBits.isValid() || !triggerEvent.isValid()) {
    edm::LogWarning("GsfElectronHLTPathDRHelper") << "Trigger products not found";
    writeValueMap(iEvent, probes, dRValuesLeg1, outputDRNameLeg1_);
    writeValueMap(iEvent, probes, dRValuesLeg2, outputDRNameLeg2_);
    return;
  }

  // 对每个电子计算与路径两个leg的ΔR
  for (size_t i = 0; i < probes->size(); ++i) {
    const auto& probe = (*probes)[i];
    float minDRLeg1 = 9;
    float minDRLeg2 = 9;
    
    bool matchedLeg1 = matchElectronWithPathLeg(probe, *triggerEvent, hltPath_, 1, minDRLeg1);
    bool matchedLeg2 = matchElectronWithPathLeg(probe, *triggerEvent, hltPath_, 2, minDRLeg2);
    
    if (matchedLeg1) {
      dRValuesLeg1[i] = minDRLeg1;
    }
    if (matchedLeg2) {
      dRValuesLeg2[i] = minDRLeg2;
    }
  }

  writeValueMap(iEvent, probes, dRValuesLeg1, outputDRNameLeg1_);
  writeValueMap(iEvent, probes, dRValuesLeg2, outputDRNameLeg2_);
}

bool GsfElectronHLTPathDRHelper::matchElectronWithPathLeg(
    const reco::GsfElectron& electron,
    const trigger::TriggerEvent& triggerEvent,
    const std::string& hltPath,
    int legIndex,
    float& minDR) {
  
  bool found = false;
  minDR = 9;
  
  // 对于GsfElectron，我们无法直接从trigger::TriggerEvent中按路径筛选对象
  // 这里简化处理：使用所有trigger objects，但按pt排序来模拟leg1/leg2
  // 注意：这不是精确匹配，但可以作为一种近似
  
  const trigger::TriggerObjectCollection& triggerObjects = triggerEvent.getObjects();
  
  if (triggerObjects.empty()) {
    return false;
  }
  
  // 收集所有trigger objects并按pt排序
  std::vector<TriggerObjectWithPt> allObjects;
  for (size_t i = 0; i < triggerObjects.size(); ++i) {
    TriggerObjectWithPt objWithPt;
    objWithPt.obj = triggerObjects[i];
    objWithPt.pt = triggerObjects[i].pt();
    objWithPt.eta = triggerObjects[i].eta();
    objWithPt.phi = triggerObjects[i].phi();
    allObjects.push_back(objWithPt);
  }
  
  // 按pt排序（升序）
  std::sort(allObjects.begin(), allObjects.end(), 
            [](const TriggerObjectWithPt& a, const TriggerObjectWithPt& b) {
              return a.pt < b.pt;
            });
  
  // 根据legIndex选择要匹配的对象
  std::vector<TriggerObjectWithPt> targetObjects;
  
  if (legIndex == 1) {
    // leg1: 最低pt
    targetObjects.push_back(allObjects[0]);
  } else if (legIndex == 2) {
    // leg2: 最高pt
    targetObjects.push_back(allObjects[allObjects.size() - 1]);
  } else {
    return false;
  }
  
  // 使用superCluster位置
  float eleEta = electron.superCluster()->eta();
  float elePhi = electron.superCluster()->phi();
  
  // 计算与目标trigger objects的ΔR
  for (const auto& targetObj : targetObjects) {
    float dR = deltaR(eleEta, elePhi, targetObj.eta, targetObj.phi);
    
    if (dR < dRMatch_) {
      found = true;
      if (dR < minDR) {
        minDR = dR;
      }
    }
  }
  
  return found;
}

//=============================================================================
// 定义模块
//=============================================================================
DEFINE_FWK_MODULE(PatElectronHLTDRHelper);
DEFINE_FWK_MODULE(GsfElectronHLTDRHelper);
DEFINE_FWK_MODULE(PatElectronHLTPathDRHelper);
DEFINE_FWK_MODULE(GsfElectronHLTPathDRHelper);