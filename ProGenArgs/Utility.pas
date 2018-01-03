{********************************************************************}
     UNIT       Utility;
{    author :   A.Sprecher                                           }
{    date   :   12/17/92                                             }
{    version:   2.0                                                  }
{********************************************************************}

INTERFACE


USES DOS,CRT,TypeDecl;

{********************************************************************}
{**** function declaration                                      *****}
{********************************************************************}

PROCEDURE GenProjData(VAR x:LONGINT;B :BaseStruct;VAR P:Project);

FUNCTION Max(a,b:integer):integer;
FUNCTION Min(a,b:integer):integer;
FUNCTION MaxByte(a,b:byte):byte;
FUNCTION MinByte(a,b:byte):byte;
FUNCTION MaxReal(a,b:real):real;
FUNCTION Laplace(VAR ix:longint;ug,og:longint):longint;
PROCEDURE Rand(VAR ix:LONGINT);
PROCEDURE CalcCPMTimes(VAR P :Project;VAR PI :ProjectInfo;VAR TR :TreeStruct;
                       VAR T :Time;restype:CHAR;resnr:INTEGER);

PROCEDURE ErrorBreak(VAR efp:TEXT;crit :BOOLEAN;VAR success: BOOLEAN; ErrorNr: INTEGER);
FUNCTION  FindFile(fname: PathStr):BOOLEAN;

IMPLEMENTATION

{********************************************************************}
{task      : determination of minimum/maximaum of two reals/bytes    }
{********************************************************************}
FUNCTION Max(a,b:integer):integer;

BEGIN
  IF a>b THEN
    Max:=a
  ELSE
    Max:=b;
END;

FUNCTION Min(a,b:integer):integer;

BEGIN
  IF a<b THEN
    Min:=a
  ELSE
    Min:=b;
END;

FUNCTION MaxByte(a,b:byte):byte;

BEGIN
  IF a>b THEN
    MaxByte:=a
  ELSE
    MaxByte:=b;
END;

FUNCTION MaxReal(a,b:real):real;

BEGIN
  IF a>b THEN
    MaxReal:=a
  ELSE
    MaxReal:=b;
END;


FUNCTION MinByte(a,b:byte):byte;

BEGIN
  IF a<b THEN
    MinByte:=a
  ELSE
    MinByte:=b;
END;

{********************************************************************}
{ task     : generates a integer randomnumber within (0,21474833647) }
{            L. Schrage(1979): ACM Transactions,                     }
{ calling  : -                                                       }
{ called by: Laplace,Random01;                                       }
{********************************************************************}

PROCEDURE Rand(VAR ix:LONGINT);

CONST z=1;
VAR   xhi,xalo,leftlo,fhi,k: LONGINT;
      a,b15,b16,p          : LONGINT;
BEGIN
  a  :=16807;          {7^5   }
  b15:=32768;          {2^15  }
  b16:=65536;          {2^16  }
  p  :=2147483647;     {2^31-1}
  xhi:=TRUNC(ix/b16);
  xalo:=(ix-xhi*b16)*a;
  leftlo:=TRUNC(xalo/b16);
  fhi:=xhi*a+leftlo;
  k:=TRUNC(fhi/b15);
  ix:=(((xalo-leftlo*b16)-p)+(fhi-k*b15)*b16)+k;
  IF (ix < 0) THEN
    ix:=ix+p;
END;

{********************************************************************}
{ task      : generates a randomnumber within [0,1)                  }
{ calling   : rand                                                   }
{********************************************************************}

FUNCTION Random01(VAR x:Longint):real;

CONST  p  = 2147483647;     {2^31-1}

BEGIN
  Rand(x);
  Random01:=x/p;
END;


{********************************************************************}
{*** task     : generates a Laplace-distibuted random number within  }
{***            [n1,n2]                                              }
{*** calling  : rand                                                 }
{********************************************************************}

FUNCTION Laplace(VAR ix:longint;ug,og:longint):longint;


BEGIN
  rand(ix);
  Laplace:=TRUNC((ix/(2147483647/(og-ug+1)))+ug);
