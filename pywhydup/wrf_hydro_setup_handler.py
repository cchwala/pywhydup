import commands
from glob import glob
from os import path, listdir, makedirs
import netCDF4
from datetime import datetime
import shutil
import re
import xarray as xr


class WrfHydroSetupBase(object):
    def __init__(self,
                 absolute_path,
                 forcing_dir='forcing'):
        self.absolute_path = absolute_path
        self.root_dir = path.normpath(path.join(absolute_path, '..'))
        self.forcing_dir = forcing_dir

        self.t_start, self.t_stop = self._get_forcing_files_t_start_and_stop()
        self.lon_grid, self.lat_grid = self._get_forcing_file_lon_lat_grid()

    def _get_forcing_files_t_start_and_stop(self):
        forcing_file_list = self.get_forcing_file_list()
        t_start = get_date_from_LDAS_filename(forcing_file_list[0])
        t_stop = get_date_from_LDAS_filename(forcing_file_list[-1])
        return t_start, t_stop

    def _get_forcing_file_lon_lat_grid(self):
        fn_list = self.get_forcing_file_list()
        ds = xr.open_dataset(fn_list[0])
        lon_grid = ds.XLONG_M.isel(Time=0)
        lat_grid = ds.XLAT_M.isel(Time=0)
        return lon_grid.values, lat_grid.values

    def get_forcing_file_list(self,
                              t_start=None,
                              t_stop=None,
                              t_format='%Y-%m-%d'):
        if t_start:
            t_start = datetime.strptime(t_start, t_format)
        if t_stop:
            t_stop = datetime.strptime(t_stop, t_format)

        fn_absolute_list = glob(
            path.join(self.absolute_path,
                      self.forcing_dir,
                      '*LDASIN*'))
        fn_absolute_list.sort()

        if len(fn_absolute_list) == 0:
            raise ValueError('No forcing files found')

        if (t_start is None) and (t_stop is None):
            return fn_absolute_list
        else:
            date_list = [get_date_from_LDAS_filename(fn)
                         for fn in fn_absolute_list]

            fn_absolute_list_new = []
            fn_t_smaller = []
            fn_t_larger = []
            for date, fn in zip(date_list, fn_absolute_list):
                if t_start and t_stop:
                    if (date >= t_start) and (date <= t_stop):
                        fn_absolute_list_new.append(fn)
                        if date <= t_start:
                            fn_t_smaller.append(fn)
                        if date >= t_stop:
                            fn_t_larger.append(fn)
                elif t_start:
                    if date >= t_start:
                        fn_absolute_list_new.append(fn)
                    if date <= t_start:
                        fn_t_smaller.append(fn)
                elif t_stop:
                    if date <= t_stop:
                        fn_absolute_list_new.append(fn)
                    if date >= t_stop:
                        fn_t_larger.append(fn)

            if t_start and (len(fn_t_smaller) == 0):
                print('WARNING: No files with time stamp smaller or equal '
                      'to `t_start` found.')
            if t_stop and (len(fn_t_larger) == 0):
                print('WARNING: No files with time stamp larger or equal '
                      'to `t_stop` found.')

            if len(fn_absolute_list_new) == 0:
                raise ValueError('No forcing files for specified period found')

            return fn_absolute_list_new


class WrfHydroSetupTemplate(WrfHydroSetupBase):
    def duplicate(self,
                  new_dir=None,
                  t_start=None,
                  t_stop=None,
                  t_format='%Y-%m-%d'):
        """ Duplicate template dir and limit forcing data time period

        The current WRF-Hydro template directory is duplicated, copying all
        files in its base directory and the `lib` directory. The forcing data
        in the forcing directory is only copied for the selected time period if
        `t_start` and/or `t_stop` are supplied. In this case, also the starting
        time of the simulation will automatically be update in the file
        `namelist.hrldas`.

        Parameters
        ----------
        new_dir : str, optional
            Name of the directory of the duplicated setup. This directory is
            placed in the `root_dir`.
        t_start : str, optional
        t_stop
        t_format

        Returns
        -------

        """
        # Make a copy of the WRF-Hydro template folder
        if new_dir is None:
            default_setup_dir_name_base = 'setup'
            setup_dir_name = default_setup_dir_name_base + '_{:03d}'.format(1)

            i = 1
            while path.exists(path.join(self.root_dir, setup_dir_name)):
                i += 1
                setup_dir_name = (default_setup_dir_name_base
                                  + '_{:03d}'.format(i))
                if i > 999:
                    raise ValueError('There seem to already be more then 999 '
                                     'setups. Hence I cannot create a new one '
                                     'because numbering is limited to go from '
                                     '1 to 999.')

            new_dir = setup_dir_name

        if path.exists(path.join(self.root_dir, new_dir)):
            raise ValueError('`new_dir` already exists at {}'
                             .format(path.join(self.root_dir, new_dir)))
        else:
            makedirs(path.join(self.root_dir, new_dir))

        try:
            print('Copying template base dir content...')
            fn_list_base_dir = glob(path.join(self.absolute_path, '*'))
            for fn in fn_list_base_dir:
                if not path.isdir(fn):
                    shutil.copy(fn,
                                path.join(self.root_dir,
                                          new_dir,
                                          path.split(fn)[-1]))
            print('Copying template lib dir content...')
            shutil.copytree(path.join(self.absolute_path, 'lib'),
                            path.join(self.root_dir, new_dir, 'lib'))
            print('Copying template forcing dir content...')
            fn_forcing_list = self.get_forcing_file_list(
                t_start=t_start,
                t_stop=t_stop,
                t_format=t_format)

            if not path.exists(path.join(self.root_dir,
                                         new_dir,
                                         self.forcing_dir)):
                makedirs(path.join(self.root_dir,
                                   new_dir,
                                   self.forcing_dir))

            for fn in fn_forcing_list:
                shutil.copy(fn,
                            path.join(self.root_dir,
                                      new_dir,
                                      self.forcing_dir,
                                      path.split(fn)[-1]))

            print('Copied everything to {}'.format(path.join(self.root_dir,
                                                             new_dir)))
        except OSError, e:
            print e
            print 'Skipping copying of template dir.'

        new_setup = WrfHydroSetup(absolute_path=path.join(self.root_dir,
                                                          new_dir))

        if t_start:
            new_setup.set_new_starting_date_in_namelist_file(t_start=t_start)
            print('Updated start date in `namelist.hrldas')

        return new_setup


