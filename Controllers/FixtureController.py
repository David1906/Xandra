import subprocess

from DataAccess.MainConfigData import MainConfigData


class FixtureController:
    def launch_fct_host_control(self, fixture, stateTraceability):
        mainConfigData = MainConfigData()
        cmd = f"{mainConfigData.get_fixture_ip_env_name()}={fixture.ip} {mainConfigData.get_fct_host_control_fullpath()}  -f {fixture.id}"
        if stateTraceability == False:
            cmd += " -m"
        print(cmd)
        subprocess.call(cmd, shell=True)
        # subprocess.call(["gnome-terminal", "-x", "sh", "-c", f"{cmd}; bash"])
        # subprocess.call(["gnome-terminal", "-x", cmd])
