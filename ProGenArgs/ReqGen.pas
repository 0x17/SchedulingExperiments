{****************************************************************************}
     UNIT       ReqGen;
{    author :   R.Kolisch                                                    }
{    date   :   5/15/92                                                      }
{    version:   2.0                                                          }
{****************************************************************************}

INTERFACE

USES  Crt,TypeDecl,Utility;

PROCEDURE ResReqMain(VAR ef:TEXT;VAR x1:LONGINT;VAR B:BaseStruct;VAR P:Project);

IMPLEMENTATION



{****************************************************************************}
{procedure: resource requirement mainprogram                                 }
{called by: genproj (Unit Projmain)                                          }
{calling  : ChooseResFunc, ResReqSub                                         }
{task     : main procedure for generating the resource requirement           }
{****************************************************************************}

PROCEDURE ResReqMain(VAR ef:TEXT;VAR x1:LONGINT;VAR B:BaseStruct;VAR P:Project);

TYPE ResDensType = ARRAY[JType,MType,RDNType] of BYTE;

VAR ResDens  : ResDensType;
    F        : FuncSel;



{****************************************************************************}
{function : number resources                                                 }
{task     : returns the number of resources for the given resource type      }
{****************************************************************************}

FUNCTION NumRes(ResType:CHAR):RDNType;

BEGIN
  CASE ResType OF
    'R': NumRes:=P.R;
    'D': NumRes:=P.D;
    'N': NumRes:=P.N;
  END;
END;



{****************************************************************************}
{function : minimum resource requirement                                     }
{task     : returns the minimum resource requirement for the given resource  }
{           type                                                             }
{****************************************************************************}

FUNCTION  MinResReq(ResType:CHAR):ReqType;

BEGIN
  CASE ResType OF
    'R': MinResReq:=B.MinRReq;
    'D': MinResReq:=B.MinDReq;
    'N': MinResReq:=B.MinNReq;
  END;
END;



{****************************************************************************}
{function : maximum resource requirement                                     }
{task     : returns the maximum resource requirement for the given resource  }
{           type                                                             }
{****************************************************************************}

FUNCTION  MaxResReq(ResType:CHAR):ReqType;

BEGIN
  CASE ResType OF
    'R': MaxResReq:=B.MaxRReq;
    'D': MaxResReq:=B.MaxDReq;
    'N': MaxResReq:=B.MaxNReq;
  END;
END;



{****************************************************************************}
{function : minimum number resources used                                    }
{task     : returns the minimim number of resources out of one resource type }
{           to be used by one [j,m]                                          }
{****************************************************************************}

FUNCTION MinResUsed(ResType:CHAR):RDNType;

BEGIN
  CASE ResType OF
    'R': MinResUsed:=B.MinRRU;
    'D': MinResUsed:=B.MinDRU;
    'N': MinResUsed:=B.MinNRU;
  END;
END;



{****************************************************************************}
{function : maximim number resources used                                    }
{task     : returns the maximum number of resources out of one resource type }
{           to be used by one [j,m]                                          }
{****************************************************************************}

FUNCTION MaxResUsed(ResType:CHAR):RDNType;

BEGIN
  CASE ResType OF
    'R': MaxResUsed:=B.MaxRRU;
    'D': MaxResUsed:=B.MaxDRU;
    'N': MaxResUsed:=B.MaxNRU;
  END;
END;



{****************************************************************************}
{function : resource factor                                                  }
{task     : returns the desired resource factor for one resource type        }
{****************************************************************************}

FUNCTION ResFac(ResType:CHAR):REAL;

BEGIN
  CASE ResType OF
    'R': ResFac:=B.RRF;
    'D': ResFac:=B.DRF;
    'N': ResFAc:=B.NRF;
  END;
END;



{****************************************************************************}
{function : resource function                                                }
{task     : returns the resource function for resource r of the desired type }
{****************************************************************************}

FUNCTION  ResFunc(ResType:CHAR; r:RDNType):FType;

BEGIN
  CASE ResType OF
    'R':ResFunc:=F.R[r];
    'D':ResFunc:=F.D[r];
    'N':ResFunc:=F.N[r];
  END;
