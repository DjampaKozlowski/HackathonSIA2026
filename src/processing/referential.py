import json 

def read_referential_json(fpath:str) -> dict:
    with open(fpath, 'r') as f:
        res = json.load(f)
    return res

def parse_raw_referential(raw_dict: dict) -> dict:
    for page in raw_dict:
        entries = page.get('result', None)


if __name__ == '__main__':
    fpath = '../../data/reference/raw_vitis_crop_ontology.json'
    res = read_referential_json(fpath=fpath)
    parse_raw_referential(res)