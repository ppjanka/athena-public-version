"""
unstratified-primary-cylindrical.py

A regression test for globAccDisk-src-primary_grav.hpp (source terms for gravity with a source at the coordinate center).

Current test:
 -- stratified gravity
 -- cylindrical coordinate version
 -- a Keplerian disk inclined wrt the coordinate system is initialized, the test ensures that it remains stationary

"""

# Modules
import numpy as np                             # standard Python module for numerics
import sys                                     # standard Python module to change path
import scripts.utils.athena as athena          # utilities for running Athena++
import scripts.utils.comparison as comparison  # more utilities explicitly for testing
sys.path.insert(0, '../../vis/python')         # insert path to Python read scripts
import athena_read                             # utilities for reading Athena++ data # noqa
import socket                                  # recognizing host machine


def prepare(**kwargs):

    # check which machine we're running on and configure accordingly
    if socket.gethostname() == 'ast1506-astro':
        athena.configure('hdf5', 'mpi',
                     prob='globAccDisk-test-binary_gravity',
                     flux='roe',
                     eos='adiabatic',
                     coord='cylindrical',
                     hdf5_path='/usr/local/Cellar/hdf5/1.10.4',
                     **kwargs)
    else:
        athena.configure('hdf5', 'mpi',
                     prob='globAccDisk-test-binary_gravity',
                     flux='roe',
                     eos='adiabatic',
                     coord='cylindrical',
                     **kwargs)


    athena.make()


def run(**kwargs):

    arguments = ['job/problem_id=stratified-primary-cylindrical',
                 'output1/file_type=hdf5',
                 'output1/variable=prim',
                 'output1/dt=%.20f' % (2.5),
                 'time/cfl_number=0.3',
                 'time/tlim=%.20f' % (2.5),
                 'mesh/nx1=32',
                 'mesh/x1min=0.5',
                 'mesh/x1max=1.0',
                 'mesh/ix1_bc=reflecting',
                 'mesh/ox1_bc=reflecting',
                 'mesh/nx2=64',
                 'mesh/x2min=0.0',
                 'mesh/x2max=%.20f' % (2.*np.pi),
                 'mesh/ix2_bc=periodic',
                 'mesh/ox2_bc=periodic',
                 'mesh/nx3=16',
                 'mesh/x3min=-0.5',
                 'mesh/x3max=0.5',
                 'mesh/ix3_bc=reflecting',
                 'mesh/ox3_bc=reflecting',
                 'meshblock/nx1=16',
                 'meshblock/nx2=16',
                 'meshblock/nx3=16',
                 'hydro/gamma=1.1',
                 'hydro/dfloor=0.0001',
                 'hydro/pfloor=0.0001',
                 'problem/stratified=1',
                 'problem/binary_component=0',
                 'problem/GM1=1.0',
                 'problem/rho=1.0',
                 'problem/rho0=0.01',
                 'problem/press=0.01',
                 'problem/inclination=0.3',
                 'problem/position_angle=1.0',
                 'problem/ang_dist_max=0.2']

    athena.run('hydro/athinput.binary_gravity', arguments)

def analyze():

    initial_state = athena_read.athdf('bin/stratified-primary-cylindrical.out1.00000.athdf')
    r0, phi0, z0, rho = [initial_state[key] for key in ['x1v', 'x2v', 'x3v', 'rho']]
    z, phi, r = np.meshgrid(z0, phi0, r0, indexing='ij')

    #calculate the center of mass of each vertical stencil to be compared with the final state
    com_expected = np.sum(rho*z, axis=0) / np.sum(rho, axis=0)

    # check if the frames are identical
    for i in range(1,2):
        test_results = athena_read.athdf('bin/stratified-primary-cylindrical.out1.0000%i.athdf' % i)
        rho = test_results['rho']
        com = np.sum(rho*z, axis=0) / np.sum(rho, axis=0)

        error_rel_com = np.sum(np.abs(com_expected - com)) / (np.product(com.shape) * 1.0)
        print("[stratified-primary-cylindrical]: error_rel_com = %.2e" % error_rel_com)

        if True: # useful if the test fails
          import matplotlib.pyplot as plt
          plt.clf()
          plt.subplot(1,2,1)
          plt.contourf(r0, phi0, com_expected)
          plt.subplot(1,2,2)
          plt.contourf(r0, phi0, com)
          plt.show()

        if np.isnan(error_rel_com):
            return False
        if error_rel_com > 0.05:
            return False

    return True
