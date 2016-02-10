import subprocess, json

ipmi_sdr=subprocess.check_output(['ipmitool','sdr']).strip().split("\n")
ipmi_values_dict = {}
ipmi_status_dict = {}

for sdr_row in ipmi_sdr:
  vals = sdr_row.split("|")
  vals = map(lambda s: s.strip(), vals)
  ipmi_values_dict[vals[0]]=vals[1]
  ipmi_status_dict[vals[0]]=vals[2]  
    
print json.dumps(ipmi_values_dict, sort_keys=True, indent=4)
print json.dumps(ipmi_status_dict, sort_keys=True, indent=4)
