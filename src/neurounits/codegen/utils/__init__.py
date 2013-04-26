


import pylab as plt



import networkx as nx
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance

import neurounits.ast as ast





def plot_networkx_graph(graph, show=True):
    plt.figure()
    objs, labels, colors = zip( * [ (d[0], d[1]['label'], d[1]['color'] ) for d in graph.nodes_iter(data=True) ] )
    nx.draw_graphviz(graph, font_size=10, iteration=200, node_color=colors,scale=1, labels=dict(zip(objs,labels)) )
    if show:
        plt.show()





class AnalogIntegrationBlock(object):
    def __init__(self, objs):
#        import neurounits.ast as ast
        self.state_variables = [o for o in objs if isinstance(o, ast.StateVariable)]
        self.assigned_variables = [o for o in objs if isinstance(o, ast.AssignedVariable)]
        self.rt_graphs = [o for o in objs if isinstance(o, ast.RTBlock)]
        assert len(objs) == len(self.state_variables) + len(self.assigned_variables) + len(self.rt_graphs)
        #self.assignments = []
        #self.rt_graphs = []


    def __repr__(self):
        return '<AnalogIntegrationBlock: SV: %s ASS: %s RTGrpahs: %s>' % (
                ','.join([ sv.symbol for sv in self.state_variables ] ),
                ','.join([ ass.symbol for ass in self.assigned_variables ] ),
                ','.join([ rt.name for rt in self.rt_graphs ] )
                )

    @property
    def objects(self,):
        return self.state_variables + self.assigned_variables + self.rt_graphs
        


def EventIntegrationBlock(object):
    def __init__(self, analog_blks):
        self.analog_blks = analog_blks
        




def build_analog_integration_blks(component):
    # Build the original dependance graph:
    graph = VisitorFindDirectSymbolDependance.build_direct_dependancy_graph(component)

    # Plot:
    do_plot = True and False
    if do_plot:
        plot_networkx_graph(graph, show=False)

    res = nx.components.strongly_connected_component_subgraphs(graph)

    # Get the strongly connected components, and the dependancies between the
    # nodes:
    scc = nx.strongly_connected_components(graph)
    cond = nx.condensation(graph, scc=scc)

    for node, node_data in cond.nodes_iter(data=True):
        print node, node_data


    ordering = reversed( nx.topological_sort(cond) )
    blks = []
    for o in ordering:
        blk = AnalogIntegrationBlock( objs = scc[o] )
        blks.append(blk)

    return blks








