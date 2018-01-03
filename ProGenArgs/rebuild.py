import os
import cleanup

cleanup.main()
os.system('fpc -Mtp ProGen.pas')
cleanup.main()
