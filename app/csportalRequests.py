import requests
from dictManager import statusDict, workspaceDict

class firecloud_requests(object):
    # https://api.firecloud.org/
    @staticmethod
    def generate_headers(access_token):
        return {"Authorization" : "bearer " + str(access_token)}

    @staticmethod
    def get_health():
        return requests.get("https://api.firecloud.org/health").ok

    @staticmethod
    def check_fc_registration(headers):
        return requests.get("https://api.firecloud.org/me", headers=headers).ok

    @staticmethod
    def check_billing_projects(headers):
        return requests.get("https://api.firecloud.org/api/profile/billing", headers=headers).ok

    @staticmethod
    def get_billing_projects(headers):
        return requests.get("https://api.firecloud.org/api/profile/billing", headers=headers).json()

    @staticmethod
    def create_new_workspace(headers, json):
        return requests.post("https://api.firecloud.org/api/workspaces", headers=headers, json=json)

class process_requests(firecloud_requests):
    @staticmethod
    def list_billing_projects(billing_projects_json):
        list_ = []
        for project_ in billing_projects_json:
            list_.extend([str(project_['projectName'])])
        return list_

class launch_requests(object):
    @staticmethod
    def launch_check_fc_registration(access_token):
        headers = firecloud_requests.generate_headers(access_token)
        if firecloud_requests.check_fc_registration(headers):
            return statusDict.return_success()
        else:
            return statusDict.return_danger()

    @staticmethod
    def launch_check_billing_projects(access_token):
        headers = firecloud_requests.generate_headers(access_token)
        if firecloud_requests.check_billing_projects(headers):
            json = firecloud_requests.get_billing_projects(headers)
            if len(json) > 0:
                return statusDict.return_success()
            else:
                return statusDict.return_danger()
        else:
            return statusDict.return_danger()

    @staticmethod
    def launch_list_billing_projects(access_token):
        headers = firecloud_requests.generate_headers(access_token)
        json = firecloud_requests.get_billing_projects(headers)
        return process_requests.list_billing_projects(json)

    @staticmethod
    def launch_create_new_workspace(access_token, patient):
        headers = firecloud_requests.generate_headers(access_token)
        json = workspaceDict.populate_workspace_json(patient)
        workspace = firecloud_requests.create_new_workspace(headers, json)
        print "workspace created?:", workspace.ok

class firecloud_functions(object):
    @staticmethod
    def evaluate_upload_status(status_dict):
        if 'danger' not in status_dict.values():
            return True
        else:
            return False

    @staticmethod
    def populate_status(dict, access_token):
        dict['google_status'] = statusDict.return_success()
        dict['firecloud_status'] = launch_requests.launch_check_fc_registration(access_token)
        dict['billing_status'] = launch_requests.launch_check_billing_projects(access_token)
        return dict

    @staticmethod
    def populate_user(dict, access_token):
        billing_list = launch_requests.launch_list_billing_projects(access_token)
        dict['firecloud_billing'] = []
        for i in range(0, len(billing_list)):
            dict['firecloud_billing'].append(tuple([billing_list[i], billing_list[i]]))
        return dict

# Can be deleted
#    @staticmethod
#    def create_workspace_json(patient):
#        return workspaceDict.populate_workspace_json(patient)