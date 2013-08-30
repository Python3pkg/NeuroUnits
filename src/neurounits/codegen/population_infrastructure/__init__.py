




class Population(object):
    def __init__(self, name, component, size):
        self.name = name
        self.component = component
        self.size = size


    def get_subpopulation(self, start_index, end_index, subname, autotag):
        return SubPopulation(population=self, 
                             start_index=start_index, 
                             end_index=end_index, 
                             subname=subname,
                             autotag=autotag )
    @property
    def population(self):
        return self
    @property
    def indices(self):
        return (0, self.size)

class SubPopulation(object):
    def __init__(self, population, start_index, end_index, subname, autotag):
        self._population = population
        self.start_index = start_index
        self.end_index = end_index
        self.subname = subname
        self.autotag = autotag

    @property
    def population(self):
        return self._population
    @property
    def indices(self):
        return (self.start_index, self.end_index)
    @property
    def component(self):
        return self.population.component


class Projection(object):
    def __init__(self, name, src_population, dst_population):
        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population



class ElectricalSynapseProjection(Projection):
    def __init__(self, connection_probability, strength_ohm, injected_port_name, **kwargs):
        super(ElectricalSynapseProjection, self).__init__(**kwargs)
        self.connection_probability = connection_probability
        self.strength_ohm = strength_ohm
        self.injected_port_name = injected_port_name








class EventPortConnector(object):
    def __init__(self, src_population, dst_population, src_port_name, dst_port_name, name, connector):
        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population
        self.src_port = src_population.component.output_event_port_lut.get_single_obj_by(symbol=src_port_name)
        self.dst_port = src_population.component.input_event_port_lut.get_single_obj_by(symbol=dst_port_name)
        self.connector = connector




class PopRec(object):
    def __init__(self, global_offset, size, src_population, src_pop_start_index, node, tags):
        self.global_offset = global_offset
        self.size = size
        self.src_population = src_population
        self.src_pop_start_index = src_pop_start_index
        self.node = node
        self.tags = tags

    def __str__(self):
        return "<PopRec [global_offset: %s , size: %s] from [src_pop: %s recording: %s local_offset: %s ] {Tags:%s}>" % ( 
                        self.global_offset, self.size, self.src_population.name, self.src_pop_start_index, self.node.symbol, self.tags )


class Network(object):
    def __init__(self, ):
        self.populations = []
        self.event_port_connectors = []
        self.electrical_synapse_projections = []
        self.additional_events = []
        
        
        self._record_traces = defaultdict( list )
        self._record_output_events = defaultdict( list )
        self._record_input_events = defaultdict( list )
        
        
    def record_traces(self, subpopulations, terminal_node_name):
        if isinstance(subpopulations, (Population,SubPopulation)):
            subpopulations = [subpopulations]
        for subpop in subpopulations:
            self._record_trace_for_population(subpop, terminal_node_name)
    
    def record_output_events(self, subpopulations, port_name):
        if isinstance(subpopulations, (Population,SubPopulation)):
            subpopulations = [subpopulations]
        for subpop in subpopulations:
            self._record_output_events_for_population(subpop, port_name)
            
    def record_input_events(self, subpopulations, port_name):
        if isinstance(subpopulations, (Population,SubPopulation)):
            subpopulations = [subpopulations]
        for subpop in subpopulations:
            self._record_input_events_for_population(subpop, port_name)        
        
        
        
    def _record_trace_for_population(self, subpop, terminal_node_name):
        population = subpop.population
        terminal_node = population.component.get_terminal_obj(terminal_node_name)
        self._record_traces[(population, terminal_node)].append( (subpop.indices, subpop.autotag) )

    def _record_output_events_for_population(self, subpop, terminal_node_name):
        population = subpop.population
        terminal_node = population.component.output_event_port_lut.get_single_obj_by(symbol=terminal_node_name)
        self._record_output_events[(population, terminal_node)].append( (subpop.indices, subpop.autotag) )

    def _record_input_events_for_population(self, subpop, terminal_node_name):
        population = subpop.population
        terminal_node = population.component.input_event_port_lut.get_single_obj_by(symbol=terminal_node_name)
        self._record_input_events[(population, terminal_node)].append( (subpop.indices, subpop.autotag) )

        
        
    def finalise(self):
        # Work out which traces to record:
        all_recordings = []
        
        for (population, terminal_node), values in sorted(self._record_traces.items()):
            for indices, autotag in sorted(values):
                global_offset = 0 if all_recordings == [] else ( all_recordings[-1].global_offset + all_recordings[-1].size )
                size = indices[1] - indices[0]
                all_recordings.append( PopRec( global_offset=global_offset, size=size, src_population=population, src_pop_start_index=indices[0], node=terminal_node, tags=autotag ) )
                
        # 
        print 'Traces recorded:'
        for rec in all_recordings:
            print rec
            
        
        
        #assert False
        

    def add(self, obj):
        if isinstance( obj, Population):
            self.populations.append(obj)

        elif isinstance( obj, ElectricalSynapseProjection):
            self.electrical_synapse_projections.append(obj)

        elif isinstance( obj, EventPortConnector):
            self.event_port_connectors.append(obj)

        else:
            assert False


    def provide_events(self, population, event_port, evt_details ):
        event_port = population.component.input_event_port_lut.get_single_obj_by(symbol=event_port)

        self.additional_events.append( 
            (population, event_port, evt_details )
                )




class PopulationConnector(object):
    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor):
        raise NotImplementedError()



class AllToAllConnector(PopulationConnector):
    def __init__(self, connection_probability):
        self.connection_probability = connection_probability

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor):

        from mako.template import Template
        tmpl = Template("""
        for(IntType i=IntType(0);i< IntType(${src_pop_size_expr});i++)
        {
            for(IntType j=IntType(0);j<IntType(${dst_pop_size_expr});j++)
            {
                if(i==j) continue;
                if(rnd::rand_in_range(0,1) < ${connection_probability})
                {
                    ${add_connection_functor("i","j")}; 
                }
            }
        }

        """)

        return tmpl.render( 
                src_pop_size_expr = src_pop_size_expr,
                dst_pop_size_expr = dst_pop_size_expr,
                add_connection_functor = add_connection_functor,
                connection_probability = self.connection_probability, 
                )


from collections import defaultdict

class ExplicitIndices(PopulationConnector):
    def __init__(self, indices):
        self.indices = indices

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor):

        src_tgt_map = defaultdict( set)
        for i,j in self.indices:
            src_tgt_map[i].add(j);
        

        
        from mako.template import Template
        tmpl = Template('''

        %for src, tgts in src_tgt_map.items():
            <%tgt_str = ','.join( [str(t) for t in tgts ] ) %>
            IntType tgts_from_${src}[] = { ${tgt_str} };
            IntType tgts_from_${src}_len = ${len(tgts)} ;

            // # TODO: refactor this out properly:
            projections[${src}].assign(tgts_from_${src}, tgts_from_${src} + tgts_from_${src}_len);
        %endfor

        ''')
        return tmpl.render(
                indices=self.indices,
                add_connection_functor = add_connection_functor,
                src_tgt_map=src_tgt_map
                )
