{********************************************************************}
{***** typdeclarationen                                         *****}
{********************************************************************}

UNIT TypeDecl;

INTERFACE


USES CRT,DOS;

{********************************************************************}
{**** constants for determining the size of arrays             ******}
{********************************************************************}

CONST duMax      =    15; {maximal duration                              }
      RMax       =     6; {maximal number renewable resources            }
      DMax       =     4; {maximal number doubly constrained resources   }
      NMax       =     5; {maximal number nonrenewable resources         }
      RDNMax     =    15; { max(RMax,Dmax,Nmax)                          }
      MMax       =    10; {maximal number of modes                       }
      JMax       =   100; {maximal number of jobs                        }
      PMax       =  1000; {maximal number of periods                     }
      FMax       =     3; {maximal number different resource functions   }
      HorizonMax =  1000; {maximal horizon                               }
      ReqMax     =   100; {maximal request per period for any resource   }
      RenSupMax  =  5000; {maximal supply for renewable resources        }
      NonSupMax  = 50000; {maximal supply for nonrenewable resources     }
      CostMax    =   100; {maximal costs for tardy projects              }
TYPE Menge       = SET OF BYTE;
     ReqType     = BYTE;
     RenSupType  = INTEGER;
     NonSupType  = INTEGER;
     TimeType    = 0..HorizonMax;
     RDNType     = 0..RDNMax;
     CostType    = 0..CostMax;
     PType       = 1..PMax;
     DurType     = 0..duMax;
     MType       = 0..MMax;
     FType       = 0..FMax;
     JType       = 0..JMax;

{********************************************************************}
{***** constant period (total) resource availability            *****}
{********************************************************************}

     RenResAvlArray = ARRAY [1..RMax] OF RenSupType;
     DouResPerAvlArray = ARRAY [1..DMax] OF RenSupType;  {period availab.}
     DouResTotAvlArray  = ARRAY [1..DMax] OF NonSupType; {total availab. }
     NonResAvlArray  = ARRAY [1..NMax] OF NonSupType;

     Availability = RECORD
           RPer : RenResAvlArray;
           DPer : DouResPerAvlArray;
           DTot : DouResTotAvlArray;
           NTot : NonResAvlArray;
                    END;

{********************************************************************}
{*****  constant period resource request                        *****}
{********************************************************************}

     ResReqArray = ARRAY[RDNType] OF ReqType;

{********************************************************************}
{****  resource functions and probabilities                        **}
{********************************************************************}

     FunctionArray  = ARRAY[RDNType] OF FType;
     ProbArray      = ARRAY[FType] OF real;

     FuncSel         = RECORD
                   N :  FunctionArray;
                   R :  FunctionArray;
                   D :  FunctionArray;
                       END;

{********************************************************************}
{***** project jobs modes                                       *****}
{********************************************************************}

     Modes          = RECORD
          Duration  : DurType;
          RenResReq,
          DouResReq,
          NonResReq : ResReqArray;
                      END;

     ModeArray      = ARRAY[MType] OF Modes;

     Jobs           = RECORD
           NrOfModes: MType;
           Mode     : ModeArray;
                      END;

     JobArray       = ARRAY[JType] OF Jobs;
     DateArray      = ARRAY[PType] OF TimeType;
     CostArray      = ARRAY[PType] of CostType;
     ProArray       = ARRAY[PType] OF INTEGER;
     Project        = RECORD
           NrOfPro  :  PType;
           NrOfJobs :  JType;
           Pro      :  ProArray;
           CPMT     :  ProArray;
           DueDate  :  DateArray;
           RelDate  :  DateArray;
           TardCost :  CostArray;
           Job      :  JobArray;
           R,D,N    :  RDNType;
           Horizon  :  TimeType ;
                      END;


{********************************************************************}
{**** list of possible successors / predecessors                *****}
{********************************************************************}
     Selection      = RECORD
               List :  ARRAY [1..JMax+2] OF INTEGER;
               Nbr  :  INTEGER;
                      END;

{********************************************************************}
{***** projectinformation (start- ,finish-activities)                }
{********************************************************************}

     ProjectInfo=RECORD
            NrOfJobs : INTEGER;
            NrOfPro  : INTEGER;
            PI       : ProArray;
            SJ       : ProArray;
            FJ       : ProArray;
            NSJ      : ProArray;
            NFJ      : ProArray;
            CPMT     : ProArray;
                END;


