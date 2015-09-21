"""
Test if the 'q' key is unique.
"""
import os
import h5py
import math
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Cursor, Button, Slider
from mpl_toolkits.axes_grid1 import make_axes_locatable
import collections
import timeit
import struct
import collections
import pic_information
from contour_plots import read_2d_fields, plot_2d_contour

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]

font = {'family' : 'serif',
        #'color'  : 'darkred',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 24,
        }

particles = collections.namedtuple("particles", 
        ["x", "y", "z", "ux", "uy", "uz"])

class Viewer2d(object):
    def __init__(self, file, nptl, x, y, fdata, init_ft, var_field, var_name):
        """
        Shows a given array in a 2d-viewer.
        Input: z, an 2d array.
        x,y coordinters are optional.
        """
        self.x = x
        self.y = y
        self.fdata = fdata
        self.file = file
        self.nptl = nptl
        self.ct = init_ft
        self.iptl = 0
        self.particle_tags = []
        for item in self.file:
            self.particle_tags.append(item)
        group = file[self.particle_tags[self.iptl]]
        dset_ux = group['Ux']
        self.sz, = dset_ux.shape
        self.particle_info = ParticleInfo(self.sz)
        self.ptl = self.particle_info.get_particle_info(group)
        self.pic_info = pic_information.get_pic_info('../../')
        self.smime = math.sqrt(self.pic_info.mime)
        self.px = self.ptl.x / self.smime
        self.py = self.ptl.y / self.smime
        self.pz = self.ptl.z / self.smime
        self.gama = np.sqrt(self.ptl.ux**2 + self.ptl.uy**2 + self.ptl.uz**2 + 1.0)

        self.fig = plt.figure(figsize=(10, 10))

        self.pxz_axis = self.fig.add_axes([0.1, 0.73, 0.8, 0.25])
        vmax = min(abs(np.min(self.fdata)), abs(np.max(self.fdata)))
        vmax *= 0.2
        self.im1 = self.pxz_axis.imshow(self.fdata, cmap=plt.cm.seismic,
                extent=[np.min(self.x), np.max(self.x), np.min(self.y), np.max(self.y)],
                aspect='auto', origin='lower',
                vmin = -vmax, vmax = vmax,
                interpolation='bicubic')
        divider = make_axes_locatable(self.pxz_axis)
        self.cax = divider.append_axes("right", size="2%", pad=0.05)
        self.cbar = self.fig.colorbar(self.im1, cax=self.cax)
        self.cbar.ax.tick_params(labelsize=16)
        self.cbar.ax.set_ylabel(var_name, fontdict=font, fontsize=24)
        self.pxz_axis.tick_params(labelsize=16)
        self.pxz_axis.set_xlabel(r'$x/d_i$', fontdict=font, fontsize=20)
        self.pxz_axis.set_ylabel(r'$z/d_i$', fontdict=font, fontsize=20)
        self.pxz_axis.autoscale(1,'both',1)

        # xz plot
        self.pxz, = self.pxz_axis.plot(self.px, self.pz, linewidth=2,
                color='k', marker='.', markersize=1, linestyle='')

        # Energy plot
        self.ene_axis = self.fig.add_axes([0.1, 0.46, 0.35, 0.2])
        self.pene, = self.ene_axis.plot(self.gama - 1.0, linewidth=2, color='k')
        self.ene_axis.set_ylabel(r'$\gamma - 1$', fontdict=font, fontsize=20)
        self.ene_axis.set_xlabel(r'Time', fontdict=font, fontsize=20)
        self.ene_axis.tick_params(labelsize=16)

        # x-energy
        self.xe_axis = self.fig.add_axes([0.6, 0.46, 0.35, 0.2])
        self.xe_axis.tick_params(labelsize=16)
        self.pxe, = self.xe_axis.plot(self.px, self.gama - 1.0,
                linewidth=2, color='r')
        self.xe_axis.set_ylabel(r'$\gamma - 1$', fontdict=font, fontsize=20)
        self.xe_axis.set_xlabel(r'$x$', fontdict=font, fontsize=20)

        # y-energy
        self.ye_axis = self.fig.add_axes([0.1, 0.2, 0.35, 0.2])
        self.ye_axis.tick_params(labelsize=16)
        self.pye, = self.ye_axis.plot(self.py, self.gama - 1.0,
                linewidth=2, color='g')
        self.ye_axis.set_ylabel(r'$\gamma - 1$', fontdict=font, fontsize=20)
        self.ye_axis.set_xlabel(r'$y$', fontdict=font, fontsize=20)

        # z-energy
        self.ze_axis = self.fig.add_axes([0.6, 0.2, 0.35, 0.2])
        self.ze_axis.tick_params(labelsize=16)
        self.pze, = self.ze_axis.plot(self.pz, self.gama - 1.0,
                linewidth=2, color='b')
        self.ze_axis.set_ylabel(r'$\gamma - 1$', fontdict=font, fontsize=20)
        self.ze_axis.set_xlabel(r'$z$', fontdict=font, fontsize=20)

        # Slider to choose particle
        self.sliderax = plt.axes([0.1, 0.1, 0.8, 0.03])
        particle_list = np.arange(1, self.nptl)
        self.slider = DiscreteSlider(self.sliderax, 'Particle', 1, self.nptl,\
                allowed_vals=particle_list, valinit=particle_list[self.iptl])
        self.slider.on_changed(self.update_particle)

        # Slider to choose time frames for fields
        self.field_sliderax = plt.axes([0.1, 0.05, 0.8, 0.03])
        tframes = np.arange(1, self.pic_info.ntf)
        self.field_slider = DiscreteSlider(self.field_sliderax, 'Field', 1,
                self.pic_info.ntf, allowed_vals=tframes, valinit=tframes[self.ct-1])
        self.field_slider.on_changed(self.update_field)

        self._widgets=[self.slider, self.field_slider]
        self.save_figure()

    def update_particle(self, val):
        self.iptl = self.slider.val - 1
        group = file[self.particle_tags[self.iptl]]
        self.ptl = self.particle_info.get_particle_info(group)
        self.px = self.ptl.x / self.smime
        self.py = self.ptl.y / self.smime
        self.pz = self.ptl.z / self.smime
        self.gama = np.sqrt(self.ptl.ux**2 + self.ptl.uy**2 + self.ptl.uz**2 + 1.0)
        emax = np.max(self.gama - 1.0)
        xmin = np.min(self.px)
        xmax = np.max(self.px)
        ymin = np.min(self.py)
        ymax = np.max(self.py)
        zmin = np.min(self.pz)
        zmax = np.max(self.pz)
        self.ene_axis.set_ylim([0, emax*1.1])
        self.xe_axis.set_ylim([0, emax*1.1])
        self.ye_axis.set_ylim([0, emax*1.1])
        self.ze_axis.set_ylim([0, emax*1.1])
        self.xe_axis.set_xlim([xmin*0.9, xmax*1.1])
        if ymin < 0:
            yl = ymin * 1.1
        else:
            yl = ymin * 0.9

        if ymax < 0:
            yr = ymax * 0.9
        else:
            yr = ymax * 1.1

        if zmin < 0:
            zl = zmin * 1.1
        else:
            zl = zmin * 0.9

        if zmax < 0:
            zr = zmax * 0.9
        else:
            zr = zmax * 1.1
        self.ye_axis.set_xlim([yl, yr])
        self.ze_axis.set_xlim([zl, zr])
        self.pxz.set_xdata(self.px)
        self.pxz.set_ydata(self.pz)
        self.pene.set_ydata(self.gama - 1.0)
        self.pxe.set_xdata(self.px)
        self.pye.set_xdata(self.py)
        self.pze.set_xdata(self.pz)
        self.pxe.set_ydata(self.gama - 1.0)
        self.pye.set_ydata(self.gama - 1.0)
        self.pze.set_ydata(self.gama - 1.0)
        self.fig.canvas.draw_idle()
        self.save_figure()

    def update_field(self, val):
        self.ct = self.field_slider.val
        kwargs = {"current_time":self.ct, "xl":0, "xr":400, "zb":-100, "zt":100}
        fname = '../../data/' + var_field + '.gda'
        x, z, self.fdata = read_2d_fields(self.pic_info, fname, **kwargs) 
        self.im1.set_data(self.fdata)
        self.fig.canvas.draw_idle()

    def save_figure(self):
        if not os.path.isdir('../img/'):
            os.makedirs('../img/')
        if not os.path.isdir('../img/img_traj/'):
            os.makedirs('../img/img_traj/')
        fname = '../img/img_traj/traj_' + str(self.iptl) + '_' + \
                str(self.ct).zfill(3) + '.jpg'
        self.fig.savefig(fname, dpi=200)


