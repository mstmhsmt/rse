#!/usr/bin/env python3

'''
  mkdistmat.py

  Copyright 2023 Chiba Institute of Technology

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
'''

__author__ = 'Masatomo Hashimoto <m.hashimoto@stair.center>'

import os
import sys
import random
import logging
import multiprocessing as mp

from cca.ccautil.srcdiff import diff_dirs, diffast
from cca.ccautil.cca_config import config_from_json
from cca.ccautil import srcdiff, diffts

logger = mp.get_logger()

LOGGING_FORMAT = '[%(asctime)s][%(processName)s][%(levelname)s][%(funcName)s] %(message)s'

DEFAULT_LOGGING_LEVEL = 25

DEFAULT_NPROCS = 2


def setup_logger(logger, log_level=DEFAULT_LOGGING_LEVEL, log_file=None):
    if log_file:
        fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        fh.setLevel(log_level)
        fmt = logging.Formatter(LOGGING_FORMAT)
        fh.setFormatter(fmt)
        logging.basicConfig(level=log_level, handlers=[fh])
        logger.addHandler(fh)
    else:
        logging.basicConfig(format=LOGGING_FORMAT, level=log_level)


def get_conf(name):
    m = None
    try:
        m = __import__(name)
        return m.conf
    except Exception as e:
        logger.warning(f'cannot find conf for "{name}": {e}')


def get_label(n):
    return (n + ' ' * 10)[:10]


def _do_task(args_kw, pid):
    args, kw = args_kw
    tid, conf, task, mode = args
    old, new, odir, ndir = task

    include = conf.include
    exclude = conf.exclude

    pid = mp.current_process().name

    if conf.single_file_mode:
        r = diffast(odir, ndir, **kw)

    else:
        if len(conf.include) == 1:
            target = conf.include[0]
            odir = os.path.join(odir, target)
            ndir = os.path.join(ndir, target)
            include = []

        if include or exclude:
            kw['fact_proj_roots'] = [odir, ndir]

        r = diff_dirs(diffast, odir, ndir,
                      quiet=True,
                      include=include, exclude=exclude,
                      # local_cache_name=str(pid),
                      keep_going=True,
                      **kw)

    cost = r['cost']

    nmappings = r['nmappings']

    removed = len(r['removed'])
    added = len(r['added'])
    moved = len(r['moved'])

    nrelabels = r['nrelabels']
    nmoves = r['nmoves']
    nmovrels = r['nmovrels']

    nnodes = r['nnodes']

    logger.info(f'cost={cost} nmappings={nmappings}')

    logger.info(f'removed={removed} added={added} moved={moved}'
                f' nrelabels={nrelabels} nmoves={nmoves} nmovrels={nmovrels}')

    use_similarity = False
    count_moved_nodes = True

    if use_similarity:
        logger.info('using dissimilarity')
        cost = nnodes
        # nm = (nmappings - nrelabels - nmoves + nmovrels) * 2
        # nm = (nmappings - nmoves) * 2
        nm = nmappings * 2
        logger.info(f'nnodes={nnodes} nm={nm}')

    else:
        if count_moved_nodes:
            cost = removed + added + nrelabels + moved

        tbl = {
            0: lambda x: 1,
            1: lambda x: x,
            2: lambda x: x - nrelabels,
            3: lambda x: x - nrelabels - nmoves + nmovrels,
            4: lambda x: x + (nmappings - nrelabels - nmoves + nmovrels),
            5: lambda x: x - nrelabels - nmoves + nmovrels + (nmoves - nmovrels) / 2,
            6: lambda x: x - nmoves + nmoves / 2,
        }

        nm = tbl[mode](nmappings)

        logger.info(f'nm={nm}')

    if nm > 0:
        dist = float(cost) / float(nm)
    else:
        if cost == 0:
            dist = 0.0
        else:
            # dist = float('inf')
            dist = float(cost)

    # sim = float((nmappings - nrelabels - nmoves + nmovrels) * 2) / float(nnodes)
    # dist = 1.0 - sim

    return (pid, tid, old, new, str(dist))


def do_task(args_kw):
    pid = mp.current_process().name
    return _do_task(args_kw, pid)


def gen_tasks(conf):
    pairs = []
    n = conf.nversions
    vers = conf.vers
    for i in range(n - 1):
        for j in range(i + 1, n):
            pairs.append((vers[i], vers[j]))
            pairs.append((vers[j], vers[i]))

    tasks = []

    get_long_name = conf.get_long_name

    for (old, new) in pairs:
        odir = conf.get_ver_dir(get_long_name(old))
        ndir = conf.get_ver_dir(get_long_name(new))

        tasks.append((old, new, odir, ndir))

    random.shuffle(tasks)

    return tasks


