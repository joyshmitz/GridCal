# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.  
# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

from GridCalEngine.IO.base.units import UnitMultiplier, UnitSymbol
from GridCalEngine.IO.cim.cgmes.cgmes_v3_0_0.devices.energy_connection import EnergyConnection
from GridCalEngine.IO.cim.cgmes.cgmes_enums import cgmesProfile, UnitSymbol


class EnergySource(EnergyConnection):
	def __init__(self, rdfid='', tpe='EnergySource'):
		EnergyConnection.__init__(self, rdfid, tpe)

		from GridCalEngine.IO.cim.cgmes.cgmes_v3_0_0.devices.energy_scheduling_type import EnergySchedulingType
		self.EnergySchedulingType: EnergySchedulingType | None = None
		self.nominalVoltage: float = None
		self.pMin: float = None
		self.pMax: float = None
		self.r: float = None
		self.r0: float = None
		self.rn: float = None
		self.x: float = None
		self.x0: float = None
		self.xn: float = None
		self.activePower: float = None
		self.reactivePower: float = None
		self.voltageAngle: float = None
		self.voltageMagnitude: float = None

		self.register_property(
			name='EnergySchedulingType',
			class_type=EnergySchedulingType,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.none,
			description='''Energy Scheduling Type of an Energy Source.''',
			profiles=[]
		)
		self.register_property(
			name='nominalVoltage',
			class_type=float,
			multiplier=UnitMultiplier.k,
			unit=UnitSymbol.V,
			description='''Electrical voltage, can be both AC and DC.''',
			profiles=[]
		)
		self.register_property(
			name='pMin',
			class_type=float,
			multiplier=UnitMultiplier.M,
			unit=UnitSymbol.W,
			description='''Product of RMS value of the voltage and the RMS value of the in-phase component of the current.''',
			profiles=[]
		)
		self.register_property(
			name='pMax',
			class_type=float,
			multiplier=UnitMultiplier.M,
			unit=UnitSymbol.W,
			description='''Product of RMS value of the voltage and the RMS value of the in-phase component of the current.''',
			profiles=[]
		)
		self.register_property(
			name='r',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.ohm,
			description='''Resistance (real part of impedance).''',
			profiles=[]
		)
		self.register_property(
			name='r0',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.ohm,
			description='''Resistance (real part of impedance).''',
			profiles=[]
		)
		self.register_property(
			name='rn',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.ohm,
			description='''Resistance (real part of impedance).''',
			profiles=[]
		)
		self.register_property(
			name='x',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.ohm,
			description='''Reactance (imaginary part of impedance), at rated frequency.''',
			profiles=[]
		)
		self.register_property(
			name='x0',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.ohm,
			description='''Reactance (imaginary part of impedance), at rated frequency.''',
			profiles=[]
		)
		self.register_property(
			name='xn',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.ohm,
			description='''Reactance (imaginary part of impedance), at rated frequency.''',
			profiles=[]
		)
		self.register_property(
			name='activePower',
			class_type=float,
			multiplier=UnitMultiplier.M,
			unit=UnitSymbol.W,
			description='''Product of RMS value of the voltage and the RMS value of the in-phase component of the current.''',
			profiles=[]
		)
		self.register_property(
			name='reactivePower',
			class_type=float,
			multiplier=UnitMultiplier.M,
			unit=UnitSymbol.VAr,
			description='''Product of RMS value of the voltage and the RMS value of the quadrature component of the current.''',
			profiles=[]
		)
		self.register_property(
			name='voltageAngle',
			class_type=float,
			multiplier=UnitMultiplier.none,
			unit=UnitSymbol.rad,
			description='''Phase angle in radians.''',
			profiles=[]
		)
		self.register_property(
			name='voltageMagnitude',
			class_type=float,
			multiplier=UnitMultiplier.k,
			unit=UnitSymbol.V,
			description='''Electrical voltage, can be both AC and DC.''',
			profiles=[]
		)
