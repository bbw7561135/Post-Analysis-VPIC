"""
Analysis procedures for particle number and energy.
"""
import collections
import math
import os.path
import struct

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc
from matplotlib.colors import LogNorm
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import Axes3D

import pic_information
import spectrum_fitting
from energy_conversion import read_data_from_json

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]

font = {
    'family': 'serif',
    #'color'  : 'darkred',
    'color': 'black',
    'weight': 'normal',
    'size': 24,
}

# spectrum_dir = '../'
spectrum_dir = '../data/spectra/'
# run_name = 'mime25_beta0007'
run_name = 'mime25_beta002_guide4'
fpath = spectrum_dir + run_name + '/'


def get_distributions(species, current_time, pic_info, spectrum_type):
    """Get the whole, thermal and nonthermal distributions.

    Args:
        species: particle species. 'e' for electron, 'h' for ion.
        current_time: current time frame.
        pic_info: namedtuple for the PIC simulation information.
        spectrum_type: the type name of the spectrum data.
    Returns:
        dist_info: the distributions and the energy bins.
    """
    nx = pic_info.nx
    ny = pic_info.ny
    nz = pic_info.nz
    nppc = pic_info.nppc
    fnorm = nx * ny * nz * nppc
    fname = fpath + spectrum_type + "-" + species +  "." + \
            str(current_time).zfill(len(str(current_time)))
    if (os.path.isfile(fname)):
        ene_lin, flin, ene_log, flog = \
                spectrum_fitting.get_energy_distribution(fname, fnorm)
    else:
        fname = fpath + spectrum_type + "-" + species +  \
                "." + str(current_time-1).zfill(len(str(current_time)))
        ene_lin, flin1, ene_log, flog1 = \
                spectrum_fitting.get_energy_distribution(fname, fnorm)
        fname = fpath + spectrum_type + "-" + species +  \
                "." + str(current_time+1).zfill(len(str(current_time)))
        ene_lin, flin2, ene_log, flog2 = \
                spectrum_fitting.get_energy_distribution(fname, fnorm)
        flin = (flin1 + flin2) / 2
        flog = (flog1 + flog2) / 2
    fthermal_log = spectrum_fitting.fit_thermal_core(ene_log, flog)
    fnonthermal_log = flog - fthermal_log
    distribution_info = collections.namedtuple('distribution_info', [
        'ene_lin', 'flin', 'ene_log', 'flog', 'fthermal_log', 'fnonthermal_log'
    ])
    dist_info = distribution_info(
        ene_lin=ene_lin,
        flin=flin,
        ene_log=ene_log,
        flog=flog,
        fthermal_log=fthermal_log,
        fnonthermal_log=fnonthermal_log)
    return dist_info


def get_particle_number_energy(ene_bins, fnorm, f, fthermal, fnonthermal):
    """Get the total, thermal nonthermal particle number and energy.

    Args:
        ene_bins: energy bins.
        fnorm: the normalization for the particle distribution.
        f: the whole distribution.
        fthermal: thermal part of the distribution.
        fnonthermal: nonthermal part of the distribution.
    """
    nacc_ene, eacc_ene = \
            spectrum_fitting.accumulated_particle_info(ene_bins, f)
    ntot = nacc_ene[-1] * fnorm
    etot = eacc_ene[-1] * fnorm
    nacc_ene, eacc_ene = \
            spectrum_fitting.accumulated_particle_info(ene_bins, fnonthermal)
    nnonthermal = nacc_ene[-1] * fnorm
    enonthermal = eacc_ene[-1] * fnorm
    nacc_ene, eacc_ene = \
            spectrum_fitting.accumulated_particle_info(ene_bins, fthermal)
    nthermal = nacc_ene[-1] * fnorm
    ethermal = eacc_ene[-1] * fnorm
    number_energy = collections.namedtuple('number_energy', [
        'ntot', 'etot', 'nthermal', 'ethermal', 'nnonthermal', 'enonthermal'
    ])
    ptl_n_ene = number_energy(
        ntot=ntot,
        etot=etot,
        nthermal=nthermal,
        ethermal=ethermal,
        nnonthermal=nnonthermal,
        enonthermal=enonthermal)
    return ptl_n_ene