END;



{****************************************************************************}
{function : resource function probability                                    }
{task     : returns the probability of the function for the resource type    }
{****************************************************************************}

FUNCTION ResFuncProb(ResType:CHAR; f:FType):REAL;

BEGIN
  CASE ResType OF
    'R':ResFuncProb:=B.RFuncProb[f];
    'D':ResFuncProb:=B.DFuncProb[f];
    'N':ResFuncProb:=B.NFuncProb[f];
  END;
END;



{****************************************************************************}
{function : errornumber                                                      }
{task     : returns the erronumber with respect to the base and resource type}
{****************************************************************************}

FUNCTION errornumber(base:INTEGER;ResType:CHAR):INTEGER;

BEGIN
  CASE ResType OF
    'R': errornumber:=base+1;
    'D': errornumber:=base+2;
    'N': errornumber:=base+3;
  END;
END;



{****************************************************************************}
{function : duration                                                         }
{task     : returns the duration of job j in mode m                          }
{****************************************************************************}

FUNCTION dur(j:JType;m:MType):DurType;

BEGIN
  dur:=P.Job[j].Mode[m].Duration;
END;



{****************************************************************************}
{function : resource requirement per period                                  }
{task     : returns the period resource requirement of job j in mode m with  }
{           respect to resource r of a certain type                          }
{****************************************************************************}

FUNCTION perreq(j:JType;m:MType;r:RDNType;ResType:CHAR):ReqType;

BEGIN
  CASE ResType OF
    'R':perreq:=P.Job[j].Mode[m].RenResReq[r];
    'D':perreq:=P.Job[j].Mode[m].DouResReq[r];
    'N':perreq:=P.Job[j].Mode[m].NonResReq[r];
  END;
END;



{********************* testprocedures and -functions ***********************}

PROCEDURE showreq(ResType:CHAR);

VAR j     : JType;
    m     : MType;
    r     : RDNType;
    answer: CHAR;

BEGIN
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
    WRITE('show ? ');
    READLN(answer);
    WRITELN('Resource requirement job ',j);
    WRITELN;
    FOR r:=1 TO NumRes(ResType) DO
    BEGIN
      FOR m:=1 TO P.Job[j].NrOfModes DO
        WRITE(perreq(j,m,r,ResType),' ');
      WRITELN;
    END
  END;
END;

PROCEDURE showdens(ResType:CHAR);

VAR j : JType;
    m : MType;
    r : RDNType;
    answer: CHAR;

BEGIN
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
    WRITE('show ? ');
    READLN(answer);
    WRITELN('Resource usage job ',j);
    WRITELN;
    FOR r:=1 TO NumRes(ResType) DO
    BEGIN
      FOR m:=1 TO P.Job[j].NrOfModes DO
         WRITE(ResDens[j,m,r],' ');
      WRITELN;
    END
  END;
END;

PROCEDURE showefficiency(j:JType);

VAR m1,m2: MType;
    r    : RDNType;              a:CHAR;

BEGIN
  FOR m1:=1 TO  P.Job[j].NrOfModes-1 DO
    FOR m2:=m1+1 TO P.Job[j].NrOfModes DO
    BEGIN
      WRITE('show ? ');READLN(a);
      WRITELN('         m',m1,' m',m2);
      WRITELN('dur:     ',dur(j,m1),' ',dur(j,m2));
      FOR r:=1 TO P.R DO
        WRITELN('perR[',r,']: ',perreq(j,m1,r,'R'),' ',perreq(j,m2,r,'R'));
      FOR r:=1 TO P.D DO
      BEGIN
        WRITELN('perD[',r,']: ',perreq(j,m1,r,'D'),' ',perreq(j,m2,r,'D'));
        WRITELN('totD[',r,']: ',perreq(j,m1,r,'D')*dur(j,m1),' ',perreq(j,m2,r,'D')*dur(j,m2));
      END;
      FOR r:=1 TO P.N DO
        WRITELN('totN[',r,']: ',perreq(j,m1,r,'N')*dur(j,m1),' ',perreq(j,m2,r,'N')*dur(j,m2));
    END;
