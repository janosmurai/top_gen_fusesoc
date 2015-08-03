'''
@author: wachag, janosmurai
'''
#from ihooks import _Verbose
import os

import topgen.handleConfFile
import topgen.repo_clone
from pyverilog.vparser.parser import VerilogCodeParser
from pyverilog.vparser.ast import ModuleDef, Parameter, Identifier, ParamArg, PortArg, Instance
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator



class IPNode:
    parameters = []
    ports = []
    name = ""
    connections_to_file = []
    val = ""
    
    def __init__(self, moduleNode):

        self.name = moduleNode.name
        self.portlist = []
        self.paramlist = []
        for port in moduleNode.portlist.ports:
            self.portlist.append(PortArg(Identifier(port.first.name), Identifier(port.first.name)))
        for item in moduleNode.paramlist.params:
            self.findParameters(item, self.parameters)
        for item in moduleNode.items:
            self.findParameters(item, self.parameters)

    def findParameters(self, node, lst):
        if isinstance(node, Parameter):
            var = node.value.var
            cg = ASTCodeGenerator()
            val = cg.visit(var)
            self.paramlist.append(ParamArg(Identifier(node.name), var))
            lst.append((node.name, val))
        for child in node.children():
            self.findParameters(child, lst)
        return lst

    def instantiate(self, instanceName, rank):
        val = ""
        inst = Instance(self.name, instanceName, self.portlist, self.paramlist)
        for line in inst.portlist:
            if (line.argname.name != "wb_clk") & (line.argname.name != "wb_rst") & line.argname.name.startswith("wb"):
                if rank == "slave":
                    if line.argname.name.endswith("i"):
                        line.argname.name = "wb_m2s_{modul_name}_{port}".format(modul_name=self.name,
                                                                                port=line.argname.name[3:-2])
                    else:
                        line.argname.name = "wb_s2m_{modul_name}_{port}".format(modul_name=self.name,
                                                                                port=line.argname.name[3:-2])
                else:
                    if line.argname.name.endswith("o"):
                        line.argname.name = "wb_m2s_{modul_name}_{port}".format(modul_name=self.name,
                                                                                port=line.argname.name[3:-2])
                    else:
                        line.argname.name = "wb_s2m_{modul_name}_{port}".format(modul_name=self.name,
                                                                                port=line.argname.name[3:-2])
        # Call the code generator
        cg = ASTCodeGenerator()
        val = cg.visit(inst)
        val += "\n\n"
        print(rank)
        print(val)
        return val

def writeToFile(output):
    f = open('/home/murai/openrisc/orpsoc-cores-ng/systems/logsys_spartan_6/top_generating/top.v', 'r+')
    if (f.readlines() != ""):
        f.write("")
    f.close()

    f = open('/home/murai/openrisc/orpsoc-cores-ng/systems/logsys_spartan_6/top_generating/top.v', 'a')
    f.write(output)
    f.close()




def lookForSource(name):
    source_list = []
    core_exist = False
    for source in name:
        # Look for source file
        for file in os.listdir(
                "/home/murai/openrisc/orpsoc-cores-ng/cores"):  # TODO: The path comes from the fusesoc.conf file
            if file == source:
                core_exist = True
                break
            else:
                core_exist = False

        if core_exist == True:
            # .v file -> use it immediately
            # .core file -> look for repositories
            for file in os.listdir("/home/murai/openrisc/orpsoc-cores-ng/cores/" + source):
                if file.endswith(".v"):
                    source_list.append("/home/murai/openrisc/orpsoc-cores-ng/cores/" + source + "/" + source + ".v")
                elif file.endswith(".core"):
                    topgen.repo_clone.Repo_clone("/home/murai/openrisc/orpsoc-cores-ng/cores/" + source + "/" + file)
                    for element in topgen.repo_clone.Repo_clone.source_list:
                        source_list.append(element)
                    topgen.repo_clone.Repo_clone.source_list = []
                else:
                    print("Neither core file nor source files exist!")
            core_exist = False
    return source_list


def findTopGen(tr):
    # Find modul nodes
    if isinstance(tr, ModuleDef):
        moduleNode = IPNode(tr)
        return moduleNode
    for child in tr.children():
        return findTopGen(child)


def top_gen_main():
    print("called")
    source_list = []
    output = ""
    # Open configuration file
    topgen.handleConfFile.processConfFile("/home/murai/openrisc/orpsoc-cores-ng/systems/logsys_spartan_6/top_generating/top.txt")
    # # Look for source files
    source_list = lookForSource(topgen.handleConfFile.module_name)
    print(source_list)
    # Instantiation from the source list
    for source in range(len(source_list)):
        codeParser = VerilogCodeParser(filelist=[source_list[source]])
        sAst = codeParser.parse()
        moduleNode = findTopGen(sAst)
        output += moduleNode.instantiate(topgen.handleConfFile.instantiation_name[source], topgen.handleConfFile.rank[source])
    # Create the top.v file
    writeToFile(output)

top_gen_main()