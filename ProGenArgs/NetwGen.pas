{********************************************************************}
{***** network generation                                       *****}
{********************************************************************}

UNIT NetwGen;

INTERFACE


USES CRT,TypeDecl,Utility,InOut;


PROCEDURE GenNetwork(VAR efp:TEXT;VAR x:LONGINT;B :BaseStruct;VAR P:Project;
                     VAR PI :ProjectInfo;VAR TD:TreeStruct;VAR success:BOOLEAN);
PROCEDURE CalcDueDates(VAR B:BaseStruct;VAR P:Project;VAR PI:ProjectInfo);
PROCEDURE WriteNetwToFile(Var fp :TEXT ;VAR P:Project;VAR TD:TreeStruct);


IMPLEMENTATION


{************************************************************************}
{***** task     : calculates the duedates                                }
{***** called by:                                                        }
{************************************************************************}

PROCEDURE CalcDueDates(VAR B: BaseStruct;VAR P:Project;VAR PI:ProjectInfo);

VAR       pnr : INTEGER;
BEGIN
FOR pnr:= 1 TO P.NrOfPro DO
  BEGIN
  P.DueDate[pnr]:=TRUNC({P.RelDate[pnr]+}P.CPMT[pnr]
                  +B.DueDateFac*(P.Horizon-P.CPMT[pnr]));
  END;
END;


