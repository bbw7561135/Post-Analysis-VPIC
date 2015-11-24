"""
Analysis procedures for energy conversion.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
from matplotlib import rc
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import math
import os.path
import struct
import collections
import pic_information
from pic_information import list_pic_info_dir
import simplejson as json
from serialize_json import data_to_json, json_to_data
from runs_name_path import ApJ_long_paper_runs
from scipy.interpolate import interp1d
import palettable
import re

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]

colors = palettable.colorbrewer.qualitative.Set1_9.mpl_colors

font = {'family' : 'serif',
        #'color'  : 'darkred',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 24,
        }

def plot_energy_evolution(pic_info):
    """Plot energy time evolution.

    Plot time evolution of magnetic, electric, electron and ion kinetic
    energies. 

    Args:
        pic_info: the PIC simulation information.
    """
    tenergy = pic_info.tenergy
    ene_electric = pic_info.ene_electric
    ene_magnetic = pic_info.ene_magnetic
    kene_e = pic_info.kene_e
    kene_i = pic_info.kene_i
    ene_bx = pic_info.ene_bx
    ene_by = pic_info.ene_by
    ene_bz = pic_info.ene_bz

    enorm = ene_magnetic[0]

    fig = plt.figure(figsize=[7, 5])
    xs, ys = 0.13, 0.13
    w1, h1 = 0.8, 0.8
    ax = fig.add_axes([xs, ys, w1, h1])
    ax.set_color_cycle(colors)
    p1, = ax.plot(tenergy, ene_magnetic/enorm, linewidth=2, 
            label=r'$\varepsilon_{b}$')
    p2, = ax.plot(tenergy, kene_i/enorm, linewidth=2, label=r'$K_i$')
    p3, = ax.plot(tenergy, kene_e/enorm, linewidth=2, label=r'$K_e$')
    p4, = ax.plot(tenergy, 100*ene_electric/enorm, linewidth=2,
            label=r'$100\varepsilon_{e}$')
    # ax.set_xlim([0, np.max(tenergy)])
    ax.set_xlim([0, np.max(tenergy)])
    ax.set_ylim([0, 1.05])

    ax.set_xlabel(r'$t\Omega_{ci}$', fontdict=font, fontsize=24)
    ax.set_ylabel(r'Energy/$\varepsilon_{b0}$', fontdict=font, fontsize=24)
    leg = ax.legend(loc=1, prop={'size':20}, ncol=2,
            shadow=False, fancybox=False, frameon=False)
    for color,text in zip(colors, leg.get_texts()):
            text.set_color(color)

    # ax.text(0.5, 0.8, r'$\varepsilon_{b}$',
    #         color='blue', fontsize=24,
    #         bbox=dict(facecolor='none', alpha=1.0, edgecolor='none', pad=10.0),
    #         horizontalalignment='center', verticalalignment='center',
    #         transform = ax.transAxes)
    # ax.text(0.7, 0.8, r'$\varepsilon_e$', color='m', fontsize=24,
    #         bbox=dict(facecolor='none', alpha=1.0, edgecolor='none', pad=10.0),
    #         horizontalalignment='center', verticalalignment='center',
    #         transform = ax.transAxes)
    # ax.text(0.5, 0.5, r'$K_e$', color='red', fontsize=24,
    #         bbox=dict(facecolor='none', alpha=1.0, edgecolor='none', pad=10.0),
    #         horizontalalignment='center', verticalalignment='center',
    #         transform = ax.transAxes)
    # ax.text(0.7, 0.5, r'$K_i$', color='green', fontsize=24,
    #         bbox=dict(facecolor='none', alpha=1.0, edgecolor='none', pad=10.0),
    #         horizontalalignment='center', verticalalignment='center',
    #         transform = ax.transAxes)
   
    plt.tick_params(labelsize=20)
    #plt.savefig('pic_ene.eps')

    print('The dissipated magnetic energy: %5.3f' % (1.0 - ene_magnetic[-1]/enorm))
    print('Energy gain to the initial magnetic energy: %5.3f, %5.3f' %
            ((kene_e[-1]-kene_e[0])/enorm, (kene_i[-1]-kene_i[0])/enorm))
    print('Initial kene_e and kene_i to the initial magnetic energy: %5.3f, %5.3f' %
            (kene_e[0]/enorm, kene_i[0]/enorm))
    print('Final kene_e and kene_i to the initial magnetic energy: %5.3f, %5.3f' %
            (kene_e[-1]/enorm, kene_i[-1]/enorm))
    init_ene = pic_info.ene_electric[0] + pic_info.ene_magnetic[0] + \
               kene_e[0] + kene_i[0]
    final_ene = pic_info.ene_electric[-1] + pic_info.ene_magnetic[-1] + \
               kene_e[-1] + kene_i[-1]
    print('Energy conservation: %5.3f' % (final_ene / init_ene))
    # plt.show()


def plot_particle_energy_gain():
    """Plot particle energy gain for cases with different beta.

    """
    # beta_e = 0.005
    pic_info = pic_information.get_pic_info(
            '../../mime25-beta00025-guide0-200-100-nppc200')
    tenergy1 = pic_info.tenergy
    kene_e1 = pic_info.kene_e
    kene_i1 = pic_info.kene_i

    # beta_e = 0.02
    pic_info = pic_information.get_pic_info(
            '../../mime25-beta001-guide0-200-100-nppc400')
    tenergy2 = pic_info.tenergy
    kene_e2 = pic_info.kene_e
    kene_i2 = pic_info.kene_i

    # beta_e = 0.06
    pic_info = pic_information.get_pic_info(
            '../../mime25-beta003-guide0-200-100-nppc200')
    tenergy3 = pic_info.tenergy
    kene_e3 = pic_info.kene_e
    kene_i3 = pic_info.kene_i

    # beta_e = 0.2
    pic_info = pic_information.get_pic_info(
            '../../mime25-beta01-guide0-200-100-nppc200')
    tenergy4 = pic_info.tenergy
    kene_e4 = pic_info.kene_e
    kene_i4 = pic_info.kene_i

    # Estimate the energy gain for beta_e = 0.0072 using beta_e = 0.005
    kene_e12 = kene_e1[0] + (kene_e1-kene_e1[0])*0.005/0.0072
    kene_i12 = kene_i1[0] + (kene_i1-kene_i1[0])*0.005/0.0072

    print 'The ratio of electron energy gain to its initial energy: '
    print '    beta_e = 0.0072, 0.02, 0.06, 0.2: ', \
            (kene_e12[-1]-kene_e12[0])/kene_e12[0], \
            (kene_e2[-1]-kene_e2[0])/kene_e2[0], \
            (kene_e3[-1]-kene_e3[0])/kene_e3[0], \
            (kene_e4[-1]-kene_e4[0])/kene_e4[0]
    # Electrons
    fig = plt.figure(figsize=[3.5,2.5])
    ax = fig.add_axes([0.22, 0.22, 0.75, 0.73])
    ax.plot(tenergy1, (kene_e12-kene_e12[0])/kene_e12[0], 'b', linewidth=2)
    ax.plot(tenergy2, (kene_e2-kene_e2[0])/kene_e2[0], 'r', linewidth=2)
    ax.plot(tenergy3, (kene_e3-kene_e3[0])/kene_e3[0], 'orange', linewidth=2)
    ax.plot(tenergy4, (kene_e4-kene_e4[0])/kene_e4[0], 'g', linewidth=2)
    ax.set_xlim([0, 1190])
    #ax.set_ylim([0, 1.05])

    #plt.title('Energy spectrum', fontdict=font)
    ax.set_xlabel(r'$t\Omega_{ci}$', fontdict=font, fontsize=20)
    ax.set_ylabel(r'$\Delta K_e/K_e(0)$', fontdict=font, fontsize=20)
    plt.tick_params(labelsize=16)
   
    ax.text(680, 8.8, r'$\beta_e=0.007$', color='blue', 
            rotation=5, fontsize=16)
    ax.text(680, 5, r'$\beta_e=0.02$', color='red', 
            rotation=4, fontsize=16)
    ax.text(680, 2.1, r'$\beta_e=0.06$', color='orange', 
            rotation=0, fontsize=16)
    ax.text(680, -1.5, r'$\beta_e=0.2$', color='green', 
            rotation=0, fontsize=16)
    # Ions
    fig = plt.figure(figsize=[3.5,2.5])
    ax = fig.add_axes([0.22, 0.22, 0.75, 0.73])
    ax.plot(tenergy1, (kene_i12-kene_i12[0])/kene_i12[0], 'b', linewidth=2)
    ax.plot(tenergy2, (kene_i2-kene_i2[0])/kene_i2[0], 'r', linewidth=2)
    ax.plot(tenergy3, (kene_i3-kene_i3[0])/kene_i3[0], 'orange', linewidth=2)
    ax.plot(tenergy4, (kene_i4-kene_i4[0])/kene_i4[0], 'g', linewidth=2)
    ax.set_xlim([0, 1190])
    ax.set_ylim([-5, 30])

    #plt.title('Energy spectrum', fontdict=font)
    ax.set_xlabel(r'$t\Omega_{ci}$', fontdict=font, fontsize=20)
    ax.set_ylabel(r'$\Delta K_i/K_i(0)$', fontdict=font, fontsize=20)
    plt.tick_params(labelsize=16)
   
    ax.text(680, 22, r'$\beta_e=0.007$', color='blue', 
            rotation=0, fontsize=16)
    ax.text(680, 9, r'$\beta_e=0.02$', color='red', 
            rotation=0, fontsize=16)
    ax.text(680, 3, r'$\beta_e=0.06$', color='orange', 
            rotation=0, fontsize=16)
    ax.text(680, -4, r'$\beta_e=0.2$', color='green', 
            rotation=0, fontsize=16)
    plt.show()

def read_jdote_data(species, rootpath='../../'):
    """Read j.E data.

    Args:
        species: particle species. 'e' for electron, 'h' for ion.
        rootpath: rootpath of this run
        fpath_jdote: filepath of the jdote file.
    """
    pic_info = pic_information.get_pic_info(rootpath)
    ntf = pic_info.ntf
    dt_fields = pic_info.dt_fields
    dtf_wpe = dt_fields * pic_info.dtwpe / pic_info.dtwci
    fpath_jdote = rootpath + 'pic_analysis/data/'
    fname = fpath_jdote + "jdote00_" + species + ".gda"
    fh = open(fname, 'r')
    data = fh.read()
    fh.close()
    njote = 16  # different kind of data.
    jdote_data = np.zeros((ntf, njote))
    index_start = 0
    index_end = 4
    for current_time in range(ntf):
        for i in range(njote):
            jdote_data[current_time, i], = \
                    struct.unpack('f', data[index_start:index_end])
            index_start = index_end
            index_end += 4
    jcpara_dote = jdote_data[:, 0]
    jcperp_dote = jdote_data[:, 1]
    jmag_dote   = jdote_data[:, 2]
    jgrad_dote  = jdote_data[:, 3]
    jdiagm_dote = jdote_data[:, 4]
    jpolar_dote = jdote_data[:, 5]
    jexb_dote   = jdote_data[:, 6]
    jpara_dote  = jdote_data[:, 7]
    jperp_dote  = jdote_data[:, 8]
    jperp1_dote = jdote_data[:, 9]
    jperp2_dote = jdote_data[:, 10]
    jqnupara_dote = jdote_data[:, 11]
    jqnuperp_dote = jdote_data[:, 12]
    jagy_dote     = jdote_data[:, 14]
    jtot_dote     = jdote_data[:, 13]
    jdivu_dote     = jdote_data[:, 15]
    jcpara_dote_int = cumulate_with_time(jcpara_dote, dtf_wpe, ntf)
    jcperp_dote_int = cumulate_with_time(jcperp_dote, dtf_wpe, ntf)
    jmag_dote_int   = cumulate_with_time(jmag_dote, dtf_wpe, ntf)
    jgrad_dote_int  = cumulate_with_time(jgrad_dote, dtf_wpe, ntf)
    jdiagm_dote_int = cumulate_with_time(jdiagm_dote, dtf_wpe, ntf)
    jpolar_dote_int = cumulate_with_time(jpolar_dote, dtf_wpe, ntf)
    jexb_dote_int   = cumulate_with_time(jexb_dote, dtf_wpe, ntf)
    jpara_dote_int  = cumulate_with_time(jpara_dote, dtf_wpe, ntf)
    jperp_dote_int  = cumulate_with_time(jperp_dote, dtf_wpe, ntf)
    jperp1_dote_int = cumulate_with_time(jperp1_dote, dtf_wpe, ntf)
    jperp2_dote_int = cumulate_with_time(jperp2_dote, dtf_wpe, ntf)
    jqnupara_dote_int = cumulate_with_time(jqnupara_dote, dtf_wpe, ntf)
    jqnuperp_dote_int = cumulate_with_time(jqnuperp_dote, dtf_wpe, ntf)
    jagy_dote_int     = cumulate_with_time(jagy_dote, dtf_wpe, ntf)
    jtot_dote_int     = cumulate_with_time(jtot_dote, dtf_wpe, ntf)
    jdivu_dote_int     = cumulate_with_time(jdivu_dote, dtf_wpe, ntf)
    jdote_collection = collections.namedtuple('jdote_collection',
            ['jcpara_dote', 'jcperp_dote', 'jmag_dote', 'jgrad_dote',
                'jdiagm_dote', 'jpolar_dote', 'jexb_dote', 'jpara_dote',
                'jperp_dote', 'jperp1_dote', 'jperp2_dote', 'jqnupara_dote',
                'jqnuperp_dote', 'jagy_dote', 'jtot_dote', 'jdivu_dote',
                'jcpara_dote_int', 'jcperp_dote_int', 'jmag_dote_int',
                'jgrad_dote_int', 'jdiagm_dote_int', 'jpolar_dote_int',
                'jexb_dote_int', 'jpara_dote_int', 'jperp_dote_int',
                'jperp1_dote_int', 'jperp2_dote_int', 'jqnupara_dote_int',
                'jqnuperp_dote_int', 'jagy_dote_int', 'jtot_dote_int',
                'jdivu_dote_int'])
    jdote = jdote_collection(jcpara_dote, jcperp_dote, jmag_dote, jgrad_dote,
            jdiagm_dote, jpolar_dote, jexb_dote, jpara_dote, jperp_dote,
            jperp1_dote, jperp2_dote, jqnupara_dote, jqnuperp_dote,
            jagy_dote, jtot_dote, jdivu_dote,
            jcpara_dote_int, jcperp_dote_int, jmag_dote_int, jgrad_dote_int,
            jdiagm_dote_int, jpolar_dote_int, jexb_dote_int, jpara_dote_int, 
            jperp_dote_int, jperp1_dote_int, jperp2_dote_int, 
            jqnupara_dote_int, jqnuperp_dote_int, jagy_dote_int,
            jtot_dote_int, jdivu_dote_int)
    return jdote


def cumulate_with_time(f, dt, ntf):
    """
    Args:
        f: the time evolution of one field.
        dt: the time step.
        ntf: number of time frames for fields.
    """
    f_cumulative = np.zeros(ntf) # originally 0
    for i in range(1,ntf):
        f_cumulative[i] = f_cumulative[i-1] + 0.5*(f[i]+f[i-1])*dt
    return f_cumulative


def plot_jdotes_evolution(pic_info, jdote, species):
    """
    Plot the time evolution of the energy conversion due to different currents.

    Args:
        pic_info: PIC simulation information.
        jdote: the jdote data.
        species: particle species. 'e' for electron, 'h' for ion.
    """
    jdote_tot_drifts = jdote.jcpara_dote + jdote.jgrad_dote \
            + jdote.jmag_dote \
            + jdote.jagy_dote
            # + jdote.jpolar_dote \
            # + jdote.jqnupara_dote \
            # + jdote.jdivu_dote \

    jdote_tot_drifts_int = jdote.jcpara_dote_int + jdote.jgrad_dote_int \
            + jdote.jmag_dote_int \
            + jdote.jagy_dote_int
            # + jdote.jpolar_dote_int \
            # + jdote.jqnupara_dote_int \
            # + jdote.jdivu_dote_int \

    if species == 'e':
        dkene = pic_info.dkene_e
        kene = pic_info.kene_e
        kename = '$\Delta K_e$'
    else:
        dkene = pic_info.dkene_i
        kene = pic_info.kene_i
        kename = '$\Delta K_i$'

    tfields = pic_info.tfields
    tenergy = pic_info.tenergy
    fig = plt.figure(figsize=[7, 4])
   
    width = 0.82
    height = 0.4
    xs = 0.14
    ys = 0.15
    ax1 = fig.add_axes([xs, ys+height, width, height])
    ax1.plot(tfields, jdote.jcpara_dote, lw=2, color='b')
    ax1.plot(tfields, jdote.jgrad_dote, lw=2, color='g')
    ax1.plot(tfields, jdote.jmag_dote, lw=2, color='r')
    ax1.plot(tfields, jdote_tot_drifts, lw=2, color='m')
    ax1.plot(tenergy, dkene, lw=2, color='k', label=kename)
    ax1.plot([np.min(tenergy), np.max(tenergy)], [0,0], 'k--')
    ax1.set_ylabel(r'$d\varepsilon_c/dt$', fontdict=font, fontsize=20)
    ax1.tick_params(reset=True, labelsize=16)
    ax1.tick_params(axis='x', labelbottom='off')
    ax1.set_xlim([np.min(tfields), np.max(tfields)])

    enorm = pic_info.ene_magnetic[0]
    ax2 = fig.add_axes([xs, ys, width, height])
    ax2.plot(tfields, jdote.jcpara_dote_int/enorm, lw=2, color='b')
    ax2.plot(tfields, jdote.jgrad_dote_int/enorm, lw=2, color='g')
    ax2.plot(tfields, jdote.jmag_dote_int/enorm, lw=2, color='r')
    ax2.plot(tfields, jdote_tot_drifts_int/enorm, lw=2, color='m')
    ax2.plot(tenergy, (kene-kene[0])/enorm, color='k', lw=2)
    ax2.plot([np.min(tenergy), np.max(tenergy)], [0,0], 'k--')

    ax2.set_xlabel(r'$t\Omega_{ci}$', fontdict=font, fontsize=20)
    ax2.set_ylabel(r'$\varepsilon_c$', fontdict=font, fontsize=20)
    ax2.tick_params(labelsize=16)
    ax2.set_xlim(ax1.get_xlim())

    ax1.text(0.05, 0.85, r'$\mathbf{j}_g\cdot\mathbf{E}$', color='g', fontsize=20,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.2, 0.85, r'$\mathbf{j}_m\cdot\mathbf{E}$', color='r', fontsize=20,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.05, 0.65, r'$\mathbf{j}_c\cdot\mathbf{E}$', color='b', fontsize=20,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    fname = r'$dK_' + species + '/dt$'
    ax1.text(0.05, 0.15, fname, color='k', fontsize=20,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.2, 0.15, r"$\mathbf{j}_\perp\cdot\mathbf{E}$", color='m',
            fontsize=20, horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)

    td = -1
    print 'The fraction of perpendicular heating (model): ', \
            jdote_tot_drifts_int[td]/(kene[td]-kene[0])
    print 'The fraction of perpendicular heating (simulation): ', \
            jdote.jqnuperp_dote_int[-1]/(kene[-1]-kene[0])

    # fname = '../img/jdrifts_dote_' + species + '.eps'
    # fig.savefig(fname)
    # plt.show()


def plot_jpara_perp_dote(jdote_e, jdote_i, pic_info):
    """Plot the parallel and perpendicular heating using the simulation data.

    Args:
        jdote_e: jdote data for electrons.
        jdote_i: jdote data for ions.
        pic_info: PIC simulation information.
    """
    tfields = pic_info.tfields
    tenergy = pic_info.tenergy
    jtot_dote = jdote_e.jqnupara_dote + jdote_e.jqnuperp_dote
    jtot_dote_int = jdote_e.jqnupara_dote_int + jdote_e.jqnuperp_dote_int
    dkene = pic_info.dkene_e
    kene = pic_info.kene_e
    kename = '$\Delta K_e$'

    #fig, axes = plt.subplots(2, sharex=True, sharey=False)
    fig = plt.figure(figsize=[7, 5])
   
    width = 0.78
    height = 0.39
    xs = 0.17
    ys = 0.96 - height
    gap = 0.05
    #mpl.rc('text', usetex=False)
    ax1 = fig.add_axes([xs, ys, width, height])
    ax1.plot(tfields, jdote_e.jqnupara_dote, lw=2, color='b', 
            label=r'$\boldsymbol{j}_{e\parallel}\cdot\boldsymbol{E}$')
    ax1.plot(tfields, jdote_e.jqnuperp_dote, lw=2, color='g',
            label=r'$\boldsymbol{j}_{e\perp}\cdot\boldsymbol{E}$')
    ax1.plot(tfields, jtot_dote, lw=2, color='r',
            label=r'$\boldsymbol{j}\cdot\boldsymbol{E}$')
    ax1.plot(tenergy, dkene, lw=2, color='k', label=kename)
    ax1.plot([np.min(tenergy), np.max(tenergy)], [0,0], 'k--')
    ax1.set_ylabel(r'$d\varepsilon_c/dt$', fontdict=font, fontsize=24)
    ax1.tick_params(reset=True, labelsize=20)
    ax1.tick_params(axis='x', labelbottom='off')
    # ax1.set_xlim([np.min(tenergy), np.max(tenergy)])
    ax1.set_xlim([0, 800])
    dmax = np.max([jdote_e.jqnuperp_dote, jdote_e.jqnupara_dote, jtot_dote])
    dmin = np.min([jdote_e.jqnuperp_dote[2:], jdote_e.jqnupara_dote[2:], jtot_dote[2:]])
    ax1.set_ylim([dmin*1.1, dmax*1.1])
    # ax1.yaxis.set_ticks(np.arange(-1, 6, 1))
    # ax1.text(0.9, 0.85, r'$(e)$', color='black', fontsize=24,
    #         bbox=dict(facecolor='none', alpha=1.0, edgecolor='none', pad=10.0),
    #         horizontalalignment='left', verticalalignment='center',
    #         transform = ax1.transAxes)
    ax1.text(0.8, 0.85, r'$dK_e/dt$', color='black', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.45, 0.85, r'$\boldsymbol{j}_{\parallel}\cdot\boldsymbol{E}$',
            color='blue', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.62, 0.85, r'$\boldsymbol{j}_{\perp}\cdot\boldsymbol{E}$',
            color='green', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.5, 0.7, r'$(\boldsymbol{j}_{\parallel}+\boldsymbol{j}_\perp)\cdot\boldsymbol{E}$',
            color='red', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)

    jpara_dote_int = jdote_e.jqnupara_dote_int
    jperp_dote_int = jdote_e.jqnuperp_dote_int
    jtot_dote_int = jpara_dote_int + jperp_dote_int
    print("The ratio of parallel and perpendicular acceleration for electrons: %5.3f" %
            (jpara_dote_int[-1] / jtot_dote_int[-1]))

    jtot_dote = jdote_i.jqnupara_dote + jdote_i.jqnuperp_dote
    jtot_dote_int = jdote_i.jqnupara_dote_int + jdote_i.jqnuperp_dote_int
    dkene = pic_info.dkene_i
    kene = pic_info.kene_i
    kename = '$\Delta K_i$'

    ys -= height + gap
    ax2 = fig.add_axes([xs, ys, width, height])
    ax2.plot(tfields, jdote_i.jqnupara_dote, lw=2, color='b', 
            label=r'$\mathbf{j}_{e\parallel}\cdot\mathbf{E}$')
    ax2.plot(tfields, jdote_i.jqnuperp_dote, lw=2, color='g',
            label=r'$\mathbf{j}_{e\perp}\cdot\mathbf{E}$')
    ax2.plot(tfields, jtot_dote, lw=2, color='r',
            label=r'$\mathbf{j}\cdot\mathbf{E}$')
    ax2.plot(tenergy, dkene, lw=2, color='k', label=kename)
    ax2.plot([np.min(tenergy), np.max(tenergy)], [0,0], 'k--')
    ax2.set_xlabel(r'$t\Omega_{ci}$', fontdict=font, fontsize=24)
    ax2.set_ylabel(r'$d\varepsilon_c/dt$', fontdict=font, fontsize=24)
    ax2.tick_params(reset=True, labelsize=20)
    ax2.set_xlim(ax1.get_xlim())
    dmax = np.max([jdote_i.jqnuperp_dote, jdote_i.jqnupara_dote, jtot_dote])
    dmin = np.min([jdote_i.jqnuperp_dote[2:], jdote_i.jqnupara_dote[2:], jtot_dote[2:]])
    ax2.set_ylim([dmin*1.1, dmax*1.1])
    # ax2.yaxis.set_ticks(np.arange(-2, 11, 2))
    # ax2.text(0.02, 0.85, r'$(i)$', color='black', fontsize=24,
    #         bbox=dict(facecolor='none', alpha=1.0, edgecolor='none', pad=10.0),
    #         horizontalalignment='left', verticalalignment='center',
    #         transform = ax2.transAxes)
    ax2.text(0.8, 0.85, r'$dK_i/dt$', color='black', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax2.transAxes)

    jpara_dote_int = jdote_i.jqnupara_dote_int
    jperp_dote_int = jdote_i.jqnuperp_dote_int
    jtot_dote_int = jpara_dote_int + jperp_dote_int
    print("The ratio of parallel and perpendicular acceleration for ions: %5.3f" %
            (jpara_dote_int[-1] / jtot_dote_int[-1]))

    # if not os.path.isdir('../img/'):
    #     os.makedirs('../img/')
    # fig.savefig('../img/jpp_dote.eps')
    # plt.show()


def plot_jtot_dote():
    """
    Plot the total energy conversion jtot_dote for both electrons and ions.

    """
    pic_info = pic_information.get_pic_info('../../')
    tfields = pic_info.tfields
    tenergy = pic_info.tenergy

    jdote = read_jdote_data('e')
    jtot_dote = jdote.jqnupara_dote + jdote.jqnuperp_dote
    jtot_dote_int = jdote.jqnupara_dote_int + jdote.jqnuperp_dote_int
    # jdote = read_jdote_data('i')
    # jtot_dote += jdote.jqnupara_dote + jdote.jqnuperp_dote
    # jtot_dote_int += jdote.jqnupara_dote_int + jdote.jqnuperp_dote_int

    dkene_e = pic_info.dkene_e
    kene_e = pic_info.kene_e
    dkene_i = pic_info.dkene_i
    kene_i = pic_info.kene_i
    dkene = dkene_e + dkene_i
    kene = kene_e + kene_i
    kename = '$\Delta K_e$'

    #fig, axes = plt.subplots(2, sharex=True, sharey=False)
    fig = plt.figure(figsize=[7, 3])
   
    width = 0.76
    height = 0.7
    xs = 0.18
    ys = 0.95-height
    #mpl.rc('text', usetex=False)
    ax1 = fig.add_axes([xs, ys, width, height])
    ax1.plot(tfields, jdote.jqnupara_dote_int, lw=2, color='b', 
            label=r'$\mathbf{j}_{e\parallel}\cdot\mathbf{E}$')
    ax1.plot(tfields, jdote.jqnuperp_dote_int, lw=2, color='g',
            label=r'$\mathbf{j}_{e\perp}\cdot\mathbf{E}$')
    ax1.plot(tfields, jtot_dote_int, lw=2, color='r',
            label=r'$\mathbf{j}\cdot\mathbf{E}$')
    ax1.plot(tenergy, kene_e-kene_e[0], lw=2, color='k', label=kename)
    ax1.plot([np.min(tenergy), np.max(tenergy)], [0,0], 'k--')
    ax1.set_xlabel(r'$t\Omega_{ci}$', fontdict=font, fontsize=24)
    ax1.set_ylabel(r'$d\varepsilon_c$', fontdict=font, fontsize=24)
    ax1.tick_params(reset=True, labelsize=20)
    # ax1.tick_params(axis='x', labelbottom='off')
    # ax1.set_ylim([-20, 20])
    # ax1.yaxis.set_ticks(np.arange(-1, 6, 1))
    # ax1.set_xlim([0, 800])
    ax1.text(0.5, 0.8, r'$\mathbf{j}_{\parallel}\cdot\mathbf{E}$',
            color='blue', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.7, 0.8, r'$\mathbf{j}_{\perp}\cdot\mathbf{E}$',
            color='green', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.5, 0.6, r'$(\mathbf{j}_{\parallel}+\mathbf{j}_\perp)\cdot\mathbf{E}$',
            color='red', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)
    ax1.text(0.6, 0.4, r'$dK_e/dt$', color='black', fontsize=24,
            horizontalalignment='left', verticalalignment='center',
            transform = ax1.transAxes)

    if not os.path.isdir('../img/'):
        os.makedirs('../img/')
    fig.savefig('../img/jtot_dote.eps')

    plt.show()


def read_data_from_json(fname):
    """Read jdote data from a json file

    Args:
        fname: file name of the json file of the jdote data.
    """
    with open(fname, 'r') as json_file:
        data = json_to_data(json.load(json_file))
    print("Reading %s" % fname)
    return data


def calc_energy_gain_single(fname):
    """Calculate the particle energy gain for a single run.

    Args:
        fname: file name of the json file of PIC information.
    """
    pic_info = read_data_from_json(fname)
    kene_e = pic_info.kene_e
    kene_i = pic_info.kene_i
    dke_e = (kene_e[-1] - kene_e[0]) / kene_e[0]
    dke_i = (kene_i[-1] - kene_i[0]) / kene_i[0]
    print('Electron energy gain percentage: %4.2f' % dke_e)
    print('Ion energy gain percentage: %4.2f' % dke_i)


def calc_energy_gain_multi():
    """Calculate the particle energy gain for different runs.
    """
    dir = '../data/pic_info/'
    fnames = list_pic_info_dir(dir)
    for fname in fnames:
        fname = dir + fname
        calc_energy_gain_single(fname)


def plot_energy_evolution_multi():
    """Plot energy evolution for multiple runs.
    """
    dir = '../data/pic_info/'
    if not os.path.isdir('../img/'):
        os.makedirs('../img/')
    odir = '../img/ene_evolution/'
    if not os.path.isdir(odir):
        os.makedirs(odir)
    fnames = list_pic_info_dir(dir)
    for fname in fnames:
        rname = fname.replace(".json", ".eps")
        oname = rname.replace("pic_info", "enes")
        oname = odir + oname
        fname = dir + fname
        pic_info = read_data_from_json(fname)
        plot_energy_evolution(pic_info)
        plt.savefig(oname)
        plt.close()


def save_jdote_json(species):
    """Save jdote data for different runs as json

    Args:
        species: particle species
    """
    if not os.path.isdir('../data/'):
        os.makedirs('../data/')
    dir = '../data/jdote_data/'
    if not os.path.isdir(dir):
        os.makedirs(dir)

    base_dirs, run_names = ApJ_long_paper_runs()
    for base_dir, run_name in zip(base_dirs, run_names):
        jdote = read_jdote_data(species, base_dir)
        jdote_json = data_to_json(jdote)
        fname = dir + 'jdote_' + run_name + '_' + species + '.json'
        with open(fname, 'w') as f:
            json.dump(jdote_json, f)


def plot_jpara_jperp_dote_multi():
    """Plot energy evolution from the parallel and perpendicular directions.
    """
    dir = '../data/jdote_data/'
    if not os.path.isdir('../img/'):
        os.makedirs('../img/')
    odir = '../img/jdote/'
    if not os.path.isdir(odir):
        os.makedirs(odir)
    base_dirs, run_names = ApJ_long_paper_runs()
    for run_name in run_names:
        picinfo_fname = '../data/pic_info/pic_info_' + run_name + '.json'
        jdote_e_fname = '../data/jdote_data/jdote_' + run_name + '_e.json'
        jdote_i_fname = '../data/jdote_data/jdote_' + run_name + '_i.json'
        pic_info = read_data_from_json(picinfo_fname)
        jdote_e = read_data_from_json(jdote_e_fname)
        jdote_i = read_data_from_json(jdote_i_fname)
        plot_jpara_perp_dote(jdote_e, jdote_i, pic_info)
        oname = odir + 'jpp_' + run_name + '.eps'
        plt.savefig(oname)
        plt.close()


def plot_jdotes_evolution_multi(species):
    """Plot jdote evolution for multiple runs.

    Args:
        species: particle species.
    """
    dir = '../data/jdote_data/'
    if not os.path.isdir('../img/'):
        os.makedirs('../img/')
    odir = '../img/jdote/'
    if not os.path.isdir(odir):
        os.makedirs(odir)
    base_dirs, run_names = ApJ_long_paper_runs()
    for run_name in run_names:
        picinfo_fname = '../data/pic_info/pic_info_' + run_name + '.json'
        jdote_fname = '../data/jdote_data/jdote_' + \
                run_name + '_' + species + '.json'
        pic_info = read_data_from_json(picinfo_fname)
        jdote = read_data_from_json(jdote_fname)
        plot_jdotes_evolution(pic_info, jdote, species)
        suffix = 'wjagy'
        oname = odir + 'jdrifts_dote_' + run_name + '_' + suffix + '.eps'
        plt.savefig(oname)
        plt.close()


def calc_jdotes_fraction_multi(species):
    """Calculate the fractions for jdotes due to different drift.

    Args:
        species: particle species.
    """
    dir = '../data/jdote_data/'
    if not os.path.isdir(dir):
        os.makedirs(dir)
    fname = dir + 'jdotes_fraction_' + species + '.dat'
    f = open(fname, 'w')
    base_dirs, run_names = ApJ_long_paper_runs()
    nruns = len(run_names)
    jdote_drifts_fraction = []
    for irun in range(nruns):
        run_name = run_names[irun]
        picinfo_fname = '../data/pic_info/pic_info_' + run_name + '.json'
        jdote_fname = dir + 'jdote_' + run_name + '_' + species + '.json'
        pic_info = read_data_from_json(picinfo_fname)
        tenergy = pic_info.tenergy
        tfields = pic_info.tfields
        tmax = min(tenergy[-1], tfields[-1])
        jdote_data = read_data_from_json(jdote_fname)
        kene = pic_info.kene_e if species == 'e' else pic_info.kene_i
        nf = len(jdote_data)
        jdote_names = jdote_data._fields
        f1 = interp1d(tenergy, kene-kene[0], 'cubic')
        jdote_drifts_int = []
        names = []
        for name in jdote_names:
            if 'int' in name:
                names.append(name)
                jdote_int = getattr(jdote_data, name)
                f2 = interp1d(tfields, jdote_int, 'cubic')
                jdote_last = f2(tmax)
                jdote_drifts_int.append(jdote_last)
        jdote_drifts_np = np.asarray(jdote_drifts_int/f1(tmax))
        nj = len(jdote_drifts_np)
        if irun == 0:
            f.write("%25s" % ' ')
            for i in range(nj):
                name = names[i]
                name_head = name[:-9]
                length = len(name_head)
                # name_head.ljust(10)
                f.write("%10s" % name_head)
            f.write("\n")
        f.write("%25s" % run_name)
        for i in range(nj):
            f.write("%10.4f" % jdote_drifts_np[i])
        f.write("\n")
        jdote_drifts_fraction.append(jdote_drifts_np)
    f.close()
    return jdote_drifts_fraction


if __name__ == "__main__":
    species = 'e'
    # pic_info = pic_information.get_pic_info('../../')
    # jdote = read_jdote_data(species)
    # jdote_e = read_jdote_data('e')
    # jdote_i = read_jdote_data('i')
    # plot_energy_evolution(pic_info)
    # plot_particle_energy_gain()
    # plot_jdotes_evolution(pic_info, jdote, species)
    # plot_jpara_perp_dote(jdote_e, jdote_i, pic_info)
    # plot_jtot_dote()
    # calc_energy_gain_multi()
    # plot_energy_evolution_multi()
    # save_jdote_json('e')
    plot_jpara_jperp_dote_multi()
    # plot_jdotes_evolution_multi(species)
    # calc_jdotes_fraction_multi(species)
