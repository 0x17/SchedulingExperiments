{****************************************************************************}
UNIT AvailGen;
{    author :   R.Kolisch                                                    }
{    date   :   5/6/92     20/12/91  19/08/91                                }
{    version:   2.0        1.01      1.0                                     }
{****************************************************************************}

INTERFACE

USES TypeDecl,Utility;

PROCEDURE ResAvlMain(VAR P:Project;VAR PI:ProjectInfo;VAR B:Basestruct;
                     VAR TR:TreeStruct;VAR ResAvl:Availability);


IMPLEMENTATION



{****************************************************************************}
{procedure: resource availability                                            }
{task     : generates the periode and total availabiltiy for all resources   }
{           with respect to request figures and desired RS                   }
{****************************************************************************}

PROCEDURE ResAvlMain(VAR P:Project;VAR PI:ProjectInfo;VAR B:Basestruct;
                     VAR TR:TreeStruct;VAR ResAvl:Availability);



{****************************************************************************}
{ Function : Resource Requirement                                            }
{ task     : Returns the resource requirement                                }
{****************************************************************************}

FUNCTION ResReq(j:JType;m:MType;r:RDNType;ResKind:CHAR):ReqType;

BEGIN
  CASE ResKind OF
        'R': ResReq:=P.Job[j].Mode[m].RenResReq[r];
        'D': ResReq:=P.Job[j].Mode[m].DouResReq[r];
        'N': ResReq:=P.Job[j].Mode[m].NonResReq[r];
  END;
END;



{****************************************************************************}
{Function : Minimum Usage                                                    }
{task     : Returns Max (Min (kjmr³mîMj)³jîJ)                                }
{****************************************************************************}

FUNCTION MinUse(ResPointer:RDNType; ResKind:CHAR):ReqType;

VAR   j       : JType;
      m       : MType;
      MinReq,
      MinReqJ : ReqType;

BEGIN
  MinReq:=0;
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
    MinReqJ:=ReqMax;
    FOR m:=1 TO P.Job[j].NrOfModes DO
       MinReqJ:=MinByte(MinReqJ,ResReq(j,m,ResPointer,ResKind));
    MinReq:=MaxByte(MinReq,MinReqJ);
  END;
  MinUse:=MinReq;
END;

{************************************************************************}
{function : Maximum per period use of renewable resources                }
{task     : calculates the maximal per period request of the MPM schedule}
{           if for each job the mode with the maximum per period request }
{           is used (ties are broken by smallest mode number)            }
{************************************************************************}

FUNCTION  MaxUse(VAR T:Time;restype:CHAR;resnr:INTEGER):INTEGER;

VAR      ReqAtTime: ARRAY[1..HorizonMax] OF INTEGER;
         MaxReq   : INTEGER;
         tt,j     : INTEGER;

BEGIN
  FOR tt:=1 TO P.Horizon DO
    ReqAtTime[tt]:=0;
  FOR j:= 2 TO P.NrOfJobs-1 DO
    FOR tt:=T[j].EST+1 TO T[j].EFT DO
      ReqAtTime[tt]:=ReqAtTime[tt]+ResReq(j,T[j].Mode,resnr,ResType);
{
CASE restype OF
  'R': BEGIN
       FOR j:= 2 TO P.NrOfJobs-1 DO
         FOR tt:=T[j].EST+1 TO T[j].EFT DO
           ReqAtTime[tt]:=ReqAtTime[tt]+
                          P.Job[j].Mode[T[j].Mode].RenResReq[resnr];
       END;
  'D': BEGIN
       FOR j:= 2 TO P.NrOfJobs-1 DO
         FOR tt:=T[j].EST+1 TO T[j].EFT DO
           ReqAtTime[tt]:=ReqAtTime[tt]+
                          P.Job[j].Mode[T[j].Mode].DouResReq[resnr];
       END;
}
MaxReq:=0;
FOR tt:= 1 TO P.Horizon DO
  MaxReq:=Max(MaxReq,ReqAtTime[tt]);
MaxUse:=MaxReq;
END;


{****************************************************************************}
{function : Maximum Consumption                                              }
{task     : Returns ä Max(kjmr*djm ³mîMj )                                   }
{                  jîJ                                                       }
{****************************************************************************}

FUNCTION MaxCon(ResPointer:RDNType; ResKind:CHAR):NonSupType;

VAR   j       : JType;
      m       : MType;
      TotalMaxCon,
      MaxConJ : NonSupType;

BEGIN
  TotalMaxCon:=0;
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
    MaxConJ:=0;
    FOR m:=1 TO P.Job[j].NrOfModes DO
       MaxConJ:=MaxByte(MaxConJ,ResReq(j,m,ResPointer,ResKind));
    TotalMaxCon:=TotalMaxCon+MaxConJ;
  END;
  MaxCon:=TotalMaxCon;
END;



{****************************************************************************}
{function : Minimum Consumption                                              }
{task     : Returns ä Min(kjmr*djm ³mîMj )                                   }
{                  jîJ                                                       }
{****************************************************************************}

FUNCTION MinCon(ResPointer:RDNType; ResKind:CHAR):NonSupType;

VAR   j       : JType;
      m       : MType;
      TotalMinCon,
      MinConJ : NonSupType;

BEGIN
  TotalMinCon:=0;
  FOR j:=2 TO P.NrOfJobs-1 DO
  BEGIN
    MinConJ:=ReqMax*duMax;
    FOR m:=1 TO P.Job[j].NrOfModes DO
       MinConJ:=Min(MinConJ,ResReq(j,m,ResPointer,ResKind));
    TotalMinCon:=TotalMinCon+MinConJ;
  END;
  MinCon:=TotalMinCon;
END;



{****************************************************************************}
{procedure: resource availability                                            }
{task     : generates the periode and total availabiltiy for all resources   }
{           with respect to request figures and desired RS                   }
{****************************************************************************}


VAR  r       : RDNType;
     TS      : Time;

BEGIN
  FOR r:=1 TO P.R DO
    BEGIN
    CalcCPMTimes(P,PI,TR,TS,'R',r);
    ResAvl.RPer[r]:=ROUND((1-B.RRS)*MinUse(r,'R')+B.RRS*MaxUse(TS,'R',r));
    END;
  FOR r:=1 TO P.N DO
    ResAvl.NTot[r]:=ROUND((1-B.NRS)*MinCon(r,'N')+B.NRS*MaxCon(r,'N'));
  FOR r:=1 TO P.D DO
  BEGIN
    CalcCPMTimes(P,PI,TR,TS,'D',r);
    ResAvl.DPer[r]:=ROUND((1-B.DRSP)*MinUse(r,'D')+B.DRSP*MaxUse(TS,'D',r));
    ResAvl.DTot[r]:=ROUND((1-B.DRST)*MinCon(r,'D')+B.DRST*MaxCon(r,'D'));
  END;
END;


BEGIN
END.