END;



{****************************************************************************}
{procedure: choose resource function                                         }
{task     : Chooses for each resource out of ResType one time-resource       }
{           function with respect to the discret probability function        }
{           randomly                                                         }
{****************************************************************************}

PROCEDURE   ChooseResFunc(ResType:CHAR);

VAR choice,
    CumProb : REAL;
    func    : FType;
    r       : RDNType;

BEGIN
FOR r:=1 TO NumRes(ResType) DO
  BEGIN
    func:=1;
    choice:=laplace(x1,1,10)/10;
    CumProb:=ResFuncProb(ResType,func);
    WHILE (CumProb < choice) DO
    BEGIN
      func:=func+1;
      CumProb:=CumProb+ResFuncProb(ResType,func);
    END;
    CASE ResType OF
      'R':F.R[r]:=func;
      'D':F.D[r]:=func;
      'N':F.N[r]:=func;
    END;
  END;
END;



{****************************************************************************}
{procedure: adjust maximum number resources used                             }
{task     : if the maximum number of different resources used by one [j,m]   }
{           exceeds the number of resources, then the maximum number is set  }
{           to the number of resources                                       }
{****************************************************************************}

procedure AdjustMaxResUsed(error:BOOLEAN;ResType:CHAR);

BEGIN
  IF (error) THEN
    CASE ResType OF
      'R':B.MaxRRU:=P.R;
      'D':B.MaxDRU:=P.D;
      'N':B.MaxNRU:=P.N;
    END;
END;



{****************************************************************************}
{procedure: adjust minimum number resources used                             }
{task     : if the minimum number of different resources used by one [j,m]   }
{           exceeds the maximum number, then the minimum number is set to    }
{           to the maximum number                                            }
{****************************************************************************}

procedure AdjustMinResUsed(error:BOOLEAN;ResType:CHAR);

BEGIN
  IF (error) THEN
    CASE ResType OF
      'R':B.MinRRU:=B.MaxRRU;
      'D':B.MinDRU:=B.MaxDRU;
      'N':B.MinNRU:=B.MaxNRU;
    END;
END;



{****************************************************************************}
{procedure: test resource density                                            }
{task     : Tests correctness of resource factor, the minimum and maximum     }
{           number resources requested by each [j,m]                         }
{****************************************************************************}

PROCEDURE   TestResDens(ResType: CHAR);

VAR  success    : BOOLEAN;

BEGIN
  errorbreak(ef,MaxResUsed(ResType)>NumRes(ResType),success,errornumber(10,ResType));
  AdjustMaxResUsed(maxresused(ResType)>NumRes(ResType),ResType);
  errorbreak(ef,MinResUsed(ResType)>MaxResUsed(ResType),success,errornumber(13,ResType));
  AdjustMinResUsed(MinResUsed(ResType)>MaxResUsed(ResType),ResType);
  IF (NumRes(ResType)>0) THEN
  BEGIN
    errorbreak(ef,((NumRes(ResType)>0) AND (ResFac(ResType)<
          MinResUsed(ResType)/NumRes(ResType))),success,errornumber(16,ResType));
    errorbreak(ef,((NumRes(ResType)>0) AND (ResFac(ResType)>
          MaxResUsed(ResType)/NumRes(ResType))),success,errornumber(19,ResType));
  END;
END;



{****************************************************************************}
{procedure: initialize resource density matrix                               }
{task     : Initializes the part of the resource density matrix which belongs}
{           to job j                                                         }
{****************************************************************************}

PROCEDURE InitResDens(j:JType; ResType:CHAR);

VAR m : MType;
    r : RDNType;

BEGIN
    FOR m:=1 TO P.Job[j].NrOfModes DO
      FOR r:=1 TO NumRes(ResType) DO
        ResDens[j,m,r]:=0;
END;



{****************************************************************************}
{procedure: Set minimum resource density                                     }
{task     : Sets the minimum resource density as required by minnum          }
{****************************************************************************}

PROCEDURE   SetMinResDens(j:JType;ResType:CHAR);