def plot_nonthermal_populations(species, pic_info, spectrum_type):
    """Plot nonthermal particle population.

    Plot the number and energy for nonthermal particle population.

    Args:
        species: particle species. 'e' for electron, 'h' for ion.
        pic_info: namedtuple for the PIC simulation information.
        spectrum_type: the type name of the spectrum data.
    """
    ntp = pic_info.ntp
    nx = pic_info.nx
    ny = pic_info.ny
    nz = pic_info.nz
    nppc = pic_info.nppc
    fnorm = nx * ny * nz * nppc
    n_nonthermal_fraction = np.zeros(ntp)
    e_nonthermal_fraction = np.zeros(ntp)
    for ct in range(1, ntp + 1):
        dist_info = get_distributions(species, ct, pic_info, spectrum_type)
        ptl_n_ene = get_particle_number_energy(
            dist_info.ene_log, fnorm, dist_info.flog, dist_info.fthermal_log,
            dist_info.fnonthermal_log)
        n_nonthermal_fraction[ct - 1] = ptl_n_ene.nnonthermal / ptl_n_ene.ntot
        e_nonthermal_fraction[ct - 1] = ptl_n_ene.enonthermal / ptl_n_ene.etot
    # differentiate the fractions.
    n_nonthermal_fraction_diff = np.gradient(n_nonthermal_fraction)
    e_nonthermal_fraction_diff = np.gradient(e_nonthermal_fraction)
    tparticles = pic_info.tparticles

    # save the fractions data.
    f = open('nonthermal_fractions.dat', 'w')
    for i in range(ntp):
        f.write(str(tparticles[i]) + ' ')
        f.write(str(n_nonthermal_fraction[i]) + ' ')
        f.write(str(e_nonthermal_fraction[i]))
        f.write('\n')
    f.close()

    fig, ax = plt.subplots(figsize=[7, 5])
    n_nonthermal_fraction[0] = 0
    e_nonthermal_fraction[0] = 0
    tmin = np.min(tparticles)
    tmax = np.max(tparticles)
    p1, = ax.plot(
        tparticles,
        n_nonthermal_fraction,
        linewidth=2,
        color='b',
        label=r'$n_{nth} / n_{tot}$')
    p2, = ax.plot(
        tparticles,
        e_nonthermal_fraction,
        linewidth=2,
        color='g',
        label=r'$E_{nth} / E_{tot}$')
    ax.set_xlim([tmin, tmax])
    ax.set_ylim([-0.05, 1.05])
    ax.tick_params(labelsize=20)
    ax.set_xlabel(r'$t\Omega_{ci}$', fontdict=font)
    ax.set_ylabel(r'Non-thermal Fraction', fontdict=font)
    ax.legend(loc=4, prop={'size': 24}, ncol=1, shadow=True, fancybox=True)
    fig.tight_layout()

    fig, ax = plt.subplots(figsize=[7, 5])
    p1 = ax.plot(
        tparticles,
        n_nonthermal_fraction_diff,
        linewidth=2,
        color='b',
        label='Non-thermal particle number $n$')
    p2 = ax.plot(
        tparticles,
        e_nonthermal_fraction_diff,
        linewidth=2,
        color='g',
        label='Non-thermal particle energy $E$')
    ax.set_xlim([tmin, tmax])
    ax.tick_params(labelsize=20)
    ax.set_xlabel(r'$t\omega_{ci}$', fontdict=font)
    ax.set_ylabel(r'$dP_\text{nonthermal}/dt$', fontdict=font)
    p3 = ax.plot([tmin, tmax], [0, 0], 'k--')
    fig.subplots_adjust(hspace=0)
    fig.tight_layout()
    plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
    #fname = 'n_ene_portion_' + species + '.eps'
    #plt.savefig(fname)
    plt.show()


