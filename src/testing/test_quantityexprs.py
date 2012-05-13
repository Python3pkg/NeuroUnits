


import subprocess
import os

from neurounits.neurounitparser import NeuroUnitParser
from mredoc.objects.core import Document, Table
from mredoc.writers.html import HTMLWriter
from mredoc.writers.latex import LatexWriter


from util_test_locations import TestLocations



# Missing Tests:
# ###############


# * meters vs milli (m)
# * Check nested functions:



# TODO: Simple Systems:
#  - FitzHugh Nagumo ()
#  - Morris Leccar
#  - Van de Pol




def apply_reps(s,reps):
    for (a,b) in reps:
        s = s.replace(a,b)
    return s


# General Functions:
# ###################
def verify_equivalence_with_gnuunits(a,b):

    # Some replaces:
    reps = [('um','microm'), ('uF','micro-F')]

    a = apply_reps(a,reps)
    b = apply_reps(b,reps)

    cmd = 'units', '-1', '-s','--compact',"%s"%a,"%s"%b
    cmd_str = " ".join(cmd)
    print cmd_str
    op = subprocess.check_output( cmd,  )
    print op
    assert op.strip() == "1"







# Testing NeuroUnits.QuantitySimple:
# ###################################

valid_quantitysimple= [
#                   A           B               Test with GNU units
                   ("1000V",    "1kV",         True  ),
                   ("1000mV",   "1 V",         True  ),

                   ("0.1",      "1e-1",        True  ),
                   ("400",      "4e2",         True  ),
                   ("10",       "1e1",         True  ),
                   ("1",        "1e0",         True  ),
                   ("1.54",     "1.54e0",      True  ),
                   ("0.324",    "3240.e-4",    True  ),

                   ("0.324m",    "324mm",      True  ),
                   ("0.324m",    "32.4cm",     True  ),
                   ("0.324m",    "324e3um",    False  ),

                   ("1m2",    "1e6 mm2",        True  ),
                   ("1m2",    "1e4 cm2",        True  ),
                   ("1cm2",    "100.0 mm2",     True  ),
                   ("1cm2",    "100.0e6 um2",   True  ),

                   ("1mA/cm2",    "10 pA/um2",    True  ),
                   ("1mA cm-2",   "10 pA/um2",    False  ),
                   ("1mA cm-2",   "10 pA um-2",   False  ),

                   ]






def test_quantitysimple():
    data = []

    for (a,b, check_with_gnu) in valid_quantitysimple:
        A = NeuroUnitParser.QuantitySimple(a)
        B = NeuroUnitParser.QuantitySimple(b)

        if check_with_gnu:
            verify_equivalence_with_gnuunits(a,b)

        pcA =  ((A-B)/A).dimensionless()
        pcB =  ((A-B)/B).dimensionless()
        assert pcA==0
        assert pcB==0
        data.append ( [a,b, str(A), str(B), str(pcA), str(pcB)] )

    header = "A|B|Parsed(A)|Parsed(B)|PC(A)|PC(B)".split("|")
    return  Table( header=header, data=data)




required_libraries = ["std.math","std.geom","std.neuro",]

valid_quantity_exprs = [
                    ( '1.0',       "1.0",                                                               True ),

                    # From Koch, Biophysics of Computation:
                    # #####################################
                    # Pg. 7:
                    ( 'std.geom.area_of_sphere(r=5um) * {1 uF/cm2} * {-70mV}', "-0.22e-12 C",            False ),
                    # Pg. 11:
                    ('{100 megaohm} * {100 pF}','10 ms',                                                 False),
                    # Pg. 32:
                    ('std.neuro.space_constant(d=4um,Ri={200 ohm cm},Rm={20e3 ohm cm2})', '1mm',         False),
                    # Pg. 34:
                    ('std.neuro.Rinf_sealed_end(d=2um,Rm=10e5 Ohm cm2)',                   '3000 GOhm',  False),
                    # Pg. 42:
                    ('std.neuro.space_constant(d=2um,Ri=200 Ohm cm,Rm=50000ohm cm2)','1.581um',          False),
#                    # Pg. 151:
                    ('1/({0.3mS/cm2})','3333 ohm cm2',                                                   False),
                    ('{1uF/cm2} * {3333 ohm cm2}','0.85ms',                                              False),

                    # Current, Voltage, Conductance:
                    # ##############################
                    # V = I * R and V = I / G
                    ("1V",          "{1A}*{1ohm}",          False),
                    ("1V",          "{1A}/{1S}",            False),
                    ("10V",         "{10A}/{1S}",           False),
                    ("10V",         "{1A}/{0.1S}",          False),
                    ("1mV",         "{1mA}/{1S}",           False),
                    ("{1mV/cm2}",     "{1mA cm-2}/{1S}",    False),
                    ("{1mV/cm2}",     "{10pA um-2}/{1S}",   False),



                    # Check that builtin functions handle units properly:
                    # Functions must be dimensionless, and
                    ("-5.0687e-1",     "std.math.sin(100)",                     False),
                    #("0",              "std.math.sin(0)",                      False),
                    ("-5.0687e-1",     "std.math.sin({0.1kV}/{1V})",            False),
                    ("-5.0687e-1",     "std.math.sin({1V}/{10mV})",             False),


                    # Check user defined functions:
                    ("std.geom.area_of_sphere( r=5um)",              "1um2", False ),
                    ("std.geom.area_of_sphere( r={5um}+{1um})",      "1um2", False ),
                    ("std.geom.area_of_sphere( {5um}+{1um})",        "1um2", False ),
                    ("std.geom.area_of_sphere( {5um}/3 )",           "1um2", False ),
                    ("std.geom.area_of_sphere( {5um2}/{1m} )",       "1um2", False ),
                    ("std.geom.area_of_sphere( r={5um2}/{1mm} )",    "1um2", False ),



                    ]