VAR m      : MType;
    r,
    ActNr : RDNType;

BEGIN
  FOR m:=1 TO P.Job[j].NrOfModes DO
    BEGIN
      ActNr:=0;
      WHILE (ActNr < MinResUsed(ResType)) DO
      BEGIN
        r:=laplace(x1,1,NumRes(ResType));
        IF (ResDens[j,m,r]=0) THEN
        BEGIN
          ResDens[j,m,r]:=1;
          ActNr:=ActNr+1;
        END;
      END;
    END;
END;



{****************************************************************************}
{function : Number requested resources                                       }
{task     : Checks how many different resources are requested by [j,m]       }
{****************************************************************************}

FUNCTION    NrReqRes(j:JType; m:MType; ResType:CHAR):RDNType;

VAR r,
    count : RDNType;

BEGIN
  count:=0;
  FOR r:=1 TO NumRes(ResType) DO
    IF (ResDens[j,m,r]=1) THEN
      count:=count+1;
  NrReqRes:=count;
END;



{****************************************************************************}
{procedure: determine                                                        }
{task     : Determines the randomly chosen tripel [j,m,r]                    }
{****************************************************************************}

FUNCTION   Determine (element:LONGINT; ResType:CHAR):Jtype;

VAR sum           : LONGINT;
    j,
    jchosen       : JType;
    m             : MType;
    r             : RDNType;
    TripelNotFound: BOOLEAN;

BEGIN
  sum:=1;
  TripelNotFound:=TRUE;
  FOR j:=2 TO P.NrOfJobs-1 DO
    FOR m:=1 TO P.Job[j].NrOfModes DO
      FOR r:=1 TO NumRes(ResType) DO
        IF ((TripelNotFound) AND (ResDens[j,m,r]=0) AND
            (NrReqRes(j,m,ResType)<MaxResUsed(ResType))) THEN
        BEGIN
          IF (sum=element) THEN
            BEGIN
              ResDens[j,m,r]:=1;
              TripelNotFound:=FALSE;
              jchosen:=j;
            END
          ELSE
            sum:=sum+1;
        END;
  Determine:=jchosen;
END;



{****************************************************************************}
{function : Set resource density                                             }
{task     : Sets the resource density as required by the resource factor     }
{****************************************************************************}

PROCEDURE SetResDens(ResType:CHAR);


VAR j,jchosen   : JType;
    m           : MType;
    r           : RDNType;
    ActResFac   : REAL;
    element,
    freelements : LONGINT;
    success     : BOOLEAN;

BEGIN
  ActResFac:=MinResUsed(ResType)/maxbyte(1,NumRes(ResType));
  freelements:=0;
  FOR j:=2 TO P.NrOfJobs-1 DO
    freelements:=freelements+P.Job[j].NrOfModes;
  freelements:=freelements*(NumRes(ResType)-MinResUsed(ResType));
  WHILE ((ResFac(ResType) > ActResFac) AND (freelements > 0)) DO
  BEGIN
    element:=laplace(x1,1,freelements);
    jchosen:=determine(element,ResType);
    freelements:=freelements-1;
    ActResFac:=ActResFac+1/((P.NrOfJobs-2)*NumRes(ResType)*P.Job[jchosen].NrOfModes);
  END;
{
  WRITE('RF of ',ActResFac:4:2,' for type ',ResType,' achieved;');
  WRITELN(' RF of ',ResFac(ResType):4:2, ' desired.');
}
  errorbreak(ef,(ActResFac<ResFac(ResType)*(1-B.ReqTol)),success,errornumber(22,ResType));
  errorbreak(ef,(ActResFac>ResFac(ResType)*(1+B.ReqTol)),success,errornumber(25,ResType));
END;



{****************************************************************************}
{function : Generate resource density                                        }
{task     : generates the resource density matrix for the given resource type}
{****************************************************************************}

PROCEDURE GenResdens(ResType:CHAR);

VAR j:JType;

BEGIN
  TestResDens(ResType);
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
    InitResDens(j,ResType);
    SetMinResDens(j,ResType);
  END;
  SetResDens(ResType);
