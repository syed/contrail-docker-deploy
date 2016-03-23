
import logging
import cgitb
import cStringIO

from vnc_api.vnc_api import *

class MigrateServices(object):

    def __init__(self, args=None):
        self.vnc_lib = VncApi('admin', 'contrail123', 'admin', '127.0.0.1', 8082)

    def migrate_all_vm(self):
        vm_list = self.vnc_lib.virtual_machines_list()
        for vm in vm_list['virtual-machines']:
            vm_obj = self.vnc_lib.virtual_machine_read(fq_name=vm['fq_name'])
            if vm_obj.display_name:
                logging.info('\tVM display name exists to %s' % vm_obj.display_name)
                continue
            vm_obj.set_display_name(vm_obj.fq_name[-1])
            try:
                self.vnc_lib.virtual_machine_update(vm_obj)
                logging.info('\tVM display name updated to %s' % vm_obj.display_name)
            except Exception:
                logging.error('\tVM display name update failed for %s' % vm_obj.display_name)
                cgitb_error_log()

def cgitb_error_log():
    string_buf = cStringIO.StringIO()
    cgitb.Hook(file=string_buf, format="text").handle(sys.exc_info())
    logging.info(string_buf.getvalue())

def main():
    logging.basicConfig(filename='display_name.log', level=logging.INFO)
    cgitb.enable(format='text')
    logging.info('Starting upgrade of vm display name')
    try:
        migrate = MigrateServices()
        migrate.migrate_all_vm()
    except Exception:
        cgitb_error_log()

if __name__ == '__main__':
    main()