def setup_kwargs(conf, basedir, usecache=False):
    cache_dir_base = os.path.abspath(os.path.join(basedir, 'CACHE'))
    kwargs = {
        'usecache': usecache,
        'cache_dir_base': cache_dir_base,
    }
    return kwargs


def dumpdistmat(conf, result, ofile, factor):
    logger.info(f'dumping distmat to "{ofile}"...')
    dist_tbl = {}
    for (tid, r) in result.items():
        vstr = r[2]
        try:
            v = float(vstr)
            v *= factor
            dist_tbl[(r[0], r[1])] = v

        except ValueError:
            logger.error(f'illegal value: "{vstr}" (tid={tid})')

    with open(ofile, 'w') as out:

        out.write(str(conf.nversions))
        out.write('\n')

        vers = conf.vers

        for s0 in vers:
            label = get_label(conf.abbrev_tbl.get(s0, s0))
            out.write(label)
            for s1 in vers:
                dist = 0.0
                try:
                    try:
                        dist = dist_tbl[(s0, s1)]
                    except KeyError:
                        dist = dist_tbl[(s1, s0)]
                except KeyError:
                    pass

                try:
                    if dist_tbl[(s0, s1)] != dist_tbl[(s1, s0)]:
                        dist = (dist_tbl[(s0, s1)] + dist_tbl[(s1, s0)]) / 2.0
                except KeyError:
                    pass

                dist_str = vstr = f'{dist:0.10f}'

                out.write(dist_str + ' ')
            out.write('\n')

    logger.info('done.')


def init_proc(log_level, log_dir):
    pid = mp.current_process().name
    log_dir = os.path.join(log_dir)
    log_file = os.path.join(log_dir, f'mkdistmat.{pid}.log')
    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(log_level)
    fmt = logging.Formatter(LOGGING_FORMAT)
    fh.setFormatter(fmt)
    logger = mp.get_logger()
    logger.addHandler(fh)
    logger.propagate = False
    diffts.logger = logger
    srcdiff.logger = logger


def mkdistmat():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='make distance matrix (multi-process)',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('proj_id', type=str)

    parser.add_argument('-b', '--basedir', dest='basedir',
                        default='.', metavar='DIR',
                        help='set base dir to DIR')

    parser.add_argument('-p', '--nprocs', dest='nprocs',
                        default=DEFAULT_NPROCS, type=int,
                        help='number of processes', metavar='N')

    parser.add_argument('--dist-mode', dest='dist_mode',
                        default=1, type=int, choices=[0, 1],
                        help='distance mode', metavar='N')

    parser.add_argument('--factor', dest='factor', default=1.0, type=float,
                        help='multiply distances by R', metavar='R')

    args = parser.parse_args()

    log_level = logging.INFO

    setup_logger(logger, log_level)

    conf = config_from_json(os.path.join('configs', args.proj_id+'.json'))

    if conf is None:
        print(f'config not found for "{args.proj_id}"')
        exit(1)

    if not os.path.exists(args.basedir):
        os.makedirs(args.basedir)
        print(f'"{args.basedir}" created')

    kw = setup_kwargs(conf, args.basedir)

    tasks = gen_tasks(conf)

    ntasks = len(tasks)

    print(f'{ntasks} tasks generated')

    init = init_proc
    initargs = (log_level, args.basedir)

    done = 0

    tl = []

    for tid, task in enumerate(tasks):
        tl.append(((tid, conf, task, args.dist_mode), kw))

    result_tbl = {}

    with mp.Pool(processes=args.nprocs, initializer=init, initargs=initargs) as pool:
        for (pid, tid, old, new, dist) in pool.imap_unordered(do_task, tl, chunksize=1):
            result_tbl[tid] = (old, new, dist)
            done += 1
            r = float(done) * 100.0 / ntasks
            sys.stdout.write(f' processed {done:4}/{ntasks:4} ({r:2.2f}%)\r')
            sys.stdout.flush()
            logger.info(f'[{pid}] processed task-{tid} ({done}/{ntasks}={r:.2f}%)')

    print(f'processed {done} tasks in total          ')
    logger.info(f'processed {done} tasks in total')

    dumpdistmat(conf,
                result_tbl,
                os.path.join(args.basedir, f'infile.{args.proj_id}.diffast.d{args.dist_mode}'),
                factor=args.factor)


if __name__ == '__main__':
    mkdistmat()
