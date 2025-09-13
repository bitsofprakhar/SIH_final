# import requests
#
# # Test the API directly
# url = "https://kwztlhywsczfajjtpjmo.supabase.co"
# headers = {
#     "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3enRsaHl3c2N6ZmFqanRwam1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxNzk5NjMsImV4cCI6MjA3Mjc1NTk2M30.vjr315rV_HkZkVVpPmhqc4eNgWKcRLowOf_8-osH1KU",
#     "Authorization": f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3enRsaHl3c2N6ZmFqanRwam1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxNzk5NjMsImV4cCI6MjA3Mjc1NTk2M30.vjr315rV_HkZkVVpPmhqc4eNgWKcRLowOf_8-osH1KU"
# }
#
# response = requests.get(url, headers=headers)
# print(f"Status: {response.status_code}")
# print(f"Response: {response.text}")
########################################
import requests

url = "https://kwztlhywsczfajjtpjmo.supabase.co/rest/v1/Student_Data"
headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3enRsaHl3c2N6ZmFqanRwam1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxNzk5NjMsImV4cCI6MjA3Mjc1NTk2M30.vjr315rV_HkZkVVpPmhqc4eNgWKcRLowOf_8-osH1KU",
    "Authorization": f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3enRsaHl3c2N6ZmFqanRwam1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxNzk5NjMsImV4cCI6MjA3Mjc1NTk2M30.vjr315rV_HkZkVVpPmhqc4eNgWKcRLowOf_8-osH1KU"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")