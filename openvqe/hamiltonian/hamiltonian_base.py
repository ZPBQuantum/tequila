"""
Base Class for OpenVQE Hamiltonians
Implements all functions which are needed by as good as all derived classes
"""

from dataclasses import dataclass
from openvqe.abc import OpenVQEModule, OpenVQEParameters, parametrized
from openvqe import OpenVQEParameterError, OpenVQEException, OpenVQETypeError
import openfermion


@dataclass
class ParametersHamiltonian(OpenVQEParameters):
    """
    Enter general parameters which hold for all types of Hamiltonians
    """
    transformation: str = "JW"

    # convenience functions
    def jordan_wigner(self):
        if self.transformation.upper() in ["JW", "J-W", "JORDAN-WIGNER"]:
            return True
        else:
            return False

    # convenience functions
    def bravyi_kitaev(self):
        if self.transformation.upper() in ["BK", "B-K", "BRAVYI-KITAEV"]:
            return True
        else:
            return False


@parametrized(ParametersHamiltonian)
class HamiltonianBase(OpenVQEModule):

    def __call__(self) -> openfermion.QubitOperator:
        """
        Calls the self.get_hamiltonian() function and transforms it to a qubit operator
        The transformation is specified in the parameters
        :return: Gives back the Qubit Operator
        """

        self.verify()

        if self.parameters.jordan_wigner():
            return openfermion.jordan_wigner(openfermion.get_fermion_operator(self.get_fermionic_hamiltonian()))
        elif self.parameters.bravyi_kitaev():
            return openfermion.bravyi_kitaev(openfermion.get_fermion_operator(self.get_fermionic_hamiltonian()))
        else:
            # test if an internal transformation was defined
            transform_method = getattr(self, self.parameters.transformation, None)
            if callable(transform_method): return transform_method(self.get_fermionic_hamiltonian())
            raise OpenVQEParameterError(parameter_name="transformation", parameter_class=type(self.parameters),
                                        parameter_value=self.parameters.transformation,
                                        called_from=type(self).__name__ + ".__call__()")

    def n_qubits(self):
        """
        Needs to be overwritten by specialization
        :return: the number of qubits this hamiltonian needs
        """
        raise OpenVQEException(type(
            self).__name__ + ": forgot to overwrite n_qubits() function or you are calling the BaseClass which you shall not do")

    def get_fermionic_hamiltonian(self):
        """
        Compute the Fermionic Hamiltonian which will be transformed
        by the class' __call__ function
        This function should be overwritten by classes which take this class as base
        :return: the fermionic Hamiltonian
        """
        raise NotImplementedError(
            "You try to call get_hamiltonian from the HamiltonianBase class. This function needs to be overwritten by subclasses")

    def verify(self) -> bool:
        """
        check if the instance is sane, should be overwritten by derived classes
        :return: true if sane, raises exception if not
        """
        return self._verify()