from collections import defaultdict
def build_event_blks(component, analog_blks):

    # Find out what the rt_graphs are dependant on: events & triggers:
    # =================================================================
    # 1. Make a map dependancies 'rt_graph -> state_variable/assignments'
    rt_graph_deps_triggers = defaultdict(set)
    dep_finder = VisitorFindDirectSymbolDependance()
    for tr in component._transitions_triggers:
        print 'TRANSITION:', repr(tr)
        trigger_deps = dep_finder.visit(tr.trigger)
        for tdep in trigger_deps:
            if tdep.symbol != 't':
                rt_graph_deps_triggers[tr.rt_graph].add(tdep)

    # 2. Make a map dependancies 'rt_graph -> event_ports'
    rt_graph_deps_events = defaultdict(set)
    for tr in component._transitions_events:
        print 'TRANSITION:', repr(tr)
        rt_graph_deps_events[tr.rt_graph].add(tr.port)

    # Find out what transitions particular state-variables
    # are dependant on because of assignments:
    # =========================================
    statevar_on_rt_deps= defaultdict(set)
    for tr in component.transitions:
        for action in tr.actions:
            if isinstance(action, ast.OnEventStateAssignment):
                statevar_on_rt_deps[action.lhs].add(tr.rt_graph)


    # OK, now lets build a new dependancy graph to work out transition/event
    # dependancies:
    # A. Start with the analog graph:
    graph = VisitorFindDirectSymbolDependance.build_direct_dependancy_graph(component)
    # B. Add the RT-graph nodes:
    for rt_graph in component._rt_graphs:
        graph.add_node(rt_graph, label=repr(rt_graph), color='orange')
    # C. Add the dependance of rt_graphs on trigger-conditions:
    for rt_graph, deps in rt_graph_deps_triggers.items():
        for dep in deps:
            graph.add_edge(rt_graph,dep,)
    # D. Add the dependance of state_varaibles on assignments in rt_graphs: 
    for sv, deps in statevar_on_rt_deps.items():
        for dep in deps:
            graph.add_edge(sv,dep,)
    # E. Event Dependancies:
    #  -- (Use the src event ports as the 'objects' in the graph:
    for inp in component.input_event_port_lut:
        graph.add_node(inp, label=repr(inp), color='brown')
    for out in component.output_event_port_lut:
        graph.add_node(out, label=repr(out), color='chocolate')
        
    #Output events are dependant on their rt_graphs:
    for tr in component.transitions:
        for a in tr.actions:
            if isinstance(a, ast.EmitEvent ):
                graph.add_edge(a.port, tr.rt_graph)

    #  -- RT graph dependance on input events:
    for tr in component._transitions_events:
        # The RT graph depends on the incoming events:
        graph.add_edge(tr.rt_graph, tr.port )

    # -- Input ports can depend on output ports:
    for conn in component._event_port_connections:
        graph.add_edge(conn.dst_port, conn.src_port)



    





    statevar_on_rt_deps= defaultdict(set)
    
    for d in graph.nodes_iter(data=True):
        print d
        print d[1]['label']

    do_plot=True
    if do_plot:
        plot_networkx_graph(graph, show=False)

    print rt_graph_deps_triggers
    print rt_graph_deps_events

    scc = nx.strongly_connected_components(graph)
    cond = nx.condensation(graph, scc=scc)
    
    #plot_networkx_graph(cond)
    plt.figure()
    nx.draw_graphviz(cond, font_size=10, iteration=200, ) 

    for node, node_data in cond.nodes_iter(data=True):
        print node, node_data

    for sc in scc:
        print sc



    # Build a dictionary mapping each state_variable to analog block that its in:
    obj_to_analog_block = {}
    for blk in analog_blks:
        for obj in blk.objects:
            assert not obj in obj_to_analog_block
            obj_to_analog_block[obj] = blk

    ordering = reversed( nx.topological_sort(cond) )

    ev_blks = []
    print 'Event Block ordering:'
    print '====================='
    for o in ordering:
        print
        print ' ---- %d ---- ' % o
        print scc[o]
        #for obj in scc[o]:
        #    print ' -- ', obj, 

        analog_blks = list(set( [obj_to_analog_block.get(obj,None) for obj in scc[o] ] ) )
        analog_blks = [blk for blk in analog_blks if blk is not None]
        print 'Analog Blocks:', len(analog_blks)

        ev = EventIntegrationBlock(analog_blks)
        ev_blks.append(ev)

    return ev_blks

    #print '====================='
    #
    #
    ##
    #
    #
    #
    #
    #
    #
    #
    #
    #plt.show()

    #

    ##for blk in analog_blks:
    ##    print 'Analysing Blk:', blk

    #pass


def separate_integration_blocks(component):
    print 'Separating Integration blocks'

    # Make some cleanups to the component to start with:
    component.close_all_analog_reduce_ports()
    from remove_unused_rt_graphs import remove_unused_rt_graphs
    remove_unused_rt_graphs(component)


    # Step 1:
    # Build the AnalogIntegrationBlocks, based on what  variables needed to be
    # solved by the  integrator together:
    # These are topologically sorted, so the first ones need to be solved before
    # the later ones:
    analog_blks = build_analog_integration_blks(component)


    for o in analog_blks:
        print o

    # Step 2:
    # Work out the event dependancies between the blocks.
    # These can come from:
    # Events, or transitions that change state equations

    build_event_blks(component=component, analog_blks=analog_blks)

    return build_event_blks




    #for blk in blks:
    #    print blk



    #print 'Done'
    #assert False




    #from dependancy_new import get_dependancy_graph

    #get_dependancy_graph(component)


