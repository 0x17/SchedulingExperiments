{********************************************************************}
{***** mainprogram project generation                           *****}
{********************************************************************}

{***** Compiler Options *********************************************}
{$A+} {word align data            }
{$B+} {complete boolean evaluation}
{$D+} {debug information          }
{$E-} {emulation                  }
{$F-} {force for calls            }
{$G-} {286 instructions           }
{$H-} {do not use ansi strings}
{$I+} {I/O checking               }
{$L+} {local symbols              }
{$N-} {8087/80287                 }
{$O-} {overlays allowed           }
{$R+} {range checking             }
{$S+} {stack checking             }
{$V+} {strict var strings         }
{$X+} {extended syntax            }
{********************************************************************}

PROGRAM ProGen;

USES CRT,DOS,
     TypeDecl,   { type declaration                                  }
     NetwGen ,   { network generation                                }
     AvailGen,   { resource availability                             }
     ReqGen  ,   { resource request                                  }
     InOut   ,   { input and output                                  }
     Utility, SysUtils;

VAR P:Project;



{********************************************************************}
{*** function name: Project Generation                               }
{*** called by    : menue                                            }
{*** calling   : GetInfo,GenProjData,WriteProjData,GenNetWork        }
{***             ResReqMain,ResAvlMain,WriteReq,WriteAvaill,Replicate}
{********************************************************************}

PROCEDURE GenProj(SI:SampleInfo;VAR P:Project);

VAR
     exnr      : INTEGER     ;   { actual example number         }
     exnrstr   : STRING [4]  ;   { exnr converted to string      }
     Fname     : STRING [12] ;   { examples filename             }
     EFname    : STRING [12] ;   { error filename                }
     D         : DFILES      ;   { filepointer error/sample file }
     x1        : LONGINT     ;   { initial value random numbers  }
     x2        : LONGINT     ;   { copy of initial values        }
     A         : Availability;
     TreeData  : TreeStruct  ;
     PI        : ProjectInfo ;
     T         : Time        ;
     success   : BOOLEAN     ;
BEGIN
  IF FindFile(SI.DFile) THEN
    EXIT;
  exnr:=1;
  IF SI.InVal=0 THEN
    x1:= RANDOM(31918)
  ELSE
    x1:= SI.InVal;
  x2:=x1;
  EFName:=SI.DFile+'.'+'ERR';
  ASSIGN(D.efp,EFName);
  REWRITE(D.efp);
  WHILE exnr<=SI.NrOfEx DO
    BEGIN
    WRITELN ('number ',exnr);
    STR (exnr,exnrstr);
    Fname := SI.DFile + exnrstr + '.sm';
    Replicate(D.efp,72,'-');
    WRITELN(D.efp,'sample file -->',FName);
    Replicate(D.efp,72,'-');
{*********************************************************}
{***** generate project                              *****}
{*********************************************************}
    GenProjData(x1,SI.B,P);
    GenNetwork(D.efp,x1,SI.B,P,PI,TreeData,success);
    IF success THEN
      BEGIN
       CalcCPMTimes(P,PI,TreeData,T,'d',0);
       CalcDueDates(SI.B,P,PI);
       ResReqMain(D.efp,x1,SI.B,P);
       ResAvlMain(P,PI,SI.B,TreeData,A);
{********************************************************}
{***** write project to file                        *****}
{********************************************************}
       ASSIGN (D.fp, Fname);
       REWRITE (D.fp);
       WriteProjData(D.fp,x2,SI.BFile,P);
       WriteNetwToFile(D.fp,P,TreeData);
       WriteReq(D.fp,P);
       WriteAvail(D.fp,A,P);
       CLOSE (D.fp);
       x2:=x1;
       exnr:=exnr+1;
      END;
    END;
  CLOSE(D.efp);
END;


{***************************************************************************}
{**** called by: Menue                                                      }
{**** task     : shows main menue                                           }
{***************************************************************************}

PROCEDURE ShowMenue(SI : SampleInfo);

BEGIN
  CLRSCR;
  WRITELN('=====================================================');
  WRITELN('PROGEN2.0 - Generator For Project Scheduling Problems');
  WRITELN('=====================================================');
  WRITELN;
  WRITELN('file basedata                : ',SI.BFile);
  IF SI.InVal=0 THEN
    WRITELN('initial valuse               : randomly')
  ELSE
    WRITELN('initial value                :    ',SI.InVal:5);
  WRITELN('number of instances          :    ',SI.NrOfEx:5);
  WRITELN;
  WRITELN('1 - basedata              ');
  WRITELN('2 - initial value         ');
  WRITELN('3 - number of instances   ');
  WRITELN('4 - generate              ');
  WRITELN('5 - end program           ');
  WRITELN;
  WRITE  ('--> ');
END;

{********************************************************************}
{**** called by: main                                                }
{**** task     : acts on menue selection                             }
{********************************************************************}

PROCEDURE Menue;

VAR  Taste      : INTEGER;       { menue selection            }
     SI         : SampleInfo;
     new        : BOOLEAN;

BEGIN
  RANDOMIZE;
  SI.BFile :='no basefile';
  SI.InVal := 0;
  SI.DExt  := 'DAT';
  SI.NrOfEx:= 10;
  REPEAT
    ShowMenue(SI);
    READLN(Taste);
    WRITELN;
    WRITELN;
    CASE Taste OF
      1 : BEGIN
          GetBaseDataFromUser(SI.B,SI.BFile,P);
          FSplit(SI.BFile,SI.DDir,SI.DFile,SI.DExt);
          END;
      2 : BEGIN
          WRITE('initial value  : ');
          READ(SI.InVal);
          END;
      3 : BEGIN
          WRITE('number of instances : ');
          READ(SI.NrOfEx);
          END;
      4 : GenProj(SI,P);
    END;
  UNTIL Taste=5;
END;

{********************************************************************}

procedure ShowUsage;
begin
	WriteLn('Usage 1: ProGen base_filename [num_instances=10] [initial_value=rand]');
	WriteLn('Example: ProGen EXPL.BAS 10 23');
	WriteLn('Usage 2: ProGen show_menu');
end;

procedure RunWithArgs(baseFilename: String; numInstances: Integer; initialValue: Integer);
var si: SampleInfo;
begin
	randomize;
	
	si.BFile := baseFilename;
	GetBaseData(SI.B,SI.BFile,P);
    FSplit(SI.BFile,SI.DDir,SI.DFile,SI.DExt);
	
	si.InVal := initialValue;
	si.DExt := 'DAT';
	si.NrOfEx:= numInstances;
	GenProj(si,P);
end;

procedure ParseArgs;
var
	baseFilename: String;
	numInstances, initialValue: Integer;
begin
	if ParamCount = 0 then begin
		ShowUsage;
		exit;
	end;
	
	if ParamStr(1) = 'show_menu' then begin
		Menue;
		exit;
	end;
	
	baseFilename := ParamStr(1);
	
	if ParamCount > 1 then numInstances := StrToInt(ParamStr(2))
	else numInstances := 10;
	
	if ParamCount > 2 then initialValue := StrToInt(ParamStr(3))
	else initialValue := 0;
	
	RunWithArgs(baseFilename, numInstances, initialValue);
end;

{********************************************************************}
{**** main                                                           }
{********************************************************************}

BEGIN
  {Menue}
  ParseArgs;
END.


{ --------------------------------- Ende ---------------------------------- }
