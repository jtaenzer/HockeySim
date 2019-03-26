import random
import ROOT as r
from array import array
import AtlasStyle as AS


class Visualize:

  def __init__(self, filename, treename, tbranches, option="RECREATE"):
    self.tfile = self.create_TFile(filename,option)
    self.ttree = self.create_TTree(treename,option)
    self.tbranches = self.create_TBranches(tbranches,option)
    self.weight = 1

  def set_weight(self, weight):
    self.weight=weight

  def create_TFile(self, filename, option):
    tf = r.TFile(filename,option)
    if not tf.IsOpen():
      return None
    return tf

  def create_TTree(self, treename="simtree", option="RECREATE"):
    if option=="RECREATE": return r.TTree(treename,treename)
    if option=="READ": return self.tfile.Get(treename)
    return r.TTree(treename,treename)

  def create_TBranches(self,branchlist, option="RECREATE"):
    vardict={}
    for key in branchlist:
      vardict[key]=array('f',[0])
      vardict[key][0]=0
      if option=="RECREATE": self.ttree.Branch(key.replace(" ","_"),vardict[key],key.replace(" ","_")+"/F")
    return vardict

  def fill_TTree(self, entry, result):
    self.ttree.GetEntry(entry)
    for key in self.tbranches:
      self.tbranches[key][0]=result[key]
    self.ttree.Fill()

  def write_TFile(self):
    self.tfile.Write()

  def draw_TGraphs(self, filename):
    graphdict = {}
    for key in self.tbranches:
      graphdict[key]=r.TGraph()
      graphdict[key].SetName(key)

    for i in xrange(self.ttree.GetEntries()):
      for key in self.tbranches:
        self.ttree.GetEntry(i)
        leaf=self.ttree.GetLeaf(key.replace(" ","_"))
        graphdict[key].SetPoint(i,i,leaf.GetValue()*self.weight)

    total=0
    for i in xrange(len(allpoints)): total+=allpoints[i]

    can=r.TCanvas()
    same_str=""
    colors={}
    for key in graphdict:
      graphdict[key].SetMinimum(0.45)
      graphdict[key].SetMaximum(0.6)
      colors[key]=self.select_colour()
      graphdict[key].SetLineColor(colors[key])
      graphdict[key].Draw(same_str)
      same_str="SAME"

    # myLineBoxText is from AtlasStyle -- this reliance on AtlasStyle should be removed, although its handy for now
    counter=0
    for key in graphdict:
      y=0.85-0.04*float(counter)
      AS.myLineBoxText(0.63, y, colors[key], 1, 4, 3004, 0.08, 0.08, key)
      counter+=1

    can.SaveAs(filename)

  def select_colour(self):
    colors = [r.kBlack,r.kRed-4, r.kRed, r.kGreen + 3, r.kGreen - 3, r.kAzure -2, r.kAzure +2, r.kMagenta -2, r.kMagenta+2]
    return random.choice(colors)
