import os 
import subprocess
import shutil
import ctypes
import time

#convert window 64-bit path to 32-bit path 
class disable_file_system_redirection:
  _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
  _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
  def __enter__(self):
    self.old_value = ctypes.c_long()
    self.success = self._disable(ctypes.byref(self.old_value))
  def __exit__(self, type, value, traceback):
    if self.success:
      self._revert(self.old_value)
disable_file_system_redirection().__enter__()

#create a key called “DisableServerHeader” and set its value to 2. Reset HTTP & IIS
os.system("powershell.exe REG ADD HKLM\SYSTEM\CurrentControlSet\Services\HTTP\Parameters /v DisableServerHeader /t REG_DWORD /d 2")
os.system("powershell.exe net stop http /f")
os.system("powershell.exe net start http")
os.system('cmd /c “iisreset”')
time.sleep(3)

#display rules in powershell
os.system("powershell.exe Write-Host")
os.system("powershell.exe Write-Host IIS fixer currntly running... -ForegroundColor Yellow")
os.system("powershell.exe Write-Host Making changes to the following settings... -ForegroundColor Yellow")
time.sleep(1)
os.system("powershell.exe Write-Host")
os.system("powershell.exe Write-Host [X-Frame option] -ForegroundColor Green")
os.system("powershell.exe Write-Host")
time.sleep(3)
os.system("powershell.exe Write-Host [X-Powered-by] -ForegroundColor Green")
os.system("powershell.exe Write-Host")
time.sleep(4)
os.system("powershell.exe Write-Host [requestFiltering] -ForegroundColor Green")
os.system("powershell.exe Write-Host")
time.sleep(3)
os.system("powershell.exe Write-Host [enableVersionHeader] -ForegroundColor Green")
os.system("powershell.exe Write-Host")
time.sleep(3)
os.system("powershell.exe Write-Host [httpMethod] -ForegroundColor Green")
os.system("powershell.exe Write-Host")
time.sleep(1)
os.system("powershell.exe Write-Host Settings have been installed -ForegroundColor Yellow")

#provide file path for host file and copy version of the host file  
file_path = 'C:\Windows\System32\inetsrv\Config\applicationHost.config'
copy_path = 'C:\Windows\System32\inetsrv\Config\applicationHost_COPY.config'

#if copy exists, replace the host file with copy file.
#if copy doesn’t exist, replace the copy file with the host file
copy_exist = os.path.isfile(copy_path)
if copy_exist:
  shutil.copyfile(copy_path, file_path)
else:
  shutil.copyfile(file_path, copy_path)

#reset IIS server
os.system('cmd /c "iisreset"')

#Read the contents of the host file and return them in a list
config_fileread = open(file_path, 'r')
lines = config_fileread.readlines()

#add the following contents
remove_framework = '\t<httpProtocol>\n' + '\t<customHeader>\n' + '\t<add name="X-Frame-Options" value="SAMEORIGIN" />\n' + '\t<remove name="X-Powered-By" />\n' + '\t</customHeader>\n' + '\t</httpProtocol>\n' 
remove_IIS_version = '\t<security>\n' + '\t<requestFiltering removeServerHeader=“true” />\n' + '\t</security>\n'
remove_framework_version = '\t<system.web>\n' + '\t<httpRuntime enableVersionHeader=“false”/>\n' + '\t</system.web>\n'
disable_trace = '\t<requestFiltering>\n' + '\t<verbs allowUnlisted="false">\n' + '\t<clear/>\n' + '\t<add verb="GET" allowed="true" />\n' + '\t<add verb="HEAD" allowed="true" />\n' + '\t<add verb="POST" allowed="true" />\n' + '\t</verbs>\n' + '\t</requestFiltering>\n'
full_content = remove_framework + remove_IIS_version + remove_framework_version + disable_trace

#identify index of the first keyword “configuration” in texts and add “contents_to_add” at next index postiion
for line in lines:
  if "<configuration>" in line:
   index_num = lines.index(line)
   break
lines.insert(index_num + 1, full_content)

#convert the list to string format
revised_config_content = ''
for i in lines:
  revised_config_content += i

#Rewrite the content of the host file with “revised_config_file”
with open(file_path, 'r+') as f:
  f.truncate(0)
  f.write(revised_config_content)