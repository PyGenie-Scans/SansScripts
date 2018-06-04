from ISISCommandInterface import MaskFile, AddRuns, AssignSample, AssignCan
from ISISCommandInterface import TransmissionSample, TransmissionCan
from ISISCommandInterface import WavRangeReduction
MaskFile('Mask.txt')
#  polar bear p1 along hairs
#  Error: Missing transmission information
#  polar bear p2 along hairs
#  Error: Missing transmission information
#  polar bear p1 across hairs
sample = AddRuns([29284])
AssignSample(sample)
trans = AddRuns([29283])
TransmissionSample(trans,23000)
can = AddRuns([29280, 29286])
AssignCan(can)
can_tr = AddRuns([29285])
TransmissionCan(can_tr,23000)
WavRangeReduction(3, 9)
#  silica in pure h2o
sample = AddRuns([29288, 29292, 29295, 29298, 29301, 29304, 29307])
AssignSample(sample)
trans = AddRuns([29287])
TransmissionSample(trans,23000)
can = AddRuns([29290, 29293, 29296, 29299, 29302, 29305, 29308])
AssignCan(can)
can_tr = AddRuns([29289])
TransmissionCan(can_tr,23000)
WavRangeReduction(3, 9)
#  polar bear p2 across hairs
sample = AddRuns([29282])
AssignSample(sample)
trans = AddRuns([29281])
TransmissionSample(trans,23000)
can = AddRuns([29280, 29286])
AssignCan(can)
can_tr = AddRuns([29285])
TransmissionCan(can_tr,23000)
WavRangeReduction(3, 9)
#  dio solution 23 1mm cell
#  Error: Missing transmission information