END;



{****************************************************************************}
{procedure: write resource requirement                                       }
{task     : Writes the resource requirement into the record Job              }
{****************************************************************************}

PROCEDURE WriteResReq(j:JType;m:MType;r:RDNType;req:ReqType;ResType:CHAR);

BEGIN
  CASE ResType OF
    'R': P.Job[j].Mode[m].RenResReq[r]:=req;
    'D': P.Job[j].Mode[m].DouResReq[r]:=req;
    'N': P.Job[j].Mode[m].NonResReq[r]:=req;
  END;
END;



{****************************************************************************}
{procedure: intitialize resource requirement                                 }
{task     : Initializes the resource requirement for job j                   }
{****************************************************************************}

PROCEDURE   InitReq(j:JType;ResType:CHAR);

VAR m   : MType;
    r   : RDNType;

BEGIN
  FOR m:=1 TO P.Job[j].NrOfModes DO
    FOR r:=1 TO NumRes(ResType) DO
      WriteResReq(j,m,r,0,ResType);
END;




{****************************************************************************}
{function : Number of modes requesting a resource without same duration      }
{called by: ReqAm                                                            }
{calling  : -                                                                }
{task     : determines how many modes out of job j require resource r with-  }
{         : out having the same duration                                     }
{****************************************************************************}

FUNCTION ModesReqResWithoutSameDur(j:JType;r:RDNType):MType;

VAR count : RDNType;
    m     : MType;
    DurSet: SET OF DurType;

BEGIN
  DurSet:=[];
  count:=0;
  FOR m:=1 TO P.Job[j].NrOfModes DO
   IF (ResDens[j,m,r]=1) THEN
     IF (P.Job[j].Mode[m].Duration IN DurSet) THEN
     ELSE
     BEGIN
       DurSet:=DurSet+[P.Job[j].Mode[m].Duration];
       count:=count+1;
     END;
  ModesReqResWithoutSameDur:=count;
END;




{****************************************************************************}
{function : next mode with different duration                                }
{task     : determines whether the next mode has the same duration or not    }
{****************************************************************************}

FUNCTION NextModeWithDiffDur(j:JType; m:MType):BOOLEAN;

BEGIN
  IF ((m < P.Job[j].NrOfModes) AND
      (P.Job[j].Mode[m].Duration=P.Job[j].Mode[m+1].Duration)) THEN
      NextModeWithDiffDur:=FALSE
  ELSE
      NextModeWithDiffDur:=TRUE;
END;




{****************************************************************************}
{procedure: required resource amount                                         }
{task     : determines for every [j,m] the amount of resource usage with     }
{           respect to ResDens and the time-resource functions               }
{****************************************************************************}

PROCEDURE   ReqAm (j:JType;r:RDNType;ResType:CHAR);

VAR       Req1,Req2,
          ReqMin,ReqMax : ReqType;
          m,d           : MType;
          delta         : real   ;

BEGIN
  CASE ResFunc(ResType,r) OF

  {constant resource requirement per period for every duration          }

    1 :BEGIN
         Req1:=laplace(x1,MinResReq(ResType),MaxResReq(ResType));
         FOR m:=1 TO P.Job[j].NrOfModes DO
         IF (ResDens[j,m,r]=1) THEN
           WriteResReq(j,m,r,Req1,ResType);
       END;

  {inverse function between resource requirement per period and duration}

    2 :BEGIN
         Req1:=laplace(x1,MinResReq(ResType),MaxResReq(ResType));
         Req2:=laplace(x1,MinResReq(ResType),MaxResReq(ResType));
         ReqMin:=MinByte(Req1,Req2);
         ReqMax:=MaxByte(Req1,Req2);
         d:=1;
         delta:=(ReqMax-ReqMin)/MaxByte(1,ModesReqResWithoutSameDur(j,r));
         FOR m:=1 TO P.Job[j].NrOfModes DO
           IF (ResDens[j,m,r]=1) THEN
           BEGIN
             Req1:=laplace(x1,ROUND(ReqMax-d*delta),ROUND(ReqMax-(d-1)*delta));
             WriteResReq(j,m,r,Req1,ResType);
             IF (NextModeWithDiffDur(j,m)) THEN
               d:=d+1;
           END;
       END;
  END;
