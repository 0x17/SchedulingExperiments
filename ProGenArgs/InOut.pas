{********************************************************************}
{***** input output                                             *****}
{********************************************************************}
UNIT InOut;

INTERFACE

USES  Crt,TypeDecl;


PROCEDURE WriteReq(VAR fp:TEXT;VAR P:Project);
PROCEDURE WriteProjData(VAR fp:TEXT;VAR x:LONGINT;BaseFile :STRING;VAR P:Project);
PROCEDURE WriteAvail(VAR fp:TEXT;VAR A: Availability;VAR P:Project);
PROCEDURE Replicate(VAR fp:TEXT;n:integer;ch:char);
PROCEDURE GetInfo(VAR nrofex :INTEGER;VAR exfname :STRING;VAR exfext :STRING);
PROCEDURE GetBaseDataFromUser (VAR B :BaseStruct;VAR fname :STRING;VAR P:Project);
PROCEDURE GetBaseData (VAR B :BaseStruct;VAR fname :STRING;VAR P:Project);

IMPLEMENTATION

{********************************************************************}
{**** task: writes char ch n times to file  fp                    ***}
{********************************************************************}

PROCEDURE Replicate(VAR fp:Text;n:integer;ch:char);

VAR i:integer;

BEGIN
FOR i:=1 TO n DO
  write(fp,ch);
writeln(fp)
END;

{********************************************************************}
{****  task     : reads file from actual position to char c          }
{****  called by: GetBaseData                                        }
{********************************************************************}

PROCEDURE ReadFileToChar(VAR fp:TEXT;c: CHAR);

VAR  c1: CHAR;
BEGIN
REPEAT
read(fp,c1);
UNTIL c=c1;
END;

{********************************************************************}
{**** task   : reads info from file                                  }
{********************************************************************}

PROCEDURE GetInfo(VAR nrofex :INTEGER;VAR exfname :STRING;VAR exfext :STRING);

BEGIN
WRITE('number of instances  : ');
READLN (nrofex);
WRITELN;
WRITELN('format of filename:  [name][number].[extension]');
WRITE  ('[name]:      ');
READLN (exfname);
WRITE  ('[extension]: ');
READLN (exfext);
WRITELN;
END;


{********************************************************************}
{**** task    :  get base data from file                        *****}
{********************************************************************}

procedure GetBaseDataFromUser (VAR B :BaseStruct; VAR fname :STRING;VAR P:Project);
begin
	Write('basefiles name: ');
	ReadLn(fname);
	GetBaseData(b, fname, p);
end;

{********************************************************************}

PROCEDURE GetBaseData (VAR B :BaseStruct; VAR fname :STRING;VAR P:Project);
VAR  fp : TEXT;
     i  : INTEGER;
BEGIN  
  ASSIGN (fp,fname);
  RESET  (fp);
  WITH B DO
  BEGIN
    ReadFileToChar(fp,':');Read(fp,NrOfPro);
    ReadFileToChar(fp,':');Read(fp,MinJob);
    ReadFileToChar(fp,':');Read(fp,MaxJob);
    ReadFileToChar(fp,':');Read(fp,MaxRel);
    ReadFileToChar(fp,':');Read(fp,DueDateFac);
    ReadFileToChar(fp,':');Read(fp,MinMode);
    ReadFileToChar(fp,':');Read(fp,MaxMode);
    ReadFileToChar(fp,':');Read(fp,MinDur);
    ReadFileToChar(fp,':');Read(fp,MaxDur);
    ReadFileToChar(fp,':');Read(fp,MinOutSour);
    ReadFileToChar(fp,':');Read(fp,MaxOutSour);
    ReadFileToChar(fp,':');Read(fp,MaxOut);
    ReadFileToChar(fp,':');Read(fp,MinInSink);
    ReadFileToChar(fp,':');Read(fp,MaxInSink);
    ReadFileToChar(fp,':');Read(fp,MaxIn);
    ReadFileToChar(fp,':');Read(fp,Compl);
    ReadFileToChar(fp,':');Read(fp,MinRen);
    ReadFileToChar(fp,':');Read(fp,MaxRen);
    ReadFileToChar(fp,':');Read(fp,MinRReq);
    ReadFileToChar(fp,':');Read(fp,MaxRReq);
    ReadFileToChar(fp,':');Read(fp,MinRRU);
    ReadFileToChar(fp,':');Read(fp,MaxRRU);
    ReadFileToChar(fp,':');Read(fp,RRF);
    ReadFileToChar(fp,':');Read(fp,RRS);
    ReadFileToChar(fp,':');Read(fp,NrOfRFunc);
    FOR i:=1 TO NrOfRFunc DO
      BEGIN
      ReadFileToChar(fp,':');Read(fp,RFuncProb[i])
      END;
    ReadFileToChar(fp,':');Read(fp,MinNon);
    ReadFileToChar(fp,':');Read(fp,MaxNon);
    ReadFileToChar(fp,':');Read(fp,MinNReq);
    ReadFileToChar(fp,':');Read(fp,MaxNReq);
    ReadFileToChar(fp,':');Read(fp,MinNRU);
    ReadFileToChar(fp,':');Read(fp,MaxNRU);
    ReadFileToChar(fp,':');Read(fp,NRF);
    ReadFileToChar(fp,':');Read(fp,NRS);
    ReadFileToChar(fp,':');Read(fp,NrOfNFunc);
    FOR i:=1 TO NrOfNFunc DO
      BEGIN
      ReadFileToChar(fp,':');Read(fp,NFuncProb[i])
      END;
    ReadFileToChar(fp,':');Read(fp,MinDou);
    ReadFileToChar(fp,':');Read(fp,MaxDou);
    ReadFileToChar(fp,':');Read(fp,MinDReq);
    ReadFileToChar(fp,':');Read(fp,MaxDReq);
    ReadFileToChar(fp,':');Read(fp,MinDRU);
    ReadFileToChar(fp,':');Read(fp,MaxDRU);
    ReadFileToChar(fp,':');Read(fp,DRF);
    ReadFileToChar(fp,':');Read(fp,DRST);
    ReadFileToChar(fp,':');Read(fp,DRSP);
    ReadFileToChar(fp,':');Read(fp,NrOfDFunc);
    FOR i:=1 TO NrOfDFunc DO
      BEGIN
      ReadFileToChar(fp,':');Read(fp,DFuncProb[i]);
      END;
    ReadFileToChar(fp,':');Read(fp,NetTol);
    ReadFileToChar(fp,':');Read(fp,ReqTol);
    ReadFileToChar(fp,':');Read(fp,maxTrials);
  END;
  CLOSE(fp);