{********************************************************************}
{***** input data                                               *****}
{********************************************************************}

     BaseStruct =  RECORD
                     NrOfPro    : PType       ;{# projects             }
                     MinJob     : JType       ;{min # jobs             }
                     MaxJob     : JType       ;{max # jobs             }
                     MaxRel     : TimeType    ;{max release date       }
                     DueDateFac : REAL        ;{due date factor        }
                     MinMode    : MType       ;{ min #modes per job    }
                     MaxMode    : MType       ;{ max #modes per job    }
                     MinDur     : DurType     ;{ min duration          }
                     MaxDur     : DurType     ;{ max duration          }

                     MinOutSour : INTEGER     ;{min # startactivities  }
                     MaxOutSour : INTEGER     ;{max # startactivities  }
                     MaxOut     : INTEGER     ;{max.# successors       }
                     MinInSink  : INTEGER     ;{min # finish activities}
                     MaxInSink  : INTEGER     ;{max # finish activities}
                     MaxIn      : INTEGER     ;{max # predecessors     }
                     Width      : INTEGER     ;{max # jobs with same rg}
                     Compl      : REAL        ;{complexety             }

                     MinRen     : RDNType     ;{min # ren. resources   }
                     MaxRen     : RDNType     ;{max # ren. resources   }
                     MinRReq    : ReqType     ;{min period request     }
                     MaxRReq    : ReqType     ;{max period request     }
                     MinRRU     : RDNType     ;{min # res. requested   }
                     MaxRRU     : RDNType     ;{max # res. requested   }
                     RRF        : REAL        ;{res. factor ren. res.  }
                     RRS        : REAL        ;{res. strength ren. res.}
                     NrOfRFunc  : FType       ;{# resource functions   }
                     RFuncProb  : ProbArray   ;{prob. of res. functions}

                     MinNon     : RDNType     ;
                     MaxNon     : RDNType     ;
                     MinNReq    : ReqType     ;
                     MaxNReq    : ReqType     ;
                     MinNRU     : RDNType     ;
                     MaxNRU     : RDNType     ;
                     NRF        : REAL        ;
                     NRS        : REAL        ;
                     NrOfNFunc  : FType       ;
                     NFuncProb  : ProbArray ;

                     MinDou     : RDNType     ;
                     MaxDou     : RDNType     ;
                     MinDReq    : ReqType     ;
                     MaxDReq    : ReqType     ;
                     MinDRU     : RDNType     ;
                     MaxDRU     : RDNType     ;
                     DRF        : REAL        ;
                     DRST       : REAL        ;
                     DRSP       : REAL        ;
                     NrOfDFunc  : FType       ;
                     DFuncProb  : ProbArray   ;
                     MaxTrials  : INTEGER     ;{max #trials to achieve cpl.}
                     NetTol     : REAL        ;{tolerance complexity-deviation}
                     ReqTol     : REAL        ;{tolerance request-deviation    }
                   END;

{********************************************************************}
     SampleInfo = RECORD
        B      : BaseStruct;
        BFile  : STRING;  
        DFile  : NameStr;
        DDir   : DirStr;
        DExt   : ExtStr;
        Inval  : LONGINT;
        NrOfEx : INTEGER;
               END;

{********************************************************************}
{**** datastructure network                                     *****}
{********************************************************************}

     TreeStruct =  ARRAY [1..JMax] OF
                   RECORD
                     NrOfPred : INTEGER;{# of predecessors            }
                     NrOfSucc : INTEGER;{# of successors              }
                     DirPred  : Menge  ;{set of immidiate predecessors}
                     DirSucc  : Menge  ;{set of immidiate successors  }
                     InDirPred: Menge  ;{set of successors            }
                     InDirSucc: Menge  ;{set of predecessors          }
                   END;

     CPMTimes = RECORD
        Mode  : INTEGER;
        EST   : INTEGER;
        EFT   : INTEGER;
               END;

     Time     = ARRAY[1..JMax] OF CPMTimes;

{*********************************************************************}
{****  datastructe destination files (sample,error)              *****}
{*********************************************************************}
    DFILES   = RECORD
         fp  : TEXT;
         efp : TEXT;
              END;
IMPLEMENTATION
BEGIN
END.