class FunctionCallDimensionError():
    pass
class FunctionCallParameterMismatch():
    pass

invalid_exprs = [
        # Check  the parameters to builtin function calls:
        ("sin( 0.0 )",                  None) ,
        ("sin( 1.0 )",                  None) ,
        ("sin( {10mV} )",               FunctionCallDimensionError) ,
        ("sin( )",                      FunctionCallParameterMismatch),
        ("sin( 0.0, 0.0 )",             FunctionCallParameterMismatch),

        ("area_of_sphere( 10um )",      None),
        ("area_of_sphere( r=10um )",    None),
        ("area_of_sphere( 10mV )",      FunctionCallDimensionError),
        ("area_of_sphere( r=10mV )",    FunctionCallDimensionError),
        ("area_of_sphere( 10 )",        FunctionCallDimensionError),
        ("area_of_sphere( 10 )",        FunctionCallDimensionError),
        ("area_of_sphere( )",           FunctionCallParameterMismatch),
        ("area_of_sphere( 0.0, 0.0 )",  FunctionCallParameterMismatch),
        ("area_of_sphere( d=0.0um )",   FunctionCallParameterMismatch),




        ]




def test_quantityexpr():
    data = []

    for (a,b, check_with_gnu) in valid_quantity_exprs:
        print 'a:',a
        print 'b:',b
        A = NeuroUnitParser.QuantityExpr(a)
        print 'LOADING B'
        B = NeuroUnitParser.QuantityExpr(b)


        if check_with_gnu:
            verify_equivalence_with_gnuunits(a,b)
        print "typeA:",type(A)
        print "typeB:",type(B)

        pcA =  ((A-B)/A).dimensionless()
        pcB =  ((A-B)/B).dimensionless()
        data.append ( [a,b, "$%s$"%(A.FormatLatex()), "$%s$"%(B.FormatLatex()), str(pcA), str(pcB)] )

    header = "A|B|Parsed(A)|Parsed(B)|PC(A)|PC(B)".split("|")
    return  Table( header=header, data=data)









valid_functions = [
                    ('f(x,y) = x**2 + 2*y + 1',
                        [
                        ( {'x':1, 'y':34}, 45 ),
                        ( {'x':5, 'y':34}, 45 ),
                        ]
                    ),

                    ('f(x,y,z) = x**2 + 2*y + 1 + x*y',
                        [
                        ( {'x':1, 'y':34, 'z':1}, 45 ),
                        ( {'x':5, 'y':34}, 45 ),
                        ]
                    ),
                    ]


def test_function():
    raise NotImplementedError()


def test_invalid_units():
    raise NotImplementedError()







def load():
    r1 = test_quantitysimple()
    r2 = test_quantityexpr()

    #test_function()
    #test_invalid_units()

    #doc = Document( r1,r2 )
    return [r1,r2]#,r2]




# Hook into automatic documentation:
from test_base import ReportGenerator
class SingleLinesDoc(ReportGenerator):
    def __init__(self):
        ReportGenerator.__init__(self, "SingleLines")
    def __call__(self):
        #return []
        return load()
SingleLinesDoc()





def main():
    sections = load()

    doc = Document( *sections )

    opdir = os.path.join( TestLocations.getTestOutputDir(), 'quantity_exprs_valid' )

    HTMLWriter.BuildHTML(doc, os.path.join(opdir, 'html') )
    LatexWriter.BuildPDF(doc, os.path.join(opdir, 'all.pdf') )


if __name__ == "__main__":
    main()