END;


{*************************************************************************}
{*****  task     : write projects base data to file                  *****}
{*****  called by: main                                              *****}
{*************************************************************************}

PROCEDURE WriteProjData(VAR fp:TEXT;VAR x:LONGINT;BaseFile :STRING;VAR P:Project);

VAR   pi    : INTEGER;

BEGIN
  Replicate(fp,72,'*');
  WRITELN (fp,'file with basedata            : ',BaseFile);
  WRITELN (fp,'initial value random generator: ',x);
  Replicate(fp,72,'*');
  WRITELN (fp,'projects                      :  ',P.NrOfPro);
  WRITELN (fp,'jobs (incl. supersource/sink ):  ',P.NrOfJobs);
  WRITELN (fp,'horizon                       :  ',P.Horizon);
  WRITELN (fp,'RESOURCES');
  WRITELN (fp,'  - renewable                 :  ',P.R,'   R');
  WRITELN (fp,'  - nonrenewable              :  ',P.N,'   N');
  WRITELN (fp,'  - doubly constrained        :  ',P.D,'   D');
  Replicate(fp,72,'*');
  WriteLn(fp,'PROJECT INFORMATION:');
  Writeln(fp,'pronr.  #jobs rel.date duedate tardcost  MPM-Time');
  for pi:=1 TO P.NrOfPro DO
    BEGIN
    write(fp,pi:5);
    write(fp,P.Pro[pi]:7);
    write(fp,P.RelDate[pi]:7);
    write(fp,P.DueDate[pi]:9);
    write(fp,P.TardCost[pi]:9);
    write(fp,P.CPMT[pi]:9);

    writeLn(fp);
    END;
  Replicate(fp,72,'*');
END;

{*************************************************************************}
{***** task     : write availability to file                         *****}
{***** called by: main                                               *****}
{*************************************************************************}
PROCEDURE WriteAvail(VAR fp:TEXT;VAR A: Availability;VAR P:Project);

VAR    i : INTEGER;
BEGIN
WriteLn(fp,'RESOURCEAVAILABILITIES:');
FOR i:=1 TO P.R DO
  Write(fp,'  R',i:2);
FOR i:=1 TO P.N DO
  Write(fp,'  N',i:2);
FOR i:= 1 TO P.D DO
  Write(fp,'    D',i:5);
WriteLn(fp);
FOR i:= 1 TO P.R DO
  Write(fp,A.RPer[i]:5);
FOR i:= 1 TO P.N DO
  Write(fp,A.NTot[i]:5);
FOR i:= 1 TO P.D DO
  BEGIN
  Write(fp,A.DTot[i]:5);
  Write(fp,A.DPer[i]:5);
  END;
WriteLn(fp);
Replicate(fp,72,'*');
END;


{********************************************************************}
{***** task: write request(durations) to file                    ****}
{********************************************************************}

PROCEDURE WriteReq(VAR fp:Text;VAR P:Project);

VAR       rj,nj,dj,j,m:integer;

BEGIN
WriteLn(fp,'REQUESTS/DURATIONS:');
Write(fp,'jobnr. mode duration');
WITH P DO
  BEGIN
  FOR rj:=1 TO R DO
    write(fp,'  R',rj:2);
  FOR nj:=1 TO N DO
    write(fp,'  N',nj:2);
  FOR dj:=1 TO D DO
    write(fp,'  D',dj:2);
  writeLn(fp);
  replicate(fp,72,'-');
  FOR j:=1 TO P.NrOfJobs DO
    BEGIN
    write(fp,j:3);
    write(fp,'  ');
    FOR m:=1 TO Job[j].NrOfModes DO
      BEGIN
      write(fp,m:5);
      write(fp,'    ');
      write(fp,P.Job[j].Mode[m].Duration:2);
      write(fp,'   ');
      FOR rj:=1 TO R DO
        write(fp,Job[j].Mode[m].RenResReq[rj]:5);
      FOR nj:=1 TO N DO
        write(fp,Job[j].Mode[m].NonResReq[nj]:5);
      FOR dj:=1 TO D DO
        write(fp,Job[j].Mode[m].DouResReq[dj]:5);
      writeLn(fp);
      IF m<Job[j].NrOfModes THEN
        write(fp,'     ');
      END;
    END;
  END;
replicate(fp,72,'*');
END;
{******************** BEGIN main  ***********************************}
BEGIN

END.
