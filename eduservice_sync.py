import requests
import json

r = requests.post("https://eduservices.2035.university/rest/v2/oauth/token?grant_type=password&username=restapiuser&password=rV3EDzt3qptt",
                  headers={"content-type": "application/x-www-form-urlencoded",
                           "Authorization": "Basic ZnE0aXk0cG1mcnA2c20xbTl6d3I6eHBwYXQ2MmZtczhqdGV1eHNleXZtZ3pveXQ4aG40bTk4aWFyem43aQ=="})

data = json.loads(r.content.decode())

token = data['access_token']

r = requests.get("https://eduservices.2035.university/rest/v2/queries/srvcat_AgreementConfirm/agreementConfirmByDate?startDate=2019-07-01&endDate=2019-07-30",
                 headers={"Authorization": "Bearer {}".format(token)})

payload = json.loads(r.content.decode())


for agreement_data in payload:

    print(agreement_data['typeAgreement']['_instanceName'])
    print(agreement_data['service']['title'])
    print(agreement_data['user']['organizationName'])
    print(agreement_data['number'])
    print(agreement_data['createTs'])
    print(agreement_data['updateTs'])
