#!/usr/bin/env python

# Copyright (c) 2018 Intel Labs.
# authors: German Ros (german.ros@intel.com)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Example of automatic vehicle control from client side."""

from __future__ import print_function
import logging
import hydra
from omegaconf import DictConfig, OmegaConf
from pathlib import Path

from sim.Simulation import Simulation
from sim.utils import *

@hydra.main(config_path="conf", config_name="config", version_base="1.3")
def main(cfg: DictConfig):
    print(__doc__)

    # Optional: Print config tree
    logging.debug(OmegaConf.to_yaml(cfg))

    # Set resolution
    width, height = [int(x) for x in cfg.res.split("x")]
    cfg.width = width
    cfg.height = height

    # Logging setup
    log_level = logging.DEBUG if cfg.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)
    logging.info('Listening to server %s:%s', cfg.host, cfg.port)

    # Simulation

    sim = Simulation()
    sim.init(cfg)  # assumes Simulation accepts a DictConfig or object with .field access

    try:
        while True:
            finish = sim.step()
            if finish:
                sim.destroy()
                break

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
        sim.destroy()


if __name__ == '__main__':
    main()
