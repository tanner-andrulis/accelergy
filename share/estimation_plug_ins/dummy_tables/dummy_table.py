from accelergy.plug_in_interface.interface import *


class DummyTable(AccelergyPlugIn):
    """
    A dummy estimation plug-in
    Note that this plug-in is just a placeholder to illustrate the estimation plug-in interface
    It can be used as a template for creating user-defined plug-ins
    The energy values returned by this plug-in is not meaningful
    """
    # -------------------------------------------------------------------------------------
    # Interface functions, function name, input arguments, and output have to adhere
    # -------------------------------------------------------------------------------------
    def __init__(self):
        self.estimator_name =  "dummy_table"

    def primitive_action_supported(self, query: AccelergyQuery) -> AccuracyEstimation:
        class_name = query.class_name
        attributes = query.class_attrs
        action_name = query.action_name
        arguments = query.action_args
        if attributes.get('technology', None) == -1:
            return AccuracyEstimation(100)
        self.logger.info('Dummy Table only supports technology -1')
        return AccuracyEstimation(0)

    def estimate_energy(self, query: AccelergyQuery) -> Estimation:
        class_name = query.class_name
        attributes = query.class_attrs
        action_name = query.action_name
        arguments = query.action_args
        
        energy_pj = 0 if action_name == 'idle' else 1
        return Estimation(energy_pj, 'p') # Dummy returns 1 for all non-idle actions

    def primitive_action_supported(self, query: AccelergyQuery) -> AccuracyEstimation:
        class_name = query.class_name
        attributes = query.class_attrs
        action_name = query.action_name
        arguments = query.action_args
        if attributes.get('technology', None) == -1:
            return AccuracyEstimation(100)
        self.logger.info('Dummy Table only supports technology -1')
        return AccuracyEstimation(0)

    def estimate_area(self, query: AccelergyQuery) -> Estimation:
        class_name = query.class_name
        attributes = query.class_attrs
        action_name = query.action_name
        arguments = query.action_args
        return Estimation(1, 'u^2') # Dummy returns 1 for all non-idle actions
