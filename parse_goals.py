import xmltodict


GOAL_KEY = {}


def parse_keys():
    # parse the xml file to dict
    xml = None
    with open("goals_key.xml", "r", encoding="utf8") as f:
        content = f.read()
        xml = xmltodict.parse(content)

    key_dict = xml["enum-type"]["enum-item"]
    for i, k in enumerate(key_dict):
        # convert list to '-1' based
        i = i - 1

        # add to GOAL_KEY dict
        GOAL_KEY[i] = k["@name"]

    return GOAL_KEY
