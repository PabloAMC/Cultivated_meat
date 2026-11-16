"""Run a side-study test with the model as its note was computed.

Several side studies (tank size, thick culture, growth-factor and doubling bounds, the nutrient floor, the least medium
per kg, the case without perfusion) were written before the bubble protectant, the antifoam's effect on oxygen
transfer and the yeast-style plant's bought oxygen were counted (2026-11-15, late). Their tests pin the figures their
notes quote, so they set those three inputs back for the whole process. Import this module BEFORE any model module
other than `inputs` and `floor_physics`, so the scenarios' tank designs are chosen under the same settings.
"""
from dataclasses import replace

import floor_physics
import inputs

for _k, _v in floor_physics.BEFORE_PROTECTANT.items():
    inputs.REGISTRY[_k] = replace(inputs.REGISTRY[_k], value=_v)
