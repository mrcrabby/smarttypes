

import subprocess, os
cmd = subprocess.Popen('ps -ef | grep ssh', shell=True, stdout=subprocess.PIPE)

in_there = False
for line in cmd.stdout:
    if "5432:localhost:5432" in line:
        in_there = True

if not in_there:
    os.system('ssh timmyt@96.11.60.42 -N -f -L 5432:localhost:5432')
    print 'setup ssh db tunnel'


