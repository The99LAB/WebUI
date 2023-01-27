import cpuinfo
import platform
print("CPU model name: " + cpuinfo.get_cpu_info()['brand_raw'])
print("Platform: " + platform.platform())
print("Hostname: " + platform.node())
