'''
@author: janosmurai
'''

from git import Repo
import os
import sys
import shutil
import re
from fusesoc.utils import Launcher
import fusesoc.provider.url

##########################################################################
# Not working if the top module's name is not equal with the core's name #
##########################################################################


class Repo_clone:
    name = ""
    repo_name = ""
    repo_root = ""
    revision = ""
    user = ""
    repo = ""
    cachable = ""
    url = ""
    filetype = ""
    branch = ""
    version = ""
    source_list = []
    source_to_download = False

    def __init__(self, core_file):
        self.openCoreFile(core_file)

    def openCoreFile(self, core_file):
        provider = False
        f = open(core_file, "r")
        for line in f:
            if line == "[provider]\n":
                provider = True
                Repo_clone.source_to_download = True
            elif provider:
                # Set the repository parameters
                if line.startswith("name"):
                    Repo_clone.name = line.split("=").pop()[1:-1] # Returns with the right site of the "="
                elif line.startswith("repo_name"):
                    Repo_clone.repo_name = line.split("=").pop()[1:-1]
                elif line.startswith("repo_root"):
                    Repo_clone.repo_root = line.split("=").pop()[1:-1]
                elif line.startswith("revision"):
                    Repo_clone.revision = line.split("=").pop()[1:-1]
                elif line.startswith("user"):
                    Repo_clone.user = line.split("=").pop()[1:-1]
                elif line.startswith("repo"):
                    Repo_clone.repo = line.split("=").pop()[1:-1]
                elif line.startswith("cachable"):
                    Repo_clone.cachable = line.split("=").pop()[1:-1]
                elif line.startswith("url"):
                    Repo_clone.url = line.split("=").pop()[1:-1]
                elif line.startswith("filetype"):
                    Repo_clone.filetype = line.split("=").pop()[1:-1]
                elif line.startswith("branch"):
                    Repo_clone.branch = line.split("=").pop()[1:-1]
                elif line.startswith("version"):
                    Repo_clone.user = line.split("=").pop()[1:-1]
                elif line.startswith("["):
                    provider = False
        if Repo_clone.source_to_download:
            if Repo_clone.name == "opencores":
                # Repository is available from the opencores SVN
                Repo_clone.cloneOpencores(self)
            elif Repo_clone.name == "github":
                # Repository is available from github
                Repo_clone.cloneGitHub(self)
            elif Repo_clone.name == "url":
                # Repository is available from other source
                Repo_clone.cloneFromURL(self)
            else:
                print("Unknown name for provider")
        else:
            print(core_file + ": No source to download")
            return

    # IDK if it is a good idea to work in th /tmp folder...
    def cloneGitHub(self):
        for file in os.listdir("/tmp/top_gen_fusesoc/git_test/"):
            if file == Repo_clone.repo:
                shutil.rmtree("/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo))


        try:
            Repo.clone_from("https://github.com/{user}/{repo}".format(user=Repo_clone.user, repo=Repo_clone.repo),
                            "/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo))
        except:
            is_manual_url = input("We couldn't find the source files defined in the " + Repo_clone.repo + " core file.\n Would you like to add the URL manually? (y/n)\n")
            if re.match(r"[yY][eE][sS]", is_manual_url) or is_manual_url == "y":
                manual_url = input("Please add the URL: ")
                try:
                    Repo.clone_from(manual_url, "/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo))
                except:
                    print("We couldn't find the source files.\nThe core will be skipped")
            else:
                print("We skipped the " + Repo_clone.repo + " core. Please fix the top gen config and .core files to make this core work")


        # Add files to source list
        for root, dirs, files in os.walk("/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo), topdown=False, onerror=None, followlinks=False):
            for file in files:
                if file == (self.repo + ".v"):
                    self.source_list.append(os.path.join(root, file))
                    print(file)

    def cloneOpencores(self):
        repo_path = 'http://opencores.org/ocsvn/' + \
            self.repo_name + '/' + self.repo_name + '/' + \
            self.repo_root

        try:
            Launcher('svn', ['co', '-q', '--no-auth-cache',
                             '-r', self.revision,
                             '--username', 'orpsoc',
                             '--password', 'orpsoc',
                             repo_path,
                             "/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=self.repo_name)]).run()
        except:
            is_manual_url = input("We couldn't find the source files defined in the " + self.repo_name + " core file.\n Would you like to add the URL manually? (y/n)\n")
            if re.match(r"[yY][eE][sS]", is_manual_url) or is_manual_url == "y":
                manual_url = input("Please add the URL: ")
                try:
                    Launcher('svn', ['co', '-q', '--no-auth-cache',
                             '-r', self.revision,
                             '--username', 'orpsoc',
                             '--password', 'orpsoc',
                             manual_url,
                             "/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=self.repo_name)]).run()
                except:
                    print("We couldn't find the source files.\nThe core will be skipped.")
            else:
                print("We skipped the " + Repo_clone.repo + " core. Please fix the top gen config and .core files to make this core work")


        # Add files to source list
        for root, dirs, files in os.walk("/tmp/top_gen_fusesoc/git_test/{dir}".format(dir=self.repo_name), topdown=False, onerror=None, followlinks=False):
            for file in files:
                if file == (self.repo_name + ".v"):
                    self.source_list.append(os.path.join(root, file))
                    print(file)

    def cloneFromURL(self):

        print("Downloading from the given URL is not working yet.\n" + \
              "Please download the source manually and in the .core file set the src_files equal with them.")