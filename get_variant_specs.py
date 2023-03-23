#!/usr/bin/env python3

import os
import json

CONFIG_DIR = 'variant-configs'
OUT_JSON = 'argouml-variant-features.json'
OUT_ABBR_JSON = 'argouml-variant-features_abbr.json'
# INFILE = 'infile.argouml-variants.diffast'
# INFILE_ = 'infile.argouml-variants.diffast.abbr'

ABBR_TBL = {
    'ACTIVITYDIAGRAM': 'A',  # 2282
    'COGNITIVE': 'C',  # 16319
    'COLLABORATIONDIAGRAM': 'C',  # 1579
    'DEPLOYMENTDIAGRAM': 'D',  # 3147
    'LOGGING': 'L',  # 2159
    'SEQUENCEDIAGRAM': 'S',  # 5379
    'STATEDIAGRAM': 'S',  # 3917
    'USECASEDIAGRAM': 'U',  # 2712
}
FEATURE_LIST = sorted(list(ABBR_TBL.keys()))


def abbrev(fl):
    a = ''
    for f in FEATURE_LIST:
        f_ = '-'
        if f in fl:
            f_ = ABBR_TBL[f]
        a += f_
    a += '  '
    return a


def dump_cache():
    tbl = {}
    tbl_abbr = {}
    for config in os.listdir(CONFIG_DIR):
        with open(os.path.join(CONFIG_DIR, config)) as f:
            config_id = config.replace('.config', '')
            fl = []
            for _line in f.readlines():
                line = _line.strip()
                fl.append(line)
            fl.sort()
            tbl[config_id] = fl
            tbl_abbr[config_id] = abbrev(fl)

    with open(OUT_JSON, 'w') as f:
        json.dump(tbl, f)

    with open(OUT_ABBR_JSON, 'w') as f:
        json.dump(tbl_abbr, f)

    return tbl_abbr


def get_abbr_tbl():
    if os.path.exists(OUT_ABBR_JSON):
        with open(OUT_ABBR_JSON) as f:
            abbr_tbl = json.load(f)
    else:
        abbr_tbl = dump_cache()
    return abbr_tbl


if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='convert distance matrix of argouml-variants',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('infile', type=str)

    args = parser.parse_args()

    abbr_tbl = get_abbr_tbl()

    infile = args.infile
    infile_ = infile + '.abbr'

    with open(infile) as infile:
        with open(infile_, 'w') as infile_:
            for _line in infile.readlines():
                line = _line.strip()
                old = line[:5]
                try:
                    new = abbr_tbl[old]
                    # print(f'"{old}" -> "{new}"')
                    line = new + line[10:]
                except KeyError:
                    pass
                infile_.write(line+'\n')