class DiscreteSlider(Slider):
    """A matplotlib slider widget with discrete steps."""
    def __init__(self, *args, **kwargs):
        """
        Identical to Slider.__init__, except for the new keyword 'allowed_vals'.
        This keyword specifies the allowed positions of the slider
        """
        self.allowed_vals = kwargs.pop('allowed_vals',None)
        self.previous_val = kwargs['valinit']
        Slider.__init__(self, *args, **kwargs)
        if self.allowed_vals is None:
            self.allowed_vals = [self.valmin,self.valmax]

    def set_val(self, val):
        discrete_val = self.allowed_vals[abs(val-self.allowed_vals).argmin()]
        xy = self.poly.xy
        xy[2] = discrete_val, 1
        xy[3] = discrete_val, 0
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % discrete_val)
        if self.drawon: 
            self.ax.figure.canvas.draw()
        self.val = discrete_val
        if self.previous_val!=discrete_val:
            self.previous_val = discrete_val
            if not self.eventson: 
                return
            for cid, func in self.observers.iteritems():
                func(discrete_val)


class ParticleInfo(object):
    def __init__(self, sz):
        """
        Initialize information for one particle.
        """
        self.ux = np.zeros(sz)
        self.uy = np.zeros(sz)
        self.uz = np.zeros(sz)
        self.x = np.zeros(sz)
        self.y = np.zeros(sz)
        self.z = np.zeros(sz)

    def get_particle_info(self, group):
        """
        Read the information.
        """
        dset_ux = group['Ux']
        dset_uy = group['Uy']
        dset_uz = group['Uz']
        dset_x = group['dX']
        dset_y = group['dY']
        dset_z = group['dZ']
        dset_ux.read_direct(self.ux)
        dset_uy.read_direct(self.uy)
        dset_uz.read_direct(self.uz)
        dset_x.read_direct(self.x)
        dset_y.read_direct(self.y)
        dset_z.read_direct(self.z)
        ptl = particles(x=self.x, y=self.y, z=self.z,
                ux=self.ux, uy=self.uy, uz=self.uz)
        return ptl
  
if __name__ == "__main__":
    pic_info = pic_information.get_pic_info('../../')
    filepath = '/net/scratch1/guofan/share/ultra-sigma/'
    filepath += 'sigma1e4-mime100-4000-track/pic_analysis/vpic-sorter/data/'
    fname = filepath + 'electrons.h5p'
    file = h5py.File(fname, 'r')
    ngroups = len(file)
    init_ft = 40
    var_field = 'jy'
    var_name = '$j_y$'
    kwargs = {"current_time":init_ft, "xl":0, "xr":400, "zb":-100, "zt":100}
    fname = '../../data/' + var_field + '.gda'
    x, z, data = read_2d_fields(pic_info, fname, **kwargs) 
    fig_v = Viewer2d(file, ngroups, x, z, data, init_ft, var_field, var_name)
    plt.show()
    file.close()