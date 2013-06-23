## ArmaBriefingConversion ##


This program batch upconverts old OFP and Arma style missions
to the new briefing system used in Arma2.  It parses
the briefing.html file and pulls out the appropriate
sections and creates a briefing.sqf file.  Debriefing
is still kept and saved to a new briefing.html file.


### Requirements: ###

[Python](http://www.python.org) 2.7 or greater


### How-to-run: ###

This program will process ALL missions in the folder you specify.
It's recursive so this means all folders, subfolders, etc.

Open a commandline terminal and change directory to the location
of ArmaBriefingConversion.  Then type the following:

```
python run.py /full_path_to_missions_folder/ /empty_folder_for_converted_missions/
```

I would recommend using full paths as opposed to relative.


__I'm not responsible for lost missions or issues. Make
backups!  You have been warned.__


### Troubleshooting ###

"This doesn't work for my mission..."

I'm not surprised... the briefing HTML is difficult to parse.
The program relies heavily on regular expressions.  Many missions
were created with incorrect or poorly formatted HTML.  If you
have suggestions for how to improve the program, fork it on Github
and submit a pull request with the change.



### BIS Documentation: ###

- [Briefing.html](http://community.bistudio.com/wiki/Briefing.html)

- [createDiaryRecord](http://community.bistudio.com/wiki/createDiaryRecord)

- [createSimpleTask](http://community.bistudio.com/wiki/createSimpleTask)

- [Debriefing](http://community.bistudio.com/wiki/Debriefing)

- [Briefing](http://community.bistudio.com/wiki/briefing)

- [setSimpleTaskDescription](http://community.bistudio.com/wiki/setSimpleTaskDescription)