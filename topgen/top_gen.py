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
            try:
                self.portlist.append(PortArg(Identifier(port.first.name), Identifier(port.first.name)))
            #The port does not have first attribute, but it still contains the name.
            except AttributeError:
                self.portlist.append(PortArg(Identifier(port.name), Identifier(port.name)))
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



def writeToFile(output, top_gen_output_path, top_modul_name):
    output_path = ""
    for element in top_gen_output_path:
        output_path += element + "/"

    f = open(output_path + top_modul_name, 'w+')
    if (f.readlines() != ""):
        f.write("")
    f.close()

    f = open(output_path + top_modul_name, 'a')
    f.write(output)
    f.close()

class SourcePreparations(object):

    system_path = ""
    core_path = ""
    source_list = []

    def __init__(self, name):
        self.name = name
        self.setEnvironment()
        self.lookForSource()

    def setEnvironment(self):
        home_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))
        fusesoc_confing_path = home_path + "/.config/fusesoc/fusesoc.conf"
        fusesoc_conf_file = open(fusesoc_confing_path, "r")
        data_path = []

        for line in fusesoc_conf_file:
            data_path.append(line)

        self.system_path = "/" + str(data_path[1]).split(sep="/", maxsplit=1).pop()[:-1]
        self.core_path = "/" + str(data_path[2]).split(sep="/", maxsplit=1).pop()[:-1]



    def lookForSource(self):
        core_exist = False
        source_exist = False
        iter_for_inst_rank_clear = 0
        for source in self.name:
            # Look for source file
            print(self.core_path)
            for file in os.listdir(self.core_path):
                if file == source:
                    core_exist = True
                    break
                else:
                    core_exist = False


            if core_exist:
                # .v file -> use it immediately
                # .core file -> look for repositories
                for file in os.listdir(self.core_path + "/" + source):
                    if file.endswith(".v"):
                        self.source_list.append(self.core_path + "/" + source + "/" + source + ".v")
                        source_exist = True
                    elif file.endswith(".core"):
                        topgen.repo_clone.Repo_clone(self.core_path + "/" + source + "/" + file)
                        for element in topgen.repo_clone.Repo_clone.source_list:
                            self.source_list.append(element)
                        topgen.repo_clone.Repo_clone.source_list = []
                        source_exist = True
            else:
                print(source + ": No such core.")

            if not source_exist:
                print(source + ": Neither .core file nor .v files exist!")


            #Delete the parameters if we couldn't find the source
            if not source_exist or not core_exist:
                del topgen.handleConfFile.instantiation_name[iter_for_inst_rank_clear]
                del topgen.handleConfFile.rank[iter_for_inst_rank_clear]

            iter_for_inst_rank_clear += 1



def findTopGen(tr):
    # Find modul nodes
    if isinstance(tr, ModuleDef):
        moduleNode = IPNode(tr)
        return moduleNode
    for child in tr.children():
        return findTopGen(child)


def top_gen_main(top_gen_conf_path):
    top_gen_output_path = top_gen_conf_path.split("/")[:-1]
    top_modul_name = input("Give the top modul's name (with extension): ")
    output = ""
    # Open configuration file
    topgen.handleConfFile.processConfFile(top_gen_conf_path)
    # Set the environment and look for source files
    sourcePreparations = SourcePreparations(topgen.handleConfFile.module_name)
    # Instantiation from the source list
    for source in range(len(sourcePreparations.source_list)):
        codeParser = VerilogCodeParser(filelist=[sourcePreparations.source_list[source]])
        sAst = codeParser.parse()
        moduleNode = findTopGen(sAst)
        output += moduleNode.instantiate(topgen.handleConfFile.instantiation_name[source], topgen.handleConfFile.rank[source])
    # Create the top.v file
    writeToFile(output, top_gen_output_path, top_modul_name)

top_gen_main("/home/murai/openrisc/orpsoc-cores-ng/systems/logsys_spartan_6/top_generating/top.txt")