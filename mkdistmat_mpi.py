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
import logging
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor

from cca.ccautil.cca_config import config_from_json
from cca.ccautil import srcdiff, diffts
from mkdistmat import LOGGING_FORMAT
from mkdistmat import _do_task, setup_logger, gen_tasks, setup_kwargs, dumpdistmat

logger = logging.getLogger()


def do_task(args_kw):
    rank = MPI.COMM_WORLD.Get_rank()
    return _do_task(args_kw, rank)


def init_proc(log_level, log_dir):
    rank = MPI.COMM_WORLD.Get_rank()
    log_dir = os.path.join(log_dir)
    log_file = os.path.join(log_dir, f'mkdistmat.{rank}.log')
    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(log_level)
    fmt = logging.Formatter(LOGGING_FORMAT)
    fh.setFormatter(fmt)
    logger = logging.getLogger()
    logger.addHandler(fh)
    logger.propagate = False
    diffts.logger = logger
    srcdiff.logger = logger


def mkdistmat():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='make distance matrix (MPI)',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('proj_id', type=str)

    parser.add_argument('-b', '--basedir', dest='basedir',
                        default='.', metavar='DIR',
                        help='set base dir to DIR')

    parser.add_argument('--use-cache', dest='use_cache',
                        action='store_true', help='use cache')

    parser.add_argument('--dist-mode', dest='dist_mode',
                        default=3, type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                        help='distance mode', metavar='N')

    parser.add_argument('--factor', dest='factor', default=1.0, type=float,
                        help='multiply distances by R', metavar='R')

    args = parser.parse_args()

    log_level = logging.INFO

    log_dir = os.path.join(args.basedir, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    setup_logger(logger, log_level,
                 os.path.join(log_dir,
                              f'mkdistmat.{MPI.COMM_WORLD.Get_rank()}.log'))

    conf = config_from_json(os.path.join('configs', args.proj_id+'.json'))

    if conf is None:
        logger.error(f'conf not found for "{args.proj_id}"')
        exit(1)

    kw = setup_kwargs(conf, args.basedir, usecache=args.use_cache)

    tasks = gen_tasks(conf)

    ntasks = len(tasks)

    logger.info(f'{ntasks} tasks generated')

    done = 0

    tl = []

    for tid, task in enumerate(tasks):
        tl.append(((tid, conf, task, args.dist_mode), kw))

    result_tbl = {}

    init = init_proc
    initargs = (log_level, log_dir)

    with MPIPoolExecutor(initializer=init, initargs=initargs) as pool:
        for (rank, tid, old, new, dist) in pool.map(do_task, tl):
            result_tbl[tid] = (old, new, dist)
            done += 1
            r = float(done) * 100.0 / ntasks
            logger.info(f'[{rank}] processed task-{tid}:'
                        f' {old}-{new}: {dist} ({done}/{ntasks}={r:.2f}%)')

    logger.info(f'processed {done} tasks in total')

    dumpdistmat(conf,
                result_tbl,
                os.path.join(args.basedir,
                             f'infile.{args.proj_id}.diffast.d{args.dist_mode}'),
                factor=args.factor)


if __name__ == '__main__':
    mkdistmat()
