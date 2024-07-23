import json
import random
a = open("process.json")
data = json.load(a)


def remove_id(d):
    for key in list(d.keys()):
        if key == 'id':
            del d[key]
        elif isinstance(d[key], dict):
            remove_id(d[key])
        elif isinstance(d[key], list):
            for i in d[key]:
                remove_id(i)

# Example usage
# remove_id(data)
# json_object = json.dumps(data, indent=4)
#
# # Writing to sample.json
# with open("new_process.json", "w") as outfile:
#     outfile.write(json_object)


def generate_dutch_bank_account_number():
    bank_code = "".join(str(random.randint(0, 9)) for i in range(4))
    account_number = "".join(str(random.randint(0, 9)) for i in range(10))
    return bank_code + account_number

iets = generate_dutch_bank_account_number()
print(iets)