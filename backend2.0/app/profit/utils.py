import base64
from typing import Dict
from datetime import datetime

from loguru import logger


def get_token_headers(environment_token: str) -> Dict[str, str]:
    token_bytes = environment_token.encode("ascii")
    token_base64 = base64.b64encode(token_bytes).decode("ascii")
    headers = {"Authorization": "AfasToken " + token_base64}
    return headers


def flatten_metainfo(metainfo: dict, connector_metainfo: dict, hierarchy: str):
    metainfo["connectors"].append(
        {"name": connector_metainfo["name"], "hierarchy": hierarchy, "fields": connector_metainfo["fields"]}
    )
    if "objects" in connector_metainfo:
        if len(connector_metainfo["objects"]) > 1:
            for sub_connector_metainfo in connector_metainfo["objects"]:
                new_hierarchy = hierarchy + f" -> {sub_connector_metainfo['name']}"
                if "objects" in sub_connector_metainfo:
                    for new_connector in sub_connector_metainfo["objects"]:
                        new_new_hierarchy = new_hierarchy + f" -> {new_connector['name']}"
                        flatten_metainfo(metainfo, new_connector, new_new_hierarchy)
                    metainfo["connectors"].append(
                        {"name": sub_connector_metainfo["name"], "hierarchy": new_hierarchy,
                         "fields": sub_connector_metainfo["fields"]}
                    )

                else:
                    metainfo["connectors"].append(
                        {"name": sub_connector_metainfo["name"], "hierarchy": new_hierarchy,
                         "fields": sub_connector_metainfo["fields"]}
                    )
        else:
            for sub_connector_metainfo in connector_metainfo["objects"]:
                hierarchy += f" -> {sub_connector_metainfo['name']}"
                flatten_metainfo(metainfo, sub_connector_metainfo, hierarchy)


def get_keys(url_elements: list, data):
    keys = ""
    final_key = ""
    for key, values in data.items():
        keys += key + "/"
        for all_keys in [*values["Element"]["Fields"]]:
            keys += str(all_keys) + ","
        keys = keys[:-1] + "/"
        for all_values in list(values["Element"]["Fields"].values()):
            keys += str(all_values) + ","
        keys = keys[:-1] + "/"
        url_elements.append(keys)

        for second_key, second_value in values["Element"].items():
            if "Objects" in second_key:
                if second_value:
                    for nested_dict in second_value:
                        return get_keys(url_elements, nested_dict)
        for url in url_elements:
            final_key += url
        return final_key


def set_primary_keys_right_dict(metainfo, data, set_date):
    update_connector = next(iter(data))
    for key, value in data[update_connector]["Element"]["Fields"].items():
        if set_date:
            try:
                data[update_connector]["Element"]["Fields"][key] = datetime.strftime(datetime.fromisoformat(value[:-1]).astimezone(), "%Y-%m-%d")
            except (ValueError, TypeError):
                value = value
        for connector in metainfo["connectors"]:
            if connector["name"] == update_connector:
                for field in connector["fields"]:
                    if field["fieldId"] == key:
                        if field["primaryKey"]:
                            new_field_id = "@" + key
                            data[update_connector]["Element"][new_field_id] = value
    need_objects = data[update_connector]["Element"]["Objects"]
    if type(need_objects) == dict:
        set_primary_keys_right_dict(metainfo, need_objects, set_date)
    elif type(need_objects) == list and need_objects != []:
        set_primary_key_right_list(metainfo, need_objects, set_date)
    else:
        return data
    return data


def set_primary_key_right_list(metainfo, data, set_date):
    for dictionary in data:
        first_key = next(iter(dictionary))
        for item in dictionary[first_key]["Element"]:
            for key, value in item["Fields"].items():
                if set_date:
                    try:
                        item["Fields"][key] = datetime.strftime(datetime.fromisoformat(value[:-1]).astimezone(), "%Y-%m-%d")
                    except (ValueError, TypeError):
                        value = value
                for connector in metainfo["connectors"]:
                    if connector["name"] == first_key:
                        for field in connector["fields"]:
                            if field["fieldId"] == key:
                                if field["primaryKey"]:
                                    new_field_id = "@" + key
                                    item[new_field_id] = value
            try:
                need_objects = item["Element"]["Objects"]
                if type(need_objects) == dict:
                    set_primary_keys_right_dict(metainfo, need_objects, set_date)
                elif type(need_objects) == list and need_objects != []:
                    set_primary_key_right_list(metainfo, need_objects, set_date)
                else:
                    pass
            except KeyError:
                pass
    return data
