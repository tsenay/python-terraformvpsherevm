from terraformvspherevm.terraformvm import TerraformVM
from terraformvspherevm.terrascriptvspherevm import TerrascriptVSphereVM


def testTerrascriptVSphereVM():
    vm = TerrascriptVSphereVM('test',' guestid', 2, 1024, 'myFolder')
    vm.setDatacenter('DC')
    vm.setDatastore('DS')
    vm.setProvider('host','user','password')
    vm.setResourcePool('pool')
    vm.setTimezone('Etc/Utc')
    vm.addDisk("10")
    vm.addNetworkInterface('dvp', '10.1.1.1', '24')
    assert True

    # "args": ["--name", "terrascript-test", "--datacenter", "DC", "--datastore", "MyDatastore", 
    #     "--pool", "ressource_pool", "--template", "rhel-7.5-vmw6.0", "--guestid", "rhel7_64Guest", "--nic", "DvP_Name",
    #     "--ip", "10.0.123.123", "--cidr", "24", "--gateway", "10.0.123.1", "--cpu", "1", "--ram", "1024", "--disk", "32",
    #     "--disk","20", "--dns", "10.0.123.50", "--dnssearch","domain.com",
    #     "--dns", "10.0.123.100", "--esxhost", "esxhost.domain.com", "--esxuser", "esxusername", "--folder", "terraformed",
    #     "--domain", "my.domaon", "--timezone", "Etc/UTC", "--esxpassvar", "ESXPASS", "--action", "create"],
    #     "env": {"ESXPASS": "toto"}

