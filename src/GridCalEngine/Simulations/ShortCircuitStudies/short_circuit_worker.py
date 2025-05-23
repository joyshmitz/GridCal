# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

from typing import Tuple
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import inv
from GridCalEngine.DataStructures.numerical_circuit import NumericalCircuit
from GridCalEngine.Simulations.ShortCircuitStudies.short_circuit import short_circuit_3p, short_circuit_unbalance
from GridCalEngine.Topology.admittance_matrices import compute_admittances
from GridCalEngine.Simulations.ShortCircuitStudies.short_circuit_results import ShortCircuitResults
from GridCalEngine.Simulations.PowerFlow.NumericalMethods.common_functions import polar_to_rect
from GridCalEngine.enumerations import FaultType
from GridCalEngine.basic_structures import CxVec, Vec


def short_circuit_post_process(
        calculation_inputs: NumericalCircuit,
        V: CxVec,
        branch_rates: Vec,
        Yf: sp.csc_matrix,
        Yt: sp.csc_matrix
) -> Tuple[CxVec, CxVec, CxVec, CxVec, CxVec, CxVec, CxVec]:
    """
    Compute the important results for short-circuits
    :param calculation_inputs: instance of Circuit
    :param V: Voltage solution array for the circuit buses
    :param branch_rates: Array of branch ratings
    :param Yf: From admittance matrix
    :param Yt: To admittance matrix
    :return: Sf (MVA), If (p.u.), loading (p.u.), losses (MVA), Sbus(MVA)
    """

    Vf = V[calculation_inputs.passive_branch_data.F]
    Vt = V[calculation_inputs.passive_branch_data.T]

    # Branches current, loading, etc
    If = Yf * V
    It = Yt * V
    Sf = Vf * np.conj(If)
    St = Vt * np.conj(It)

    # Branch losses in MVA (not really important for short-circuits)
    losses = (Sf + St) * calculation_inputs.Sbase

    # branch voltage increment
    Vbranch = Vf - Vt

    # Branch power in MVA
    Sfb = Sf * calculation_inputs.Sbase
    Stb = St * calculation_inputs.Sbase

    # Branch loading in p.u.
    loading = Sfb / (branch_rates + 1e-9)

    return Sfb, Stb, If, It, Vbranch, loading, losses


def short_circuit_ph3(nc: NumericalCircuit, Vpf: CxVec, Zf: CxVec, bus_index: int):
    """
    Run a 3-phase short circuit simulation for a single island
    :param nc: NumericalCircuit
    :param Vpf: Power flow voltage vector applicable to the island
    :param Zf: Short circuit impedance vector applicable to the island
    :param bus_index: Bus index
    :return: short circuit results
    """
    adm = nc.get_admittance_matrices()
    Y_gen = nc.generator_data.get_Yshunt(seq=1)
    Y_batt = nc.battery_data.get_Yshunt(seq=1)
    Ybus_gen_batt = adm.Ybus + sp.diags(Y_gen) + sp.diags(Y_batt)

    # Compute the short circuit
    V, SCpower, ICurrent = short_circuit_3p(bus_idx=bus_index,
                                            Ybus=Ybus_gen_batt,
                                            Vbus=Vpf,
                                            Vnom=nc.bus_data.Vnom,
                                            Zf=Zf,
                                            baseMVA=nc.Sbase)

    (Sfb, Stb, If, It, Vbranch,
     loading, losses) = short_circuit_post_process(calculation_inputs=nc,
                                                   V=V,
                                                   branch_rates=nc.passive_branch_data.rates,
                                                   Yf=adm.Yf,
                                                   Yt=adm.Yt)

    # voltage, Sf, loading, losses, error, converged, Qpv
    results = ShortCircuitResults(n=nc.nbus,
                                  m=nc.nbr,
                                  n_hvdc=nc.nhvdc,
                                  bus_names=nc.bus_data.names,
                                  branch_names=nc.passive_branch_data.names,
                                  hvdc_names=nc.hvdc_data.names,
                                  bus_types=nc.bus_data.bus_types,
                                  area_names=None)

    results.SCpower = SCpower
    results.ICurrent = ICurrent
    results.Sbus1 = nc.get_power_injections_pu() * nc.Sbase  # MVA
    results.voltage1 = V
    results.Sf1 = Sfb  # in MVA already
    results.St1 = Stb  # in MVA already
    results.If1 = If  # in p.u.
    results.It1 = It  # in p.u.
    results.Vbranch1 = Vbranch
    results.loading1 = loading
    results.losses1 = losses

    return results


