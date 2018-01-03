SAMPLEFILE BASEDATA
PROJEKTS
  NrOfPro            :  1      & number of projects
  MinJob             :  30      & minimal number of jobs per project
  MaxJob             :  30      & maximal number of jobs per project
  MaxRelDate         :  0      & maximal release date
  DueDateFactor      : 0.0     & maximal due date
MODES
  MinMode            :  1      & minimal number of modes
  MaxMode            :  1      & maximal number of modes
  MinDur             :  1      & minimal duration
  MaxDur             :  10     & maximal duration
NETWORK
  MinOutSource       :  1      & minimal number of start activities per project
  MaxOutSource       :  1      & maximal number of start activities per project
  MaxOut             :  3      & maximal number of successor per activity
  MinInSink          :  1      & minimal number of end activities per project
  MaxInSink          :  1      & maximal number of end activities per project
  MaxIn              :  3      & maximal number of predecessors per activity
  Complexity         :  1.5    & complexity of network
RESSOURCEREQUEST/AVAILABILITY
  Rmin               :  2      & minimal number of renewable resources
  Rmax               :  2      & maximal number of renewable resources
  RminDemand         :  1      & minimal (per period) demand
  RmaxDemand         : 10      & maximal (per period) demand
  RRMin              :  1      & minimal number of resources requested
  RRMax              :  2      & maximal number of resources requested
  RRF                :  0.5    & resource factor
  RRS                :  0.2    & resource strength
  Number R-Func.     :  2
    p1               :  0.0    & probability to choose (duration) constant function
    p2               :  1.0    & probability to choose monotonically decreaseing function
  Nmin               :  2
  Nmax               :  2
  NminDemand         :  1
  NmaxDemand         :  10
  NRMin              :  1
  NRMax              :  2
  NRF                :  1.0
  NRS                :  0.7
  Number N-Func.     :  2
    p1               :  0.0
    p2               :  1.0
  Dmin               :  0
  Dmax               :  0
  DminDemand         :  0
  DmaxDemand         :  0
  DRMin              :  0
  DRMax              :  0
  DRF                :  0.0
  DRST               :  0.0
  DRSP               :  0.0
  Number D-Func.     :  2
    p1               :  1.0
    p2               :  0.0
LIMIT OF ITERATIONS
  Tolerance Network  :  0.05  & tolerated network deviation
  Tolerance RF       :  0.05  & tolerated resource factor deviation

  MaxTrials          :  200   & maximal number of trials randomly gen.



FORMAT OF BASE FILE
  - a colon has to be followed by a value
  - only spaces are allowed between colon and value
  - a commend is allowed to follow a value
  - commends are allowed if there is no colon in
  - value and commend have to be seperated by space
  - value is integer with the exception of
    -> due date factor     -> complexity               -> resource factor
    -> resource strength   -> function probabilities
