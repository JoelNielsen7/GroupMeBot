import requests
import json
import os


token = ''

id_list = {
    'Easton': '22793326'
}

def get_groups():
    link = ' https://api.groupme.com/v3/groups?token=' + token
    r = requests.get(link)
    res = r.json()
    # print(res, type(res))
    # for group in res['response']:
    #     print(group['name'])
    return res
    # print(r.json())

def filter_groups(groups, filters):
    filtered = []
    for group in groups['response']:
        for filter in filters:
            if group['name'] == filter:
                filtered.append(group)

    return filtered

def get_id_from_nickname(filtered, name):
    for group in filtered:
        id = group['id']
        link = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit=100'.format(id, token)
        r = requests.get(link)
        # print(r)
        res = r.json()['response']
        # print(res, group['name'], type(res['response']))
        count = res['count']
        messages = res['messages']
        print(len(messages), count)

        num_calls = count // 10
        leftover = count % 10

        all_messages = messages

        print(messages[0])
        first_id = messages[0]['id']

        for i in range(num_calls-1):
            # print("first:", first_id)
            link = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit=100&before_id={}'.format(id, token, first_id)
            messages = requests.get(link).json()['response']['messages']
            # print(messages)
            all_messages.extend(messages)
            first_id = messages[0]['id']
            for message in messages:
                if message['name'] == name:
                    print("Name:", message['name'], "id" ,message['user_id'])
                    x = 5/0


def get_messages(filtered):
    for group in filtered:
        id = group['id']
        link = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit=100'.format(id, token)
        r = requests.get(link)
        # print(r)
        res = r.json()['response']
        # print(res, group['name'], type(res['response']))
        count = res['count']
        # count = 1000
        messages = res['messages']
        print(len(messages), count)

        num_calls = count // 100
        leftover = count % 100

        all_messages = messages

        print(messages[0])
        first_id = messages[len(messages)-1]['id']

        for i in range(num_calls-1):
            # print("first:", first_id)
            link = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit=100&before_id={}'.format(id, token, first_id)
            messages = requests.get(link).json()['response']['messages']
            # print(messages)
            all_messages.extend(messages)
            first_id = messages[(len(messages)-1)]['id']

        if leftover > 0:
            link = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit={}&before_id={}'.format(id, token, leftover, first_id)

            messages = requests.get(link).json()['response']['messages']
            all_messages.extend(messages)

        print(len(all_messages), count)


        return all_messages

def get_users_messages(messages, ids):
    sorted = {}
    for id in ids:
        sorted['id'] = []
        for message in messages:
            print(message['user_id'], id)
            if message['user_id'] == id:
                print("MATCH")
                sorted['id'].append(message)
    return sorted

def generate_text_file(sorted, names):
    for id, messages in sorted.items():
        str = ''
        for message in messages:
            if message['text'] == None:
                continue #print(message)
            str += message['text']
            str += '<|endoftext|>'
        fp = open('Easton.txt', 'w')
        fp.write(str)
        fp.close()

def train_model():
    os.system('python3 encode.py Easton2.txt Easton2.npz')
    os.system('python3 train.py --dataset Easton2.npz --restore_from latest')

def generate_unconditional(name):
    temp = 0.8
    top_k = 40
    os.system('python3 interactive_conditional_samples.py --temperature {} --top_k {} --model_name {}'.format(temp, top_k, name))

if __name__ == '__main__':
    mode = 'Resume'
    if mode == 'Train':
        groups = get_groups()
        filters = ['Beta Theta Pi', 'Beta Theta Pi- Actives Only']
        filtered = filter_groups(groups, filters)
        # id = get_id_from_nickname(filtered, 'A Tyrant in an Eddie Bauer Sweater')
        messages = get_messages(filtered)
        names = ['Easton']
        ids = [id_list['Easton']]
        sorted = get_users_messages(messages, ids)
        print(sorted, sorted.keys())
        generate_text_file(sorted, names)
        train_model()
    elif mode == 'Generate':
        generate_unconditional('117M')
    elif mode == 'Resume':
        train_model()
