'''
@author: janosmurai
'''

import sys
import os


rank = []
module_name = []
instantiation_name = []


def processConfFile(conf_file_location):
    conf_file = open(conf_file_location, "r")
    for line in conf_file:
        if line.startswith("[") & line.endswith("]\n"):
            if line[1:-2] == "slave":
                # Module is a slave
                rank.append("slave")
            elif line[1:-2] == "master":
                # Module is a master
                rank.append("master")
            else:
                print("Rank must be slave or master")
        elif line.startswith("modul_name"):
            module_name.append(line.split("=").pop()[1:-1])
        elif line.startswith("instantiation_name"):
            instantiation_name.append(line.split("=").pop()[1:-1])
        else:
            print("Syntax error in the conf file")

