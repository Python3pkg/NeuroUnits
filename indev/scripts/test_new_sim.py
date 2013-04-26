

import neurounits
#import sys
import numpy as np
#import itertools

import pylab
import glob
#import warnings

from neurounits.codegen.python import simulate
from neurounits import NineMLComponent
from neurounits.locations import Locations


def test_new_sim():
     #src_files = sorted( glob.glob("/home/michael/hw_to_come//NeuroUnits/src/test_data/l4-9ml/std/*.9ml" ))
     src_files = Locations.get_default_9ml_locations()
     print src_files


     library_manager = neurounits.NeuroUnitParser.Parse9MLFiles( src_files)
     general_neuron_with_step_inj = library_manager.get('general_neuron_with_step_inj')
     comp = NineMLComponent.build_compound_component(
             component_name = 'Test1',
             instantiate={
                 'o1': general_neuron_with_step_inj,
                 'o2': general_neuron_with_step_inj,
                 'o3': general_neuron_with_step_inj,
                 'o4': general_neuron_with_step_inj,
                 },
             event_connections= [ 
                 ('o1/syntrigger/spike', 'o2/nrn/syn_excit/event'),  
                 ('o1/syntrigger/spike', 'o2/nrn/syn_inhib/event'),  
                 ('o1/syntrigger/spike', 'o3/nrn/syn_excit/event'),  
                 ('o2/syntrigger/spike', 'o3/nrn/syn_excit/event'),  

                 ('o4/syntrigger/spike', 'o2/nrn/syn_excit/event'),  
                 ('o3/syntrigger/spike', 'o4/nrn/syn_excit/event'),  
                ]
             )

     # Old version:
     #res = general_neuron_with_step_inj.simulate( times = np.arange(0, 0.1,0.00001),)

     # New version:
     res = simulate(comp, times = np.arange(0, 0.1,0.00001),)

     res.auto_plot()





if __name__=='__main__':
    test_new_sim()
    pylab.show()