{************************************************************************}
{***** task: write network to file                                  *****}
{*****       by construction the nodes are numerical labled         *****}
{*****
{************************************************************************}

PROCEDURE WriteNetwToFile(Var fp :TEXT;VAR P:Project;VAR TD:TreeStruct);

 VAR i,j     : INTEGER;
     pi      : INTEGER;
 BEGIN
   WRITELN (fp,'PRECEDENCE RELATIONS:');
   WRITELN (fp,'jobnr.    #modes  #successors   successors');
   FOR i:=1 TO P.NrOfJobs DO
   BEGIN
     WRITE(fp,i:4);
     WRITE(fp,P.Job[i].NrOfModes:9);
     WRITE(fp,TD[i].NrOfSucc:11);
     WRITE(fp,'        ');
     FOR j:=i+1 TO P.NrOfJobs DO
       IF j IN TD[i].DirSucc THEN
         WRITE(fp,j:4);
     WRITELN (fp);
   END;
   Replicate(fp,72,'*');
 END;

{*************************************************************************}
{***** function: generate network (without redundant arcs)                }
{***** called by: main                                                    }
{*************************************************************************}

PROCEDURE GenNetwork(VAR efp :TEXT;VAR x:LONGINT;B:BaseStruct;VAR P:Project;
                     VAR PI:ProjectInfo;VAR TD:TreeStruct;VAR success:BOOLEAN);


VAR
     Arcs     : INTEGER;
     TrialNr  : INTEGER;
     pnr      : INTEGER;


{**************************************************************************}
{*****   task: calculate start- and finishing activities              *****}
{*****----------------------------------------------------------------*****}
{*****   ProInf.PI[pnr] : nr of jobs of project pnr                   *****}
{*****   ProInf.SJ[pnr] : nr of first jobs of project pnr             *****}
{*****   ProInf.NSJ[pnr]: nr of start activities of project pnr       *****}
{*****   ProInf.NFJ[pnr]: nr of end   activities of project pnr       *****}
{**************************************************************************}

PROCEDURE CalcStartAndFinJobs(VAR x:LONGINT;VAR B:BaseStruct;VAR ProInf:ProjectInfo);

VAR       ip    :INTEGER;

BEGIN
WITH ProInf DO
  BEGIN
  NrOfJobs:=1;
  FOR ip:=1 TO P.NrOfPro DO
    BEGIN
    SJ[ip]   := NrOfJobs+1;
    PI[ip]   := P.Pro[ip];
    NrOfJobs := NrOfJobs+PI[ip];
    FJ[ip]   := NrOfJobs;
    END;
  NrOfJobs:=NrOfJobs+1;
  END;
END;

{**************************************************************************}
{****  task:    test if arc (i,j) is redundant or not                 *****}
{****                   (j>i is assumed)                              *****}
{**************************************************************************}

FUNCTION Redundant(i,j,FJ: INTEGER) : BOOLEAN;

VAR  k,l: INTEGER;

BEGIN
redundant:=FALSE;
{**** case (a)   *****}
IF j IN TD[i].InDirSucc THEN
  redundant:=TRUE;
{**** case (b)   *****}
FOR k:=j+1 TO FJ DO
  IF (k IN TD[j].InDirSucc) AND
     (TD[k].DirPred*TD[i].InDirPred<>[]) THEN
    redundant:=TRUE;
{***** case (c)  *****}
IF TD[j].DirPred*TD[i].InDirPred<>[] THEN
  redundant:=TRUE;
{***** case (d) *****}
IF TD[i].DirSucc*TD[j].InDirSucc<>[] THEN
  redundant:=TRUE;
END;

{*************************************************************************}
{**** task: determine the set of (possible) successors of job i      *****}
{*************************************************************************}

PROCEDURE PossSucc(VAR B:BaseStruct;i,jmin:INTEGER;VAR pnr:INTEGER;
                   VAR ProInfo:ProjectInfo;VAR Successor:Selection);
 VAR j : INTEGER;

BEGIN
  Successor.Nbr:=0;
    FOR j:=jmin TO ProInfo.FJ[pnr] DO
      IF (TD[j].NrOfPred<B.MaxIn) AND
          NOT(Redundant(i,j,ProInfo.FJ[pnr])) THEN
        BEGIN
        Successor.Nbr:=Successor.Nbr+1;
        Successor.List[Successor.Nbr]:=j;
        END;
END;

{*************************************************************************}
{**** task: determine the set of (possible) predecessors of job i    *****}
{*************************************************************************}

PROCEDURE PossPred(VAR B:BaseStruct;j,iMax:INTEGER;VAR pnr:INTEGER;
                   VAR ProInfo:ProjectInfo;VAR Predecessor:Selection);

VAR i : INTEGER;

 BEGIN
   Predecessor.Nbr:=0;
   FOR i:=PI.SJ[pnr] TO iMax DO
   IF ((TD[i].NrOfSucc < B.MaxOut) AND
        NOT(Redundant(i,j,P.NrOfJobs))) THEN
     BEGIN
     Predecessor.Nbr:=Predecessor.Nbr+1;
     Predecessor.List[Predecessor.Nbr]:=i;
     END
END;


{************************************************************************}
{***** task:add arc (i,j) to network => update precedence relations *****}
{************************************************************************}

PROCEDURE AddArc(i,j,J2 : INTEGER);

 VAR k:INTEGER;

 BEGIN
   WITH TD[i] DO
   BEGIN
     NrOfSucc := NrOfSucc + 1;
     DirSucc  := DirSucc + [j];
     InDirSucc:= InDirSucc+ [j] + TD[j].InDirSucc;
   END;
   WITH TD[j] DO
   BEGIN
     NrOfPred := NrOfPred + 1;
     DirPred  := DirPred + [i];
     InDirPred:= InDirPred + [i] + TD[i].InDirPred;
   END;
   arcs:=arcs+1;
   FOR k:= 1 TO i-1 DO
     IF k IN TD[i].InDirPred THEN
        TD[k].InDirSucc:=TD[k].InDirSucc+TD[i].InDirSucc;
   FOR k:= j+1 TO J2 DO
     IF k IN TD[j].InDirSucc THEN
        TD[k].InDirPred:=TD[k].InDirPred+TD[j].InDirPred;
END;

{*************************************************************************}
{***** task: init network                                            *****}
{*************************************************************************}

PROCEDURE InitNetw(j1,j2:INTEGER);

 VAR  i : INTEGER;

BEGIN
FOR i:=j1 TO j2 DO
  BEGIN
  TD[i].NrOfPred:=0; TD[i].NrOfSucc:=0;
  TD[i].DirPred:=[]; TD[i].DirSucc:=[];
  TD[i].InDirPred:=[]; TD[i].InDirSucc:=[];
  END;
END;

{*************************************************************************}
{***** task: add arcs due to  start- and finsh-activities            *****}
{*************************************************************************}

PROCEDURE AddArcsToSourceASink(B : BaseStruct;ProInf: ProjectInfo);

 VAR  pnr,i: INTEGER;
      J2   : INTEGER;

BEGIN
WITH ProInf DO
FOR pnr:=1 TO NrOfPro DO
  BEGIN
  FOR i:=1 TO NSJ[pnr] DO
    AddArc(1,SJ[pnr]+i-1,NrOfJobs);
  FOR i:=1 TO NFJ[pnr] DO
    AddArc(FJ[pnr]-i+1,P.NrOfJobs,NrOfJobs);
  END
END;


{*************************************************************************}
{***** task: add a predecessor to each job in project pnr            *****}
{*************************************************************************}

FUNCTION AddPred(VAR x :LONGINT;B :BaseStruct;ProInf :ProjectInfo;
                   pnr :INTEGER):BOOLEAN;

 VAR j          : INTEGER;
     iMax       : INTEGER;
     Predecessor: Selection;
     index      : INTEGER;

 BEGIN
WITH ProInf DO
   FOR j:=SJ[pnr]+NSJ[pnr] TO FJ[pnr] DO
     BEGIN
       iMax:=MinByte(j-1,FJ[pnr]-NFJ[pnr]);
       PossPred(B,j,iMax,pnr,ProInf,Predecessor);
       IF Predecessor.Nbr>0 THEN
         BEGIN
         index:=Laplace(x,1,Predecessor.Nbr);
         AddArc(Predecessor.List[index],j,NrOfJobs)
         END
       ELSE
         BEGIN
         AddPred:=FALSE;
         EXIT;
         END;
     END;
 AddPred:=True
 END;

{*************************************************************************}
{***** task: add successor to each job in project pnr                *****}
{*************************************************************************}

FUNCTION AddSucc(VAR x :LONGINT;B :BaseStruct;ProInf :ProjectInfo;
                   pnr :INTEGER):BOOLEAN;

 VAR i          : INTEGER;
     Successor  : Selection;
     jMin       : INTEGER;
     index      : INTEGER;
 BEGIN
WITH ProInf DO
  FOR i:=SJ[pnr] TO FJ[pnr]-NFJ[pnr] DO
    IF (TD[i].NrOfSucc=0) THEN
      BEGIN
      jMin:=MaxByte(i+1,SJ[pnr]+NSJ[pnr]);
      PossSucc(B,i,jMin,pnr,ProInf,Successor);
      IF Successor.Nbr>0 THEN
        BEGIN
        index:=Laplace(x,1,Successor.Nbr);
        AddArc(i,Successor.List[index],NrOfJobs)
        END
      ELSE
        BEGIN
        AddSucc:=FALSE;
        EXIT;
        END;
      END;
AddSucc:=TRUE
END;

{************************************************************************}
{***** task: add arcs up to complexity in project pnr               *****}
{*****       start- and finish activities are taken into account    *****}
{************************************************************************}

FUNCTION AddArcsToCompl(VAR x :LONGINT;B :BaseStruct;ProInf :ProjectInfo;
                            pnr:INTEGER):BOOLEAN;

 VAR  root       : INTEGER;
      Successor  : Selection;
      TrialNr    : INTEGER;
      jmin       : INTEGER;
 BEGIN
   TrialNr:=0;
   WHILE (arcs < B.Compl*(ProInf.PI[pnr]+2)) AND (TrialNr<=B.MaxTrials) DO
     BEGIN
     root:=Laplace(x,ProInf.SJ[pnr],ProInf.FJ[pnr]-ProInf.NFJ[pnr]);
     IF (TD[root].NrOfSucc<B.MaxOut) THEN
       BEGIN
       jmin:=MaxByte(root+1,ProInf.SJ[pnr]+ProInf.NSJ[pnr]);
       PossSucc(B,root,jmin,pnr,ProInf,Successor);
       IF Successor.Nbr>0 THEN
         AddArc(root,Successor.List[Laplace(x,1,Successor.Nbr)],ProInf.NrOfJobs)
       ELSE
         TrialNr:=TrialNr+1;
       END
     ELSE
       TrialNr:=TrialNr+1;
     END;
     AddArcsToCompl:=(TrialNr<=B.MaxTrials) AND
                     (arcs>=(B.Compl*(1-B.NetTol)*(ProInf.PI[pnr]+2)));
 END;


{************************************************************************}
{***** task: scanning the complete network for redundant arcs       *****}
{************************************************************************}

FUNCTION NoRedund(VAR P:Project) : BOOLEAN;

VAR i,j,k : INTEGER;

BEGIN
  NoRedund:=TRUE;
  FOR i:=1 TO P.NrOfJobs-1 DO
    FOR j:=i+1 TO P.NrOfJobs DO
      IF (j IN TD[i].DirSucc) THEN
        FOR k:=i+1 TO j-1 DO
          IF (k IN TD[i].DirSucc) THEN
            IF (j IN TD[k].InDirSucc) THEN
              NoRedund:=FALSE;
END;

{************************************************************************}
{***** mainpart GenNetwork                                          *****}
{************************************************************************}

BEGIN
  TrialNr:=1;
  PI.NrOfPro :=P.NrOfPro;
  PI.NrOfJobs:=P.NrOfJobs;
  CalcStartAndFinJobs(x,B,PI);
  InitNetw(1,P.NrOfJobs);
  pnr:=1;
  WHILE pnr<=P.NrOfPro DO
    BEGIN
    TrialNr :=1;
    success:=FALSE;
    WHILE NOT(success) AND (TrialNr<=B.MaxTrials) DO
      BEGIN
      success:=TRUE;
      PI.NSJ[pnr]  := Laplace(x,B.MinOutSour,B.MaxOutSour);
      PI.NFJ[pnr]  := Laplace(x,B.MinInSink,B.MaxInSink);
      arcs:=PI.NSJ[pnr]+PI.NFJ[pnr];
      ErrorBreak(efp,NOT(AddPred(x,B,PI,pnr)),success,1);
      ErrorBreak(efp,NOT(AddSucc(x,B,PI,pnr)),success,2);
      ErrorBreak(efp,arcs>(1+B.NetTol)*B.Compl*(PI.PI[pnr]+2),success,4);
      ErrorBreak(efp,NOT(AddArcsToCompl(x,B,PI,pnr)),success,3);
      IF NOT(success) THEN
        BEGIN
        TrialNr:=TrialNr+1;
        InitNetw(PI.SJ[pnr],PI.FJ[pnr]);
        END;
      END;
      ErrorBreak(efp,TrialNr>B.MaxTrials,success,1000);
      IF success THEN
        pnr:=pnr+1;
    END;
  AddArcsToSourceASink(B,PI);
  ErrorBreak(efp,NOT(NoRedund(P)),success,1001);
END;

{-------------------------------------------------------------------------}

BEGIN
END.