def short_circuit_unbalanced(nc: NumericalCircuit,
                             Vpf: CxVec,
                             Zf: CxVec,
                             bus_index: int,
                             fault_type: FaultType):
    """
    Run an unbalanced short circuit simulation for a single island
    :param nc:
    :param Vpf: Power flow voltage vector applicable to the island
    :param Vnom: Buses nominal voltages (kV)
    :param Zf: Short circuit impedance vector applicable to the island
    :param bus_index: Index of the failed bus
    :param fault_type: FaultType
    :return: short circuit results
    """

    # build Y0, Y1, Y2
    nbr = nc.nbr
    nbus = nc.nbus

    Y_gen0 = nc.generator_data.get_Yshunt(seq=0)
    Y_batt0 = nc.battery_data.get_Yshunt(seq=0)
    Yshunt_bus0 = Y_gen0 + Y_batt0

    Cf = nc.passive_branch_data.Cf.tocsc()
    Ct = nc.passive_branch_data.Ct.tocsc()

    adm0 = compute_admittances(R=nc.passive_branch_data.R0,
                               X=nc.passive_branch_data.X0,
                               G=nc.passive_branch_data.G0,  # renamed, it was overwritten
                               B=nc.passive_branch_data.B0,
                               tap_module=nc.active_branch_data.tap_module,
                               vtap_f=nc.passive_branch_data.virtual_tap_f,
                               vtap_t=nc.passive_branch_data.virtual_tap_t,
                               tap_angle=nc.active_branch_data.tap_angle,
                               Cf=Cf,
                               Ct=Ct,
                               Yshunt_bus=Yshunt_bus0,
                               conn=nc.passive_branch_data.conn,
                               seq=0,
                               add_windings_phase=True)

    Y_gen1 = nc.generator_data.get_Yshunt(seq=1)
    Y_batt1 = nc.battery_data.get_Yshunt(seq=1)
    Yshunt_bus1 = nc.get_Yshunt_bus_pu() + Y_gen1 + Y_batt1

    adm1 = compute_admittances(R=nc.passive_branch_data.R,
                               X=nc.passive_branch_data.X,
                               G=nc.passive_branch_data.G,
                               B=nc.passive_branch_data.B,
                               tap_module=nc.active_branch_data.tap_module,
                               vtap_f=nc.passive_branch_data.virtual_tap_f,
                               vtap_t=nc.passive_branch_data.virtual_tap_t,
                               tap_angle=nc.active_branch_data.tap_angle,
                               Cf=Cf,
                               Ct=Ct,
                               Yshunt_bus=Yshunt_bus1,
                               conn=nc.passive_branch_data.conn,
                               seq=1,
                               add_windings_phase=True)

    Y_gen2 = nc.generator_data.get_Yshunt(seq=2)
    Y_batt2 = nc.battery_data.get_Yshunt(seq=2)
    Yshunt_bus2 = Y_gen2 + Y_batt2

    adm2 = compute_admittances(R=nc.passive_branch_data.R2,
                               X=nc.passive_branch_data.X2,
                               G=nc.passive_branch_data.G2,
                               B=nc.passive_branch_data.B2,
                               tap_module=nc.active_branch_data.tap_module,
                               vtap_f=nc.passive_branch_data.virtual_tap_f,
                               vtap_t=nc.passive_branch_data.virtual_tap_t,
                               tap_angle=nc.active_branch_data.tap_angle,
                               Cf=Cf,
                               Ct=Ct,
                               Yshunt_bus=Yshunt_bus2,
                               conn=nc.passive_branch_data.conn,
                               seq=2,
                               add_windings_phase=True)

    """
    Initialize Vpf introducing phase shifts
    No search algo is needed. Instead, we need to solve YV=0,
    get the angle of the voltages from here and add them to the
    original Vpf. Y should be Yseries (avoid shunts).
    In more detail:
    -----------------   -----   -----
    |   |           |   |Vvd|   |   |
    -----------------   -----   -----
    |   |           |   |   |   |   |
    |   |           | x |   | = |   |
    | Yu|     Yx    |   | V |   | 0 |
    |   |           |   |   |   |   |
    |   |           |   |   |   |   |
    -----------------   -----   -----

    where Yu = Y1.Ybus[pqpv, vd], Yx = Y1.Ybus[pqpv, pqpv], so:
    V = - inv(Yx) Yu Vvd
    ph_add = np.angle(V)
    Vpf[pqpv] *= np.exp(1j * ph_add)
    """

    adm_series = compute_admittances(R=nc.passive_branch_data.R,
                                     X=nc.passive_branch_data.X,
                                     G=np.zeros(nbr),
                                     B=np.zeros(nbr),
                                     tap_module=nc.active_branch_data.tap_module,
                                     vtap_f=nc.passive_branch_data.virtual_tap_f,
                                     vtap_t=nc.passive_branch_data.virtual_tap_t,
                                     tap_angle=nc.active_branch_data.tap_angle,
                                     Cf=Cf,
                                     Ct=Ct,
                                     Yshunt_bus=np.zeros(nbus, dtype=complex),
                                     conn=nc.passive_branch_data.conn,
                                     seq=1,
                                     add_windings_phase=True)

    indices = nc.get_simulation_indices()

    vd = indices.vd
    pqpv = indices.no_slack

    # Y1_arr = np.array(adm_series.Ybus.todense())
    # Yu = Y1_arr[np.ix_(pqpv, vd)]
    # Yx = Y1_arr[np.ix_(pqpv, pqpv)]
    #
    # I_vd = Yu * np.array(Vpf[vd])
    # Vpqpv_ph = - np.linalg.inv(Yx) @ I_vd

    # add the voltage phase due to the slack, to the rest of the nodes
    I_vd = adm_series.Ybus[np.ix_(pqpv, vd)] * Vpf[vd]
    Vpqpv_ph = - sp.linalg.spsolve(adm_series.Ybus[np.ix_(pqpv, pqpv)], I_vd)
    ph_add = np.angle(Vpqpv_ph)
    Vpf[pqpv] = polar_to_rect(np.abs(Vpf[pqpv]), np.angle(Vpf[pqpv]) + ph_add.T)

    # solve the fault
    V0, V1, V2, SCC, ICC = short_circuit_unbalance(bus_idx=bus_index,
                                                   Y0=adm0.Ybus,
                                                   Y1=adm1.Ybus,
                                                   Y2=adm2.Ybus,
                                                   Vnom=nc.bus_data.Vnom,
                                                   Vbus=Vpf,
                                                   Zf=Zf,
                                                   fault_type=fault_type,
                                                   baseMVA=nc.Sbase)

    # process results in the sequences
    (Sfb0, Stb0, If0, It0, Vbranch0,
     loading0, losses0) = short_circuit_post_process(calculation_inputs=nc,
                                                     V=V0,
                                                     branch_rates=nc.passive_branch_data.rates,
                                                     Yf=adm0.Yf,
                                                     Yt=adm0.Yt)

    (Sfb1, Stb1, If1, It1, Vbranch1,
     loading1, losses1) = short_circuit_post_process(calculation_inputs=nc,
                                                     V=V1,
                                                     branch_rates=nc.passive_branch_data.rates,
                                                     Yf=adm1.Yf,
                                                     Yt=adm1.Yt)

    (Sfb2, Stb2, If2, It2, Vbranch2,
     loading2, losses2) = short_circuit_post_process(calculation_inputs=nc,
                                                     V=V2,
                                                     branch_rates=nc.passive_branch_data.rates,
                                                     Yf=adm2.Yf,
                                                     Yt=adm2.Yt)

    # voltage, Sf, loading, losses, error, converged, Qpv
    results = ShortCircuitResults(n=nc.nbus,
                                  m=nc.nbr,
                                  n_hvdc=nc.nhvdc,
                                  bus_names=nc.bus_data.names,
                                  branch_names=nc.passive_branch_data.names,
                                  hvdc_names=nc.hvdc_data.names,
                                  bus_types=nc.bus_data.bus_types,
                                  area_names=None)

    results.SCpower = SCC
    results.ICurrent = ICC

    results.voltage0 = V0
    results.Sf0 = Sfb0  # in MVA already
    results.St0 = Stb0  # in MVA already
    results.If0 = If0  # in p.u.
    results.It0 = It0  # in p.u.
    results.Vbranch0 = Vbranch0
    results.loading0 = loading0
    results.losses0 = losses0

    results.voltage1 = V1
    results.Sf1 = Sfb1  # in MVA already
    results.St1 = Stb1  # in MVA already
    results.If1 = If1  # in p.u.
    results.It1 = It1  # in p.u.
    results.Vbranch1 = Vbranch1
    results.loading1 = loading1
    results.losses1 = losses1

    results.voltage2 = V2
    results.Sf2 = Sfb2  # in MVA already
    results.St2 = Stb2  # in MVA already
    results.If2 = If2  # in p.u.
    results.It2 = It2  # in p.u.
    results.Vbranch2 = Vbranch2
    results.loading2 = loading2
    results.losses2 = losses2

    return results
