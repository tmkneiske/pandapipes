# Copyright (c) 2020-2021 by Fraunhofer Institute for Energy Economics
# and Energy System Technology (IEE), Kassel, and University of Kassel. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import numpy as np
from numpy import dtype
from pandapipes.component_models.pump_component import Pump
from pandapipes.idx_branch import VINIT, D, AREA, LOSS_COEFFICIENT as LC, FROM_NODE, PL, PRESSURE_RATIO
from pandapipes.idx_node import PINIT, PAMB


class Compressor(Pump):
    """

    """

    @classmethod
    def table_name(cls):
        return "compressor"

    @classmethod
    def create_pit_branch_entries(cls, net, compressor_pit, node_name):
        """
        Function which creates pit branch entries with a specific table.

        :param net: The pandapipes network
        :type net: pandapipesNet
        :param compressor_pit: a part of the pit that includes only those columns relevant for
                               compressors
        :type compressor_pit:
        :param node_name:
        :type node_name:
        :return: No Output.
        """
        compressor_pit = super(Pump, cls).create_pit_branch_entries(net, compressor_pit, node_name)

        compressor_pit[:, D] = 0.1
        compressor_pit[:, AREA] = compressor_pit[:, D] ** 2 * np.pi / 4
        compressor_pit[:, LC] = 0
        compressor_pit[:, PRESSURE_RATIO] = net[cls.table_name()].pressure_ratio.values

    @classmethod
    def adaption_before_derivatives(cls, net, branch_pit, node_pit, idx_lookups, options):
        # calculation of pressure lift
        f, t = idx_lookups[cls.table_name()]
        compressor_pit = branch_pit[f:t, :]

        from_nodes = compressor_pit[:, FROM_NODE].astype(np.int32)
        p_from = node_pit[from_nodes, PAMB] + node_pit[from_nodes, PINIT]
        p_to_calc = p_from * compressor_pit[:, PRESSURE_RATIO]
        pl_abs = p_to_calc - p_from

        v_mps = compressor_pit[:, VINIT]
        pl_abs[v_mps < 0] = 0  # force pressure lift = 0 for reverse flow

        compressor_pit[:, PL] = pl_abs

    @classmethod
    def get_component_input(cls):
        """

        Get component input.

        :return:
        :rtype:
        """
        return [("name", dtype(object)),
                ("from_junction", "u4"),
                ("to_junction", "u4"),
                ("pressure_ratio", "f8"),
                ("in_service", 'bool')]