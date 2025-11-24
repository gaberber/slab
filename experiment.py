__author__ = 'David Schuster'

import os.path
import json
import yaml
import numpy as np
import traceback

from slab import SlabFile, InstrumentManager, get_next_filename, AttrDict, LocalInstruments

class NpEncoder(json.JSONEncoder):
    """ Ensure json dump can handle np arrays """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class Experiment:
    """Base class for all experiments"""

    def __init__(self, path='', prefix='data', config_file=None, liveplot_enabled=False, **kwargs):
        """ Initializes experiment class
            @param path - directory where data will be stored
            @param prefix - prefix to use when creating data files
            @param config_file - parameters for config file specified are loaded into the class dict
                                 (name relative to expt_directory if no leading /)
                                 Default = None looks for path/prefix.json

            @param **kwargs - by default kwargs are updated to class dict

            also loads InstrumentManager, LivePlotter, and other helpers
        """

        self.__dict__.update(kwargs)
        self.path = path
        self.prefix = prefix
        self.cfg = None
        if config_file is not None:
            self.config_file = os.path.join(path, config_file)
        else:
            self.config_file = None

        if not hasattr(self, 'ns_port'):
            self.ns_port=None
        if not hasattr(self, 'ns_address'):
            self.ns_address=None
        self.im = InstrumentManager(ns_address=self.ns_address, ns_port=self.ns_port)
        # if liveplot_enabled:
        #     self.plotter = LivePlotClient()
        # self.dataserver= dataserver_client()
        self.fname = os.path.join(path, get_next_filename(path, prefix, suffix='.h5'))

        self.load_config()

    def load_config(self):
        if self.config_file is None:
            self.config_file = os.path.join(self.path, self.prefix + ".json")
        try:
            if self.config_file[-3:] == '.h5':
                with SlabFile(self.config_file) as f:
                    self.cfg = AttrDict(f.load_config())
                    self.fname = self.config_file
            elif self.config_file[-4:].lower() =='.yml':
                with open(self.config_file,'r') as fid:
                    self.cfg = AttrDict(yaml.safe_load(fid))
            else:
                with open(self.config_file, 'r') as fid:
                    cfg_str = fid.read()
                    self.cfg = AttrDict(json.loads(cfg_str))

            if self.cfg is not None:
                for alias, inst in self.cfg['aliases'].items():
                    if inst in self.im:
                        setattr(self, alias, self.im[inst])
        except Exception as e:
            print("Could not load config.")
            traceback.print_exc()

    def save_config(self):
        if self.config_file[:-3] != '.h5':
            with open(self.config_file, 'w') as fid:
                json.dump(self.cfg, fid, cls=NpEncoder), 
            self.datafile().attrs['config'] = json.dumps(self.cfg, cls=NpEncoder)

    def datafile(self, group=None, remote=False, data_file = None, swmr=False, read_mode=False):
        """returns a SlabFile instance
           proxy functionality not implemented yet"""
        if data_file ==None:
            data_file = self.fname
        if read_mode:
            f = SlabFile(data_file, 'r')
        else:
            # NOTE: this doesn't seem to be what swmr mode means in h5py?
            if swmr==True:
                f = SlabFile(data_file, 'w', libver='latest')
            elif swmr==False:
                f = SlabFile(data_file, 'a')
            else:
                raise Exception('ERROR: swmr must be type boolean')

        if group is not None:
            f = f.require_group(group)
        if 'config' not in f.attrs:
            try:
                f.attrs['config'] = json.dumps(self.cfg, cls=NpEncoder)
            except TypeError as err:
                print(('Error in saving cfg into datafile (experiment.py):', err))

        return f

    def go(self, save=False, analyze=False, display=False, progress=False):
        # get data

        data=self.acquire(progress)
        if analyze:
            data=self.analyze(data)
        if save:
            self.save_data(data)
        if display:
            self.display(data)

    def acquire(self, progress=False, debug=False):
        pass

    def analyze(self, data=None, **kwargs):
        pass

    def display(self, data=None, **kwargs):
        pass

    def save_data(self, data=None):  #do I want to try to make this a very general function to save a dictionary containing arrays and variables?
        if data is None:
            data=self.data

        with self.datafile() as f:
            for k, d in data.items():
                f.add(k, np.array(d))

    def load_data(self, f=None):
        if f is None:
            f=self.datafile()
        data={}
        for k in f.keys():
            data[k] = np.array(f[k])
        data["attrs"] = f.get_dict()
        self.data = data
        return data

    @classmethod
    def from_h5file(cls, fname):
        """
        Alternative constructor method building returning a object 
        that only has data and config read from the hdf5 file.
        Mostly used for loading measured data and running the
        analysis/display methods of its corresponding experiment.
        Note that this bypasses the normal Experiment.__init__
        """
        assert os.path.exists(fname), f"Path {fname} does not exist"
        self = cls.__new__(cls)
        self.fname = fname

        with SlabFile(fname, 'r') as f:
            self.load_data(f)
            self.cfg = AttrDict(yaml.safe_load(self.data['attrs']['config']))

        return self

