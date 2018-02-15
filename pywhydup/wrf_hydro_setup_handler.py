
class WrfHydroSetup(object):
    def __init__(self, path):
        pass

    def slurm_submit(self):
        pass

    def overwrite_rainfall_forcing_data(self, rainrate_dataset):
        # Get all forcing files
        print 'Trying to exchange forcing data for RAINFALL...'
        fn_list = glob(
            path.join(forcing_dir_root_new, 'zeelim_forcing_wrf', '*LDASIN*'))
        fn_list.sort()

        # Exchange rain rate with current interpolated CML-rainfall
        for fn_full_path in fn_list:
            fn_local = path.split(fn_full_path)[1]

            date = get_date_from_LDAS_filename(fn_local)
            t_str = datetime.strftime(date, '%Y-%m-%d %H:%M')

            t_str_cml_list = cmls.set_info['interpol'].keys()

            if t_str in t_str_cml_list:
                try:
                    # Open forcing file and replace rain rate field
                    #   !!! Beware, rainrate must be in mm/s !!!
                    with netCDF4.Dataset(fn_full_path, mode='r+') as ds:
                        R_field_mm_h = cmls.set_info['interpol'][t_str]
                        R_field_mm_s = R_field_mm_h / 60.0 / 60.0
                        ds.variables['RAINRATE'][0, :, :] = R_field_mm_s
                    print 'netCDF file RAINRATE updated'
                except:
                    print 'Could not write to netCDF file'
            else:
                print 't_str %s not in cml date range' % t_str


class SetupDirHandler(object):
    def __init__(self, root_dir, template_dir):
        pass

    def duplicate_template(self, new_dir=None, t_start=None, t_stop=None):
        # Make a copy of the WRF-Hydro template folder
        dir_name = 'zeelim.cml_v%03d' % v_number
        forcing_dir_root_new = path.join(forcing_dir_root, dir_name)
        try:
            shutil.copytree(forcing_dir_root_template, forcing_dir_root_new)
            print 'Copied everything to %s' % forcing_dir_root_new
        except OSError, e:
            print e
            print 'Skipping copying of template dir.'

    return WrfHydroSetup(path=new_dir)


wrf_forcing_dir = '/pd/home/chwala-c/wrf-hydro/test_cml_processing_zeelim/zeelim_template/zeelim_forcing_wrf/'

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


def sbatch_via_ssh(dir_name):
    import commands

    command_str = 'ssh chwala-c@keal "cd %s; sbatch run_slurm.sh"' % dir_name
    commands.getstatusoutput(command_str)