class WrfHydroSetup(WrfHydroSetupBase):
    def slurm_submit(self,
                     server='keal',
                     remote_user=None,
                     remote=True):
        if remote:
            if remote_user:
                command_str = 'ssh {}@{} "cd {}; sbatch run_slurm.sh"'.format(
                    remote_user, server, self.absolute_path)
            else:
                command_str = 'ssh {} "cd {}; sbatch run_slurm.sh"'.format(
                    server, self.absolute_path)
        else:
            command_str = '"cd {}; sbatch run_slurm.sh"'.format(
                remote_user, server, self.absolute_path)
        return commands.getstatusoutput(command_str)

    def overwrite_rainfall_forcing_data(self, rainrate_dataarray):
        # Get all forcing files
        print 'Trying to exchange forcing data for RAINFALL...'
        fn_list = self.get_forcing_file_list()
        fn_list.sort()

        # Exchange rain rate with current interpolated CML-rainfall
        for fn_full_path in fn_list:
            fn_local = path.split(fn_full_path)[1]

            date = get_date_from_LDAS_filename(fn_local)

            try:
                # Open forcing file and replace rain rate field
                #   !!! Beware, rainrate must be in mm/s !!!
                with netCDF4.Dataset(fn_full_path, mode='r+') as ds:
                    R_field_mm_h = rainrate_dataarray.sel(time=date)
                    R_field_mm_s = R_field_mm_h / 60.0 / 60.0
                    ds.variables['RAINRATE'][0, :, :] = R_field_mm_s
                print 'netCDF file RAINRATE updated'
            except:
                print 'Could not write to netCDF file'

    def set_new_starting_date_in_namelist_file(self,
                                               t_start,
                                               t_format='%Y-%m-%d'):
        fn = path.join(self.absolute_path, 'namelist.hrldas')

        t_start = datetime.strptime(t_start, t_format)

        with open(fn, "rt") as f_in:
            file_content = f_in.read()

        file_content = re.sub(r'START_YEAR  = \b[0-9]{4}\b',
                              datetime.strftime(t_start, 'START_YEAR  = %Y'),
                              file_content)
        file_content = re.sub(r'START_MONTH  = \b[0-9]{2}\b',
                              datetime.strftime(t_start, 'START_MONTH  = %m'),
                              file_content)
        file_content = re.sub(r'START_DAY  = \b[0-9]{2}\b',
                              datetime.strftime(t_start, 'START_DAY  = %d'),
                              file_content)

        with open(fn, "wt") as f_out:
            f_out.write(file_content)


class SetupDirHandler(object):
    def __init__(self, root_dir, template_dir, template_forcing_dir='forcing'):
        """ A class to create multiple duplicates of a WRF-Hydro setup

        Parameters
        ----------
        root_dir : str
            The root directory in which the template directory is located and
            in which all duplicated setup directories will be located
        template_dir : str
            Name of the template directory in the `root_dir`
        template_forcing_dir : str
            Name if the directory of the forcing data in the `template_dir`
        """

        self.root_dir = root_dir
        self.template_dir = template_dir
        self.template_setup = WrfHydroSetupTemplate(
            absolute_path=path.join(root_dir, template_dir),
            forcing_dir=template_forcing_dir)


def build_LDAS_filename(date, in_out='IN', domain_N=3):
    date_str = date
    fn = date_str + '.LDAS' + in_out + '_DOMAIN' + str(domain_N)
    return fn


def build_LDAS_full_path(date, in_out='IN', domain_N=3):
    fn = build_LDAS_filename(date, in_out, domain_N)
    return path.join(wrf_forcing_dir, fn)


def get_date_from_LDAS_filename(fn):
    # Get only filename without path
    fn_local = path.split(fn)[1]
    date_str = fn_local.split('.')[0]
    return datetime.strptime(date_str, '%Y%m%d%H')
