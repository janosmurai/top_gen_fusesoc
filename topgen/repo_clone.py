'''
@author: janosmurai
'''

import tarfile
import urllib
import zipfile
from git import Repo
import os
import sys
import shutil

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
            print("No source to download")
            return

    def cloneGitHub(self):
        for file in os.listdir("/home/murai/openrisc/top_gen_fusesoc/git_test/"):
            if file == Repo_clone.repo:
                shutil.rmtree("/home/murai/openrisc/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo))


        Repo.clone_from("https://github.com/{user}/{repo}".format(user=Repo_clone.user, repo=Repo_clone.repo),
                        "/home/murai/openrisc/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo))
                        
        #TODO: Ha nem találja git-en meglehessen adni URL-t
        #TODO: AZ add files to source list részt külön fv-be kirakni

        # Add files to source list
        for root, dirs, files in os.walk("/home/murai/openrisc/top_gen_fusesoc/git_test/{dir}".format(dir=Repo_clone.repo), topdown=False, onerror=None, followlinks=False):
            for file in files:
                if file == (self.repo + ".v"):
                    self.source_list.append(os.path.join(root, file))
                    print(file)

    def cloneOpencores(self):
        repo_path = 'http://opencores.org/ocsvn/' + \
            self.repo_name + '/' + self.repo_name + '/' + \
            self.repo_root

        # Launcher('svn', ['co', '-q', '--no-auth-cache',
        #                  '-r', self.revision,
        #                  '--username', 'orpsoc',
        #                  '--password', 'orpsoc',
        #                  repo_path,
        #                  "/home/murai/openrisc/top_gen_fusesoc/git_test/{dir}".format(dir=self.repo_name)]).run()
        
        #TODO: Ha a repo nem található akkor kérjen URL-t, vagy skippelje ezt a core fájlt. Nyilván az utólag megadott URL a cloneFromURL-t hívja meg!

        # Add files to source list
        for root, dirs, files in os.walk("/home/murai/openrisc/top_gen_fusesoc/git_test/{dir}".format(dir=self.repo_name), topdown=False, onerror=None, followlinks=False):
            for file in files:
                if file == (self.repo_name + ".v"):
                    self.source_list.append(os.path.join(root, file))
                    print(file)

    def cloneFromURL(self):
        try:
            (filename, headers) = urllib.urlretrieve(self.url)
        except urllib.URLError:
            raise
        except urllib.HTTPError:
            raise

        url = self.url.split("/")
        source_name = url.pop()
        url.pop()
        path_to_copy = "/home/murai/openrisc/top_gen_fusesoc/git_test/{dir}".format(dir=url.pop())
        if not os.path.exists(path_to_copy):
            os.makedirs(path_to_copy)
            os.makedirs(path_to_copy + "/rtl")
        path_to_copy += "/rtl"

        if self.filetype == 'tar':
            # Source is *.tar
            t = tarfile.open(filename)
            t.extractall(path_to_copy)
        elif self.filetype == 'zip':
            # Source is *.zip
            with zipfile.ZipFile(filename, "r") as z:
                z.extractall(path_to_copy)
        elif self.filetype == 'simple':
            # Source is *.v
            shutil.copy2(filename, path_to_copy)
        else:
            # Unknown file type
            raise RuntimeError("Unknown file type '" + self.filetype + "' in [provider] section")
            
        #TODO: Ha nem találja lehessen újat megadni, vagy skippelni a core fájlt

        # Add files to source list
        for root, dirs, files in os.walk(path_to_copy, topdown=False, onerror=None, followlinks=False):
            for file in files:
                if file == source_name:
                    self.source_list.append(os.path.join(root, file))
                    print(file)
