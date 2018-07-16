# When you need to update sub-tasks with the results from dealers

import requests

def read_config():
    separator = '='
    properties = {}
    creds = dict(username="zarar.siddiqi", password="")
    response = requests.post('https://ctc-customs.atlassian.net/rest/auth/1/session', json=creds)
    if response.ok:
        properties['cookie'] = '%s=%s' % (response.json()['session']['name'], response.json()['session']['value'])
    else:
        print('status: %s' % response.status_code)
        print(response.content)
        exit(1)
    return properties


def get_uat_bugs(config: dict) -> list:
    issues = []
    batch_size = 50
    jql = 'project = "5452- ORKESTRA" AND type = Bug AND status not in (Resolved, Closed) AND labels in (OnshoreQA, DAT, UAT, "INT", integration) ORDER BY Rank ASC'
    jql = 'project = "5452- ORKESTRA" AND type = Bug AND status not in (Closed) AND labels in (OnshoreQA, DAT, UAT, "INT", integration) ORDER BY Rank ASC'
    fields = ['summary', 'description', 'status', 'labels', 'parent', 'components', 'customfield_16813']
    params = {
        'jql': jql,
        'startAt': 0,
        'maxResults': batch_size,
        'fields': fields,
        'fieldsByKeys': False
    }
    response = requests.get('https://ctc-customs.atlassian.net/rest/api/2/search', params=params,
                            headers={'Cookie': config['cookie']})
    if response.ok:
        issues += response.json()['issues']
        start_at = batch_size
        total = response.json()['total']
        while start_at < total:
            percents = float(start_at) / float(total) * 100.0
            print('%.2f%%' % percents)
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': batch_size,
                'fields': fields,
                'fieldsByKeys': False
            }
            response = requests.get('https://ctc-customs.atlassian.net/rest/api/2/search', params=params,
                                    headers={'Cookie': config['cookie']})
            if response.ok:
                issues += response.json()['issues']
                start_at += batch_size
            else:
                print(response.reason)
                print(response.content)
                exit(1)
        print('Done.')
        return issues
    else:
        print(response.reason)
        print(response.content)
        exit(1)


def are_the_same(current_sub_task: dict, description: str, status: str) -> bool:
    return 'fields' in current_sub_task and description == current_sub_task['fields'][
        'description'] and status == current_sub_task['fields']['status']['name']





def main():
    config = read_config()
    uat_bugs = get_uat_bugs(config)
    uat_bugs_count = len(uat_bugs)
    uat_bugs_processed = 0
    teams = ["Roma", "Lyon", "Metalist", "Sevilla", "Rangers", "Sparta", "Arsenal", "Juventus", "Valencia", "Besiktas", "Inter", "Bayern", "Ajax", "Udinese", "Dortmund", "Dynamo"]
    for uat_bug in uat_bugs:
        print(uat_bug["key"])
        components = uat_bug['fields']['components']
        for c in components:
            if c["name"] not in teams and (uat_bug["fields"]["customfield_16813"] is None or uat_bug["fields"]["customfield_16813"] == ""):
                print("Issue requires update")
                params = {
                    'fields': {
                        'customfield_16813': c["name"]
                    }
                }
                url = 'https://ctc-customs.atlassian.net/rest/api/2/issue/' + uat_bug["key"]
                response = requests.put(url, json=params, headers={'Cookie': config['cookie']})
                if response.ok:
                    pass
                else:
                    print(response.reason)
                    print(response.content)
    


if __name__ == '__main__':
    main()