END;  {of randint                                                   }

{****************************************************************************}
{*** called by: GenModes                                                     }
{*** task     : generate a job with one mode, zero duration , zero request   }
{****************************************************************************}

PROCEDURE DummyJob(j:INTEGER;VAR B:BaseStruct;VAR P:Project);

VAR       r: INTEGER;

BEGIN
P.Job[j].NrOfModes:=1;
P.Job[j].Mode[1].Duration:=0;
FOR r:=1 TO P.N DO
  P.Job[j].Mode[1].NonResReq[r]:=0;
FOR r:=1 TO P.R DO
  P.Job[j].Mode[1].RenResReq[r]:=0;
FOR r:=1 TO P.D DO
  P.Job[j].Mode[1].DouResReq[r]:=0;
END;

{*************************************************************************}
{***** called by : GenModes                                               }
{***** task      : initilizes modes                                       }
{*************************************************************************}

PROCEDURE DurationZero(VAR P:Project);

VAR  i,j : INTEGER;

BEGIN
  FOR i:=1 TO P.NrOfJobs DO
  BEGIN
    P.Job[i].NrOfModes:=0;
    FOR j:=1 TO MMax DO
      P.Job[i].Mode[j].Duration:=0;
  END;
END;

{*************************************************************************}
{*** called by : GenModes                                                 }
{*** task      : sorting the modes with respect to durations(inceasingly) }
{*************************************************************************}

PROCEDURE SortModes(VAR P: Project);

VAR i,j,help: INTEGER;
    finished: BOOLEAN;

BEGIN
  FOR i:=2 TO P.NrOfJobs-1 DO
  BEGIN
    REPEAT
      finished:=TRUE;
      FOR j:=1 TO P.Job[i].NrOfModes-1 DO
        IF P.Job[i].Mode[j].Duration > P.Job[i].Mode[j+1].Duration THEN
          BEGIN
          help:=P.Job[i].Mode[j].Duration;
          P.Job[i].Mode[j].Duration:=P.Job[i].Mode[j+1].Duration;
          P.Job[i].Mode[j+1].Duration:=help;
          finished:=FALSE;
          END;
    UNTIL finished;
  END;
END;

{************************************************************************}
{*** called by : GenProjectData                                          }
{*** calling   : GenModes,GenDurations,Laplace                           }
{*** task      : generates the modes                                     }
{************************************************************************}

PROCEDURE GenModes(VAR x :LONGINT;VAR B :BaseStruct;VAR P:Project);

VAR i,j        : INTEGER;

BEGIN
  DurationZero(P);
  DummyJob(1,B,P);
  DummyJob(P.NrOfJobs,B,P);
  FOR i:=2 TO P.NrOfJobs-1 DO
  BEGIN
    P.Job[i].NrOfModes:=Laplace(x,B.MinMode,B.MaxMode);
    FOR j:=1 TO P.Job[i].NrOfModes DO
      P.Job[i].Mode[j].Duration:=Laplace(x,B.MinDur,B.MaxDur);
  END;
  SortModes(P);
END;