def cumulative_distributions(species, pic_info, spectrum_type, ct):
    """Accumulate particle number along energy and plot it.

    Args:
        species: particle species. 'e' for electron, 'h' for ion.
        pic_info: namedtuple for the PIC simulation information.
        spectrum_type: the type name of the spectrum data.
        ct: current time frame.
    """
    nx = pic_info.nx
    ny = pic_info.ny
    nz = pic_info.nz
    nppc = pic_info.nppc
    fnorm = nx * ny * nz * nppc
    dist_info = get_distributions(species, ct, pic_info, spectrum_type)
    ptl_n_ene = get_particle_number_energy(
        dist_info.ene_log, fnorm, dist_info.flog, dist_info.fthermal_log,
        dist_info.fnonthermal_log)
    nacc_ene, eacc_ene = spectrum_fitting.accumulated_particle_info(
        dist_info.ene_log, dist_info.flog)
    ene_log_norm = spectrum_fitting.get_normalized_energy(
        species, dist_info.ene_log, pic_info)
    fig = plt.figure(figsize=[7, 5])
    xs, ys = 0.15, 0.15
    w1, h1 = 0.8, 0.8
    ax = fig.add_axes([xs, ys, w1, h1])
    p1, = ax.semilogx(
        ene_log_norm,
        nacc_ene / nacc_ene[-1],
        linewidth=2,
        color='b',
        label='Particle number $n$')
    p2, = ax.semilogx(
        ene_log_norm,
        eacc_ene / eacc_ene[-1],
        linewidth=2,
        color='g',
        label=r'Particle energy $\varepsilon$')
    xmin = np.min(ene_log_norm)
    xmax = np.max(ene_log_norm)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([-0.05, 1.05])

    #plt.title('Energy spectrum', fontdict=font)
    plt.xlabel(r'$\varepsilon/\varepsilon_\text{th}$', fontdict=font)
    plt.ylabel(r'Cumulative $n$ and $\varepsilon$', fontdict=font)

    leg = ax.legend(
        loc=2,
        prop={'size': 20},
        ncol=1,
        shadow=False,
        fancybox=False,
        frameon=False)
    ax.tick_params(labelsize=20)
    ax.grid(True)
    #plt.savefig('n_ene_acc.eps')
    plt.show()


def plot_numerber_enerergy_each_bin(species, pic_info, spectrum_type, ct):
    """Plot particle number and energy in each energy bins.

    Args:
        species: particle species. 'e' for electron, 'h' for ion.
        pic_info: namedtuple for the PIC simulation information.
        spectrum_type: the type name of the spectrum data.
        ct: current time frame.
    """
    dist_info = get_distributions(species, ct, pic_info, spectrum_type)
    nacc_ene, eacc_ene = spectrum_fitting.accumulated_particle_info(
        dist_info.ene_log, dist_info.flog)
    ndiff_ene = np.gradient(nacc_ene)
    ediff_ene = np.gradient(eacc_ene)
    ndiff_max = np.max(ndiff_ene)
    ediff_max = np.max(ediff_ene)
    ene_log_norm = spectrum_fitting.get_normalized_energy(
        species, dist_info.ene_log, pic_info)
    fig = plt.figure(figsize=[7, 5])
    xs, ys = 0.15, 0.15
    w1, h1 = 0.8, 0.8
    ax = fig.add_axes([xs, ys, w1, h1])
    p1, = ax.loglog(
        ene_log_norm,
        ndiff_ene / ndiff_max,
        linewidth=2,
        color='b',
        label='Number $n$')
    p2, = ax.loglog(
        ene_log_norm,
        ediff_ene / ediff_max,
        linewidth=2,
        color='g',
        label=r'Energy $\varepsilon$')
    ax.set_ylim([1.0E-7, 2])
    if (species == 'e'):
        ax.set_xlim([np.min(ene_log_norm), 6E2])
    else:
        ax.set_xlim([np.min(ene_log_norm), 2E3])

    #plt.title('Energy spectrum', fontdict=font)
    ax.set_xlabel(r'$\varepsilon/\varepsilon_{th}$', fontdict=font)
    ax.set_ylabel(r'$n$ and $\varepsilon$ in each bins', fontdict=font)

    leg = ax.legend(
        loc=4,
        prop={'size': 20},
        ncol=1,
        shadow=False,
        fancybox=False,
        frameon=False)
    ax.tick_params(labelsize=20)
    # ax.tight_layout()
    ax.grid(True)
    #fname = 'n_ene_diff' + str(it) + '_' + species + '.eps'
    #plt.savefig(fname)

    plt.show()


if __name__ == "__main__":
    # pic_info = pic_information.get_pic_info('..')
    picinfo_fname = '../data/pic_info/pic_info_' + run_name + '.json'
    pic_info = read_data_from_json(picinfo_fname)
    ntp = pic_info.ntp
    vthe = pic_info.ntp
    # plot_nonthermal_populations('e', pic_info, 'spectrum')
    cumulative_distributions('e', pic_info, 'spectrum', ntp)
    # plot_numerber_enerergy_each_bin('e', pic_info, 'spectrum', ntp)
