#!/usr/bin/env python
import ROOT
import sys

# 启用 FWLite
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.FWLiteEnabler.enable()

# 打开文件
events = ROOT.TChain("Events")
events.Add("root://eospublic.cern.ch//eos/opendata/cms/Run2015D/DoubleEG/MINIAOD/08Jun2016-v1/10000/00387F48-342F-E611-AB5D-0CC47A4D76AC.root")

# 设置分支地址
electrons = ROOT.std.vector("pat::Electron")()
events.SetBranchAddress("recoPatElectrons_slimmedElectrons__RECO.obj", electrons)

# 获取第一个事件
events.GetEntry(0)

if electrons.size() > 0:
    # 获取第一个 electron
    ele = electrons[0]
    
    # 打印基本信息
    print(f"Number of electrons: {electrons.size()}")
    print(f"\nFirst electron properties:")
    print(f"  pt: {ele.pt():.2f}")
    print(f"  eta: {ele.eta():.2f}")
    print(f"  phi: {ele.phi():.2f}")
    print(f"  charge: {ele.charge()}")
    print(f"  electronID: {ele.electronID('cutBasedElectronID-Summer16-80X-V1-loose')}")
    
    # 获取 track 信息
    if ele.gsfTrack().isNonnull():
        track = ele.gsfTrack().get()
        print(f"  track chi2: {track.normalizedChi2():.2f}")
        print(f"  track hits: {track.hitPattern().numberOfValidHits()}")
    
    # 获取 supercluster 信息
    if ele.superCluster().isNonnull():
        sc = ele.superCluster().get()
        print(f"  supercluster energy: {sc.energy():.2f}")
        print(f"  supercluster eta: {sc.eta():.2f}")
    
    # 获取所有可用的 electron IDs
    print("\nAvailable electron IDs:")
    id_names = ele.electronIDs()
    for id_pair in id_names:
        print(f"  - {id_pair.first}")
    
    # 打印更多通用信息
    print("\nOther available information:")
    print(f"  isEB: {ele.isEB()}")
    print(f"  isEE: {ele.isEE()}")
    print(f"  isGap: {ele.isGap()}")
    print(f"  dB: {ele.dB():.4f}")
    print(f"  edB: {ele.edB():.4f}")
    print(f"  userIso: {ele.userIso():.2f}")
    print(f"  pfIsolationVariables:")
    iso = ele.pfIsolationVariables()
    print(f"    sumChargedHadronPt: {iso.sumChargedHadronPt:.2f}")
    print(f"    sumNeutralHadronEt: {iso.sumNeutralHadronEt:.2f}")
    print(f"    sumPhotonEt: {iso.sumPhotonEt:.2f}")
    print(f"    sumPUPt: {iso.sumPUPt:.2f}")

else:
    print("No electrons in this event")  