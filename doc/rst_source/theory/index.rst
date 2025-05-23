
Theory
==========


General
------------

.. toctree::
    :maxdepth: 3

    from_objects_to_matrices
    branch_model
    xfo_sc
    topology_processing

Topology
------------

.. toctree::
    :maxdepth: 3

    topology_processing

Power Flow
------------------

The following subsections include theory about the power flow algorithms supported by
**GridCal**. For control modes (both :ref:`reactive power control<q_control>` and
:ref:`transformer OLTC control<taps_control>`), refer to the
:ref:`Power Flow Driver API Reference<pf_driver>`.

.. toctree::
    :maxdepth: 3

    power_flow/newton_raphson
    power_flow/levenberg_marquardt
    power_flow/fast_decoupled
    power_flow/dc_approximation
    power_flow/linear_ac_power_flow
    power_flow/holomorphic_embedding
    power_flow/post_power_flow
    power_flow/continuation_power_flow
    power_flow/distributed_slack
    power_flow/generalized_power_flow


Optimal power flow
------------------------------------

.. toctree::
    :maxdepth: 3

    opf/opf
    opf/opf_dc_ts
    opf/opf_ac_ts
    opf/hydro
    opf/acopf
    opf/nodal_cap_ex
    opf/net_transfer_capacity


Short Circuit
------------------

.. toctree::
    :maxdepth: 3

    short_circuit/3_phase_sc


Linear factors
------------------------------------------------------------------------

.. toctree::
    :maxdepth: 3

    linear/ptdf
    linear/srap


Investments Evaluation
------------------------------------

.. toctree::
    :maxdepth: 3

    investments_evaluation
    investments_evaluation_nsga3