END;



{****************************************************************************}
{procedure: compare                                                          }
{task     : Compares the two values val1 and val2                            }
{****************************************************************************}

PROCEDURE compare(VAR M1supM2,M2supM1:BOOLEAN; val1,val2:INTEGER);

BEGIN
  IF (val1 < val2) THEN
    M1supM2:=TRUE
  ELSE IF (val2 < val1) THEN
    M2supM1:=TRUE;
END;



{****************************************************************************}
{procedure: resource type efficiency                                         }
{task     : compares the values of two modes for one resource type;          }
{           if for at least one value v(mode1) <(>) v(mode2) is valid,       }
{           then M1sM2=TRUE (M2sM1=TRUE)                                     }
{****************************************************************************}

PROCEDURE ResTypeEff(VAR M1sM2,M2sM1:BOOLEAN;j:JType;m1,m2:MType;ResType:CHAR);

VAR r: RDNType;

BEGIN
 FOR r:=1 TO NumRes(ResType) DO
   compare(M1sM2,M2sM1,perreq(j,m1,r,ResType),perreq(j,m2,r,ResType));
END;




{****************************************************************************}
{function : efficiency                                                       }
{task     : Tests all mode pairs of a job with respect to efficiency         }
{****************************************************************************}

FUNCTION Efficiency(j:JType):BOOLEAN;

VAR m1,m2         : BYTE;
    M1supM2,
    M2supM1       : BOOLEAN;
    efficient     : BOOLEAN;

BEGIN
  efficient:=TRUE;
  m1:=1;
  m2:=2;
  WHILE ((efficient) AND (m1<P.Job[j].NrOfModes))DO
  BEGIN
    M1supM2:=FALSE;
    M2supM1:=FALSE;
    compare(M1supM2,M2supM1,dur(j,m1),dur(j,m2));
    IF NOT ((M1supM2) AND (M2supM1)) THEN
      ResTypeEff(M1supM2,M2supM1,j,m1,m2,'R');
    IF NOT ((M1supM2) AND (M2supM1)) THEN
      ResTypeEff(M1supM2,M2supM1,j,m1,m2,'D');
    IF NOT ((M1supM2) AND (M2supM1)) THEN
      ResTypeEff(M1supM2,M2supM1,j,m1,m2,'N');
    IF NOT ((M1supM2) AND (M2supM1)) THEN
      efficient:=FALSE;
    IF (m2=P.Job[j].NrOfModes) THEN
      BEGIN
        m1:=m1+1;
        m2:=m1+1;
      END
    ELSE
      m2:=m2+1;
  END;
  efficiency:=efficient;
END;


{****************************************************************************}
{procedure: resource requirement subprogramm                                 }
{task     : calls for each resource type the relevant subprograms            }
{****************************************************************************}

PROCEDURE   ResReqSub(ResType:CHAR);

VAR j: JType;
    r: RDNType;    a:CHAR;

BEGIN
{
  WRITELN('...Generating Resource Factor for type ',ResType);
}
  genresdens(ResType);
{
  WRITE('show density <y/n>? '); READLN(a);
  IF (a='y') THEN
    showdens(ResType);
}
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
   initreq(j,ResType);
   FOR r:=1 TO NumRes(ResType) DO
     ReqAm(j,r,ResType);
  END;
{
  WRITE('show resource request <y/n>? '); READLN(a);
  IF (a='y') THEN
   showreq(ResType);
}
END;



{****************************************************************************}
{procedure: assign new durations                                             }
{task     : assigns increasing sorted durations to overcome dominated modes  }
{****************************************************************************}
{
PROCEDURE AssNewDur(j:JType);

VAR m:MType;

BEGIN
  FOR m:=1 TO P.Job[j].NrOfModes DO
    P.Job[j].Mode[m].Duration:=laplace(x1,B.MinDur,B.MaxDur);
  sortmodes(P,j);
END;
}





