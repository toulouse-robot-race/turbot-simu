# TurboDroid simulation

## What is it?

Simulation of TurboDroid robot on the Toulouse Robot Race Track.

## Installation

You will need to install the V-Rep robot simulator:
http://www.coppeliarobotics.com/downloads.html

You will also need python3 and some python libraries. We recommend that you install python with Anaconda.
https://www.anaconda.com/distribution/#download-section

You will also need the BlueZero library and its dependancies. On Windows, you can get all the needed dlls in V-Rep installation directory. Create a working directory, and copy/paste the following dlls in this working directory:

* b0.dll
* boost_date_time-vc141-mt-x64-1_68.dll
* boost_filesystem-vc141-mt-x64-1_68.dll
* boost_program_options-vc141-mt-x64-1_68.dll
* boost_regex-vc141-mt-x64-1_68.dll
* boost_serialization-vc141-mt-x64-1_68.dll
* boost_system-vc141-mt-x64-1_68.dll
* boost_thread-vc141-mt-x64-1_68.dll
* libzmq-mt-4_3_1.dll
* zlib1.dll

## Usage

This is the procedure for Windows (see above for the b0 dependancies). On Linux and MacOS, the procedure for getting the BlueZero dependancies differs.

First, open the turbodroid.ttt file in the V-REP simulator.

Then, launch:
```console
cd MY_WORKING_DIRECTORY_CONTAINING_THE_BLUEZERO_DLLs
python PATH_TO_THE_PROJECT\launch_robot_simu.py
```

That's all, you should see the robot moving in the simulator!

You can then edit the python files to create your own code to command TurboDroid.

## Licence

Copyright 2018 - Lior Perez & Cédric Franck

This content is shared by Lior Perez and Cédric Franck under the Apache 2.0 licence.