{*********************************************************************}
{*** called by : GenProjectData                                       }
{*** task      : calculates the time horizon T=sum max{d_jm| m=1,..M_j}
{*********************************************************************}

FUNCTION CalcHorizon(VAR P:Project):INTEGER;
VAR h,j:INTEGER;

BEGIN
h:=0;
WITH P DO
FOR j:= 1 TO P.NrOfJobs DO
  h:=h+Job[j].Mode[Job[j].NrOfModes].Duration;
CalcHorizon:=h;
END;



{********************************************************************}
{*** function  : Generate Project Data                               }
{*** calling   : GenModes,Laplace,CalcHorizon                        }
{*** called by : Main                                                }
{*** task      : genrates the basedata of the project and durations  }
{********************************************************************}

PROCEDURE GenProjData(VAR x : LONGINT; B: BaseStruct;VAR P:Project);

VAR   i         : INTEGER;
      MaxRelDate: INTEGER;
BEGIN
  P.NrOfPro :=B.NrOfPro;
  P.NrOfJobs:=0;
  MaxRelDate:=0;
  FOR i:=1 TO B.NrOfPro DO
    BEGIN
    P.Pro[i]     := Laplace(x,B.MinJob,B.MaxJob);
    P.NrOfJobs   := P.NrOfJobs+P.Pro[i];
    P.RelDate[i] := Laplace(x,0,B.MaxRel);
    MaxRelDate   := Max(MaxRelDate,P.RelDate[i]);
    P.TardCost[i]:= TRUNC(Random01(x)*P.Pro[i]);
    END;
  P.NrOfJobs:=P.NrOfJobs+2;
  P.Horizon:=0;
  P.R:=Laplace(x,B.MinRen,B.MaxRen);
  P.N:=Laplace(x,B.MinNon,B.MaxNon);
  P.D:=Laplace(x,B.MinDou,B.MaxDou);
  GenModes(x,B,P);
  P.Horizon:=MaxRelDate+CalcHorizon(P);
END;

{************************************************************************}
{***** task      : select the mode .....                                 }
{***** called by : CPM-Schedule                                          }
{************************************************************************}
FUNCTION SelectMode(VAR J:Jobs;restype:CHAR;resnr:INTEGER):INTEGER;

VAR      MaxReq,MaxReqMode,m: INTEGER;

BEGIN
CASE restype OF
  'd'    : SelectMode := 1;
  'R': BEGIN
       MaxReq:=-1;
       FOR m:=1 TO J.NrOfModes DO
          IF MaxReq<J.Mode[m].RenResReq[resnr] THEN
            BEGIN
              MaxReq:=J.Mode[m].RenResReq[resnr];
              MaxReqMode:= m;
            END;
       SelectMode:=MaxReqMode;
       END;
 'D':  BEGIN
       MaxReq:=-1;
       FOR m:=1 TO J.NrOfModes DO
          IF MaxReq<J.Mode[m].DouResReq[resnr] THEN
            BEGIN
            MaxReq:=J.Mode[m].DouResReq[resnr];
            MaxReqMode:= m;
            END;
       SelectMode:=MaxReqMode;
       END
END;
END;


{************************************************************************}
{***** task     : calculates CPM-lower bounds for each project           }
{*****            modes are selected due to shortest (d)uration, 0       }
{*****            maximal request (r)enewable rnr                        }
{*****            maximal request (d)oubly    rnr                        }
{***** called by:                                                        }
{************************************************************************}
PROCEDURE CalcCPMTimes(VAR P :Project;VAR PI:ProjectInfo;VAR TR:TreeStruct;
                       VAR T :Time;restype :CHAR;resnr:INTEGER);

VAR pnr,i,j: INTEGER;

BEGIN
FOR pnr:= 1 TO P.NrOfPro DO
  BEGIN
    FOR j:= PI.SJ[pnr] TO PI.FJ[pnr] DO
    BEGIN
      T[j].EST:=P.RelDate[pnr];
      FOR i:= PI.SJ[pnr] TO j-1 DO
        IF i in TR[j].DirPred THEN
          T[j].EST:=Max(T[j].EST,T[i].EFT);
      T[j].Mode:=SelectMode(P.Job[j],restype,resnr);
      T[j].EFT :=T[j].EST+P.Job[j].Mode[T[j].Mode].Duration;
    END;
    IF (restype='d') THEN
    BEGIN
      P.CPMT[pnr]:=0;
      FOR j:=PI.FJ[pnr]-PI.NFJ[pnr]+1 TO PI.FJ[pnr] do
        P.CPMT[pnr]:=Max(P.CPMT[pnr],T[j].EFT);
      PI.CPMT[pnr]:=P.CPMT[pnr];
    END;
  END;
END;




{************************************************************************}
{*****  task : writes errormesssages to console / errorfile              }
{*****         ErrorNr >= 1000  => fatal error                           }
{*****         ErrorNr <  1000  => simple error                          }
{************************************************************************}

PROCEDURE ErrorBreak(VAR efp:TEXT;crit :BOOLEAN;VAR success:BOOLEAN;
                     ErrorNr:INTEGER);

VAR Taste : STRING[2];

BEGIN
IF crit THEN
  BEGIN
  CASE ErrorNr Of
    1   : WRITELN(efp,'ERROR   1: Predecessor could not be determined');
    2   : WRITELN(efp,'ERROR   2: Successor could not be determined');
    3   : WRITELN(efp,'ERROR   3: Complexity could not be achieved (low)');
    4   : WRITELN(efp,'ERROR   4: Complexity could not be achieved (high)');
    11  : WRITELN(efp,'ERROR  11: max # req. resources > # resources for type R; -> max# := #');
    12  : WRITELN(efp,'ERROR  12: max # req. resources > # resources for type D; -> max# := #');
    13  : WRITELN(efp,'ERROR  13: max # req. resources > # resources for type N; -> max# := #');
    14  : WRITELN(efp,'ERROR  14: min # req. resources > max # for type R; -> min # := max #');
    15  : WRITELN(efp,'ERROR  15: min # req. resources > max # for type D; -> min # := max #');
    16  : WRITELN(efp,'ERROR  16: min # req. resources > max # for type N; -> min # := max #');
    17  : WRITELN(efp,'ERROR  17: RF for R can`t be achieved; min # req. resources too large');
    18  : WRITELN(efp,'ERROR  18: RF for D can`t be achieved; min # req. resources too large');
    19  : WRITELN(efp,'ERROR  19: RF for N can`t be achieved; min # req. resources too large');
    20  : WRITELN(efp,'ERROR  20: RF for R can`t be achieved; max # req. resources too small');
    21  : WRITELN(efp,'ERROR  21: RF for D can`t be achieved; max # req. resources too small');
    22  : WRITELN(efp,'ERROR  22: RF for N can`t be achieved; max # req. resources too small');
    23  : WRITELN(efp,'ERROR  23: Obtained RF falls short the tolerated range for R');
    24  : WRITELN(efp,'ERROR  24: Obtained RF falls short the tolerated range for D');
    25  : WRITELN(efp,'ERROR  25: Obtained RF falls short the tolerated range for N');
    26  : WRITELN(efp,'ERROR  26: Obtained RF exceeds the tolerated range for R');
    27  : WRITELN(efp,'ERROR  27: Obtained RF exceeds the tolerated range for D');
    28  : WRITELN(efp,'ERROR  28: Obtained RF exceeds the tolerated range for N');
    29  : WRITELN(efp,'ERROR  29: More than 1 trial was used to produce a job with non dominated modes');
   1000 : WRITELN(efp,'ERROR1000: Network generation without success');
   1001 : WRITELN(efp,'ERROR1001: Redundant arcs in network');
   1002 : WRITELN(efp,'ERROR1002: Non dominated modes for a job could`nt be produced with max # trials');
  END;
  IF (ErrorNr>=1000) THEN
    BEGIN
    WRITELN(CHR(7));
    writeln('ERROR  ',errornr);
    WRITELN('PROJECT Generation stopped !!!!!!!!!!!!!!!!!!');
    WRITELN('------>>>> fatal error execution stopped     ');
    WRITELN('terminate->>>  T :: continue ->>> RETURN ');
    READLN(Taste);
    IF taste[1]='T' THEN
      BEGIN
      CLOSE(efp);
      HALT;
      END;
    END;
  success:=FALSE;
  END;
END;

{********************************************************************}
{**** task : searches for a file                                     }
{********************************************************************}
FUNCTION FindFile(fname: PathStr):BOOLEAN;

CONST FileTypen = $27;
VAR      DirInfo : SearchRec;

BEGIN
fname:=fname+'*.err';
FindFirst(fname,FileTypen,DirInfo);
IF (DosError=0) THEN
  BEGIN
  Write(CHR(7));
  WriteLn('================================');
  WriteLn('!!!!!! FILE already exists !!!!!');
  WriteLn('================================');
  {WriteLn('continue             ---> RETURN');
  ReadLn;}
  FindFile:=TRUE;
  EXIT;
  END
ELSE
  FindFile:=FALSE;
END;


BEGIN
	
	
END.


