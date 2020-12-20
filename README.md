# Nessus_Automation
This repository contains scripts to use Nessus from the command line. Features such as creating, stopping, status checking and outputting.


# nessus_refer.py Options
```
usage: nessus_refer.py [-h] [--targets TARGETS] [--name NAME] [--status STATUS] [--stop STOP] [--export EXPORT]
                       [--output OUTPUT] [--list]

Nessus API. Functionality: Start, Check Status and Download.
Following Options:
        Create Scan: python3 nessus.py -t google.com -n Google_Scan
        Stop Scan: python3 nessus.py -x 219
        Status Scan: python3 nessus.py -s 219
        List Scans: python3 nessus.py -l
        Output Scan: python3 nessus.py -e nessus -o /home/scutter/Reports/blah.nessus

optional arguments:
  -h, --help            show this help message and exit
  --targets TARGETS, -t TARGETS
                        Target list. This can be a file or directory.
  --name NAME, -n NAME  Name of scan.
  --status STATUS, -s STATUS
                        Current status of scan using ID.
  --stop STOP, -x STOP  Stops scan using ID.
  --export EXPORT, -e EXPORT
                        Export options: Nessus, HTML, PDF, CSV, or DB.
  --output OUTPUT, -o OUTPUT
                        Ouput path.
  --list, -l            List Scans with their IDs
```