{****************************************************************************}
{procedure: assign new density                                               }
{task     : assigns a new resource usage matrix with respect to min, max     }
{           number of used resources as well as the present resource factor  }
{****************************************************************************}

PROCEDURE assnewdens(j:JType;ResType:CHAR);

VAR m            : MType;
    r            : RDNType;
    nonzeros,
    element,
    sum          : INTEGER;
    tupelnotfound: BOOLEAN;

BEGIN
  nonzeros:=0;
  FOR m:=1 TO P.Job[j].NrOfModes DO
    FOR r:=1 TO NumRes(ResType) DO
      IF (perreq(j,m,r,ResType)>0) THEN
        nonzeros:=nonzeros+1;
  InitResDens(j,ResType);
  SetMinResDens(j,ResType);
  nonzeros:=nonzeros-MinResUsed(ResType)*P.Job[j].NrOfModes;
  WHILE (nonzeros>0) DO
  BEGIN
    element:=laplace(x1,1,nonzeros);
    sum:=1;
    tupelnotfound:=TRUE;
    FOR m:=1 TO P.Job[j].NrOfModes DO
      FOR r:=1 TO NumRes(ResType) DO
        IF ((ResDens[j,m,r]=0) AND (NrReqRes(j,m,ResType)<MaxResUsed(ResType))
                               AND TupelNotFound) THEN
        BEGIN
          IF (sum=element) THEN
            BEGIN
              ResDens[j,m,r]:=1;
              TupelNotFound:=FALSE;
              nonzeros:=nonzeros-1;
            END
          ELSE
            sum:=sum+1;
        END;
  END;
END;



{****************************************************************************}
{procedure: assign new request                                               }
{task     : assign for job j the resource request with respect to the new    }
{           usage matrix                                                     }
{****************************************************************************}

PROCEDURE assnewreq(j:JType;ResType:CHAR);

VAR r:RDNType;

BEGIN
  initreq(j,ResType);
  FOR r:=1 TO NumRes(ResType) DO
    reqam(j,r,ResType);
END;



{****************************************************************************}
{procedure: test efficiency                                                  }
{task     : tests efficiency of each job; if a job is not efficient ...      }
{****************************************************************************}

PROCEDURE TestEfficiency;

VAR j        : JType;
    numtrials: BYTE;
    success  : BOOLEAN;  a,a1,a3:CHAR;

BEGIN
{
  WRITELN('Testing Efficiency ...');
  WRITE('show values <y/n>? '); READLN(a1);
}
  FOR j:=2 TO P.NrOfJobs-1 DO
    IF (P.Job[j].NrOfModes>1) THEN
      BEGIN
{
      IF (a1='y') THEN
        BEGIN
          showefficiency(j); WRITE('carry on ?'); READLN(a3);
        END;
}
      IF NOT (efficiency(j)) THEN
      BEGIN
{
        WRITELN('job ',j,' has at least one inefficient mode');
}
        numtrials:=0;
        REPEAT
{
          AssNewDur(j);
}
          AssNewDens(j,'R');
          AssNewReq(j,'R');
          AssNewDens(j,'D');
          AssNewReq(j,'D');
          AssNewDens(j,'N');
          AssNewReq(j,'N');
          numtrials:=numtrials+1;
{
         IF (a1='y') THEN
           BEGIN
            showefficiency(j);WRITE('carry on ?');READLN(b);
           END;
}
        UNTIL ((efficiency(j)) OR (numtrials>B.MaxTrials));
{
        WRITELN(numtrials,' number of trials used to resolve inefficient mode');
}
        errorbreak(ef,efficiency(j),success,29);
        errorbreak(ef,NOT(efficiency(j)),success,1002);
{
        WRITE('end ? ');READLN(b)
}
      END
{
      ELSE
        WRITELN('job ',j,' is efficient');
      END;
}
  END;
END;




BEGIN
  ChooseResFunc('R');
  ResReqSub('R');

  ChooseResFunc('D');
  ResReqSub('D');

  ChooseResFunc('N');
  ResReqSub('N');

  TestEfficiency;

END;

END.

