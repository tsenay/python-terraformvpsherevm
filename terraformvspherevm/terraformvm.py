from python_terraform import *
from terraformvspherevm.terrascriptvspherevm import TerrascriptVSphereVM
from os import environ, pathsep, linesep
from os.path import exists, join, normpath
import socket


def search_file(filename, search_path):
    logger = logging.getLogger()
    file_found = 0
    paths = str.split(search_path, pathsep)
    for path in paths:
        if exists(join(path, filename)):
            file_found = 1
            break
    if file_found:
        logger.info("{} found at {}".format(
            filename,
            normpath(join(path, filename))))
        return True
    else:
        logger.error("{} not found".format(filename))
        return None


class TerraformVM:
    def __init__(self):
        find_file = search_file('terraform', environ['PATH'])
        if not find_file:
            raise Exception

        self.terraform = Terraform()
        self.tfstateFile = 'terraform.tfstate'
        self.tfstate = None
        try:
            fd = open(self.tfstateFile, 'r')
            self.tfstate = json.load(fd)
            fd.close()
        except FileNotFoundError:
            pass

        self.VmResources = {}

    def addVM(self, terrascriptvm):
        self.VmResources[terrascriptvm.name] = {
            "script": "{}.tf.json".format(terrascriptvm.name),
            "terrascript": terrascriptvm}

    def createTerraformConfigurationFiles(self, name):
        logger = logging.getLogger()
        logger.info("Create Terraform script '{}'".format(
            self.VmResources[name]['script']))
        self.VmResources[name]['terrascript'].saveConfiguration(
            self.VmResources[name]['script'])

    def cleanTerraformConfigurationFiles(self, name):
        logger = logging.getLogger()
        logger.info("Clean terraform configuration file {}".format(
            self.VmResources[name]['script']))
        os.unlink(self.VmResources[name]['script'])

    def isVmExistsInStateFile(self, name):
        if self.tfstate:
            try:
                for module in self.tfstate['modules']:
                    tfVm = module['resources']['vsphere_virtual_machine.vm']
                    tfName = tfVm['primary']['attributes']['name']
                    if tfName == name:
                        return True
            except KeyError:
                pass
        return False

    def tfInit(self):
        logger = logging.getLogger()
        logger.info("Init Terraform")
        return_code, stdout, stderr = self.terraform.init(
            input=False,
            no_color=IsFlagged)

    def createPlan(self, name):
        logger = logging.getLogger()
        planFile = "{}.plan".format(name)
        logger.info("Create Terraform plan '{}'".format(planFile))
        return_code, stdout, stderr = self.terraform.plan(
            out=planFile,
            input=False,
            no_color=IsFlagged)

        logger.debug(stdout)

        if return_code == 0:
            logger.warning("Nothing to create. Exit")
            exit(0)

        if return_code != 2:
            logger.error("Return Code: {}".format(return_code))
            logger.error(stderr)
            raise Exception

        self.VmResources[name]['planfile'] = planFile

    def deletePlan(self, name):
        logger = logging.getLogger()
        logger.debug("Remove file ''".format(
            self.VmResources[name]['planfile']))
        os.unlink(self.VmResources[name]['planfile'])
        del self.VmResources[name]['planfile']

    def applyPlan(self, name):
        logger = logging.getLogger()
        planFile = self.VmResources[name]['planfile']
        logger.info("Apply terraform plan '{}'".format(planFile))
        return_code, stdout, stderr = self.terraform.apply(
            planFile,
            input=False,
            no_color=IsFlagged)

        logger.debug(stdout)

        if return_code != 0:
            logger.error("Return Code: {}".format(return_code))
            logger.error(stderr)
            raise Exception
        logger.info("Virtual Machine created")

    def destroyResource(self, name):
        logger = logging.getLogger()
        logger.info("Destroy terraform Resource")
        return_code, stdout, stderr = self.terraform.destroy(
            input=False)
        logger.debug(stdout)

        if return_code != 0:
            logger.error("Return Code: {}".format(return_code))
            logger.error(stderr)
            raise Exception

    def importResource(self, name):
        logger = logging.getLogger
        logger.info("Import Ressource from vSphere")
        vmProperties = self.VmResources[name]['properties']
        self.terraform.import_cmd(
            "vsphere_virtual_machine.vm",
            "/{}/vm/{}/{}".format(
                vmProperties['datacenter'],
                vmProperties['folder'],
                vmProperties['name']))

    def createVM(self, name):
        self.createTerraformConfigurationFiles(name)
        self.tfInit()
        self.createPlan(name)
        self.applyPlan(name)
        self.deletePlan(name)
        self.cleanTerraformConfigurationFiles(name)

    def destroyVM(self, name):
        self.createTerraformConfigurationFiles(name)
        self.tfInit()
        if not self.isVmExistsInStateFile(name):
            self.importResource(name)
        self.destroyResource(name)
        self.cleanTerraformConfigurationFiles(name)
