
import logging
import cgitb
import cStringIO

from vnc_api.vnc_api import *

class MigrateServices(object):

    def __init__(self, args=None):
        self.vnc_lib = VncApi('admin', 'contrail123', 'admin', '127.0.0.1', 8082)

    def _get_instance_name(self, si_obj, index):
        instance_name = "__".join(si_obj.fq_name) + '__' + index
        return instance_name

    def _get_vmi_index(self, si_obj, st_obj, old_vmi_obj):
        st_props = st_obj.get_service_template_properties()
        st_if_list = st_props.get_interface_type()
        si_props = si_obj.get_service_instance_properties()
        si_if_list = si_props.get_interface_list()
        for vmi_index in range(0, len(st_if_list)):
            old_if_type = old_vmi_obj.get_virtual_machine_interface_properties().get_service_interface_type()
            if old_if_type == st_if_list[vmi_index].service_interface_type:
                return str(vmi_index + 1)

    def _mac_alloc(self, uuid):
        return '02:%s:%s:%s:%s:%s' % (uuid[0:2], uuid[2:4],
            uuid[4:6], uuid[6:8], uuid[9:11])

    def migrate_iip_and_fip(self, si_obj, iip_list, new_vmi_obj, old_vmi_obj):
        for iip in iip_list or []:
            self.vnc_lib.ref_update('instance-ip', iip['uuid'],
                'virtual-machine-interface', old_vmi_obj.uuid, None, 'DELETE')
            logging.info('\t\tIIP %s reference to old VMI %s (%s) dropped' % (iip['uuid'], old_vmi_obj.name, old_vmi_obj.uuid))
            self.vnc_lib.ref_update('instance-ip', iip['uuid'],
                'virtual-machine-interface', new_vmi_obj.uuid, None, 'ADD')
            logging.info('\t\tIIP %s reference to new VMI %s (%s) added' % (iip['uuid'], new_vmi_obj.name, new_vmi_obj.uuid))

        for fip in old_vmi_obj.get_floating_ip_back_refs() or []:
            self.vnc_lib.ref_update('floating-ip', fip['uuid'],
                'virtual-machine-interface', old_vmi_obj.uuid, None, 'DELETE')
            logging.info('\t\tFIP %s reference to old VMI %s (%s) dropped' % (fip['uuid'], old_vmi_obj.name, old_vmi_obj.uuid))
            self.vnc_lib.ref_update('floating-ip', fip['uuid'],
                'virtual-machine-interface', new_vmi_obj.uuid, None, 'ADD')
            logging.info('\t\tFIP %s reference to new VMI %s (%s) added' % (fip['uuid'], new_vmi_obj.name, new_vmi_obj.uuid))

    def migrate_vmi(self, si_obj, st_obj, proj_obj, old_vmi_obj, vm_obj):
        vmi_index = self._get_vmi_index(si_obj, st_obj, old_vmi_obj)
        old_if_type = old_vmi_obj.get_virtual_machine_interface_properties().get_service_interface_type()
        old_local_pref = old_vmi_obj.get_virtual_machine_interface_properties().get_local_preference()
        old_user_visible = old_vmi_obj.get_id_perms().user_visible

        port_name = ('__').join([vm_obj.name, old_if_type, vmi_index])
        port_fq_name = proj_obj.fq_name + [port_name]
        vmi_obj = VirtualMachineInterface(parent_obj=proj_obj, name=port_name)

        id_perms = IdPermsType(enable=True, user_visible=old_user_visible)
        vmi_obj.set_id_perms(id_perms)

        iip_list = old_vmi_obj.get_instance_ip_back_refs()
        if not iip_list:
            lb_pools = si_obj.get_loadbalancer_pool_back_refs()
            if not lb_pools:
                logging.info('\t\tNOTICE lbpool for si %s not found' % si_obj.get_fq_name_str())
                raise NoIdError
            lb_obj = self.vnc_lib.loadbalancer_pool_read(id=lb_pools[0]['uuid'])
            vips = lb_obj.get_virtual_ip_back_refs()
            if not vips:
                logging.info('\t\tNOTICE vip for si %s not found' % si_obj.get_fq_name_str())
                raise NoIdError
            vip_obj = self.vnc_lib.virtual_ip_read(id=vips[0]['uuid'])
            vip_vmis = vip_obj.get_virtual_machine_interface_refs()
            if not vip_vmis:
                logging.info('\t\tNOTICE vip vmi for si %s not found' % si_obj.get_fq_name_str())
                raise NoIdError
            vip_vmi_obj = self.vnc_lib.virtual_machine_interface_read(id=vip_vmis[0]['uuid'])
            iip_list = vip_vmi_obj.get_instance_ip_back_refs()
            if not iip_list:
                logging.info('\t\tNOTICE vip vmi iip for si %s not found' % si_obj.get_fq_name_str())
                raise NoIdError
            
        if iip_list:
            mac_addrs_obj = MacAddressesType([self._mac_alloc(iip_list[0]['uuid'])])
            vmi_obj.set_virtual_machine_interface_mac_addresses(mac_addrs_obj)

        vmi_obj.set_virtual_machine(vm_obj)

        if_properties = VirtualMachineInterfacePropertiesType(old_if_type)
        if_properties.set_local_preference(old_local_pref)
        vmi_obj.set_virtual_machine_interface_properties(if_properties)

        try:
            vn_id = old_vmi_obj.get_virtual_network_refs()[0]['uuid']
            vn_obj = self.vnc_lib.virtual_network_read(id=vn_id)
            vmi_obj.set_virtual_network(vn_obj)
        except Exception as e:
            logging.error('\t\tVMI %s (%s) VN not found %s' % (old_vmi_obj.name, old_vmi_obj.uuid, str(e)))

        try:
            sg_id = old_vmi_obj.get_security_group_refs()[0]['uuid']
            sg_obj = self.vnc_lib.security_group_read(id=sg_id)
            vmi_obj.set_security_group(sg_obj)
        except Exception as e:
            logging.error('\t\tVMI %s (%s) SG not found %s' % (old_vmi_obj.name, old_vmi_obj.uuid, str(e)))

        '''
        try:
            rt_id = old_vmi_obj.get_interface_route_table_refs()[0]['uuid']
            rt_obj = self.vnc_lib.interface_route_table_read(id=rt_id)
            vmi_obj.set_interface_route_table(rt_obj)
        except Exception as e:
            logging.error('\t\tVMI %s (%s) RT not found %s' % (old_vmi_obj.name, old_vmi_obj.uuid, str(e)))
        '''

        try:
            self.vnc_lib.virtual_machine_interface_create(vmi_obj)
            logging.info('\t\tCREATED VMI %s (%s) and linked to VM' % (vmi_obj.name, vmi_obj.uuid))
        except RefsExistError:
            self.vnc_lib.virtual_machine_interface_update(vmi_obj)
            logging.info('\t\tUPDATED VMI %s (%s) and linked to VM' % (vmi_obj.name, vmi_obj.uuid))
        
        self.migrate_iip_and_fip(si_obj, iip_list, vmi_obj, old_vmi_obj)

        if old_vmi_obj.uuid != vmi_obj.uuid:
            try:
                self.vnc_lib.virtual_machine_interface_delete(id=old_vmi_obj.uuid)
                logging.info('\t\tDELETED VMI %s (%s) deleted from VM' % (old_vmi_obj.name, old_vmi_obj.uuid))
            except RefsExistError:
                logging.info('\t\tDELETE VMI %s (%s) failed' % (old_vmi_obj.name, old_vmi_obj.uuid))
                cgitb_error_log()
            except NoIdError:
                logging.info('\t\tDELETE VMI %s (%s) failed' % (old_vmi_obj.name, old_vmi_obj.uuid))
                cgitb_error_log()

        return vmi_obj

    def migrate_vm(self, si_obj, st_obj, proj_obj, vm_obj):
        vm_obj.set_display_name(vm_obj.name + '__' + 'network-namespace')
        self.vnc_lib.virtual_machine_update(vm_obj)
        logging.info('\tVM display name updated to %s' % vm_obj.display_name)

        old_vmi_list = vm_obj.get_virtual_machine_interface_back_refs()
        if not old_vmi_list:
            logging.error('\tVMI LIST empty')
            return
        if len(old_vmi_list) == 0 or len(old_vmi_list) > 2:
            logging.error('\tVMI LIST count %d not correct' % (len(old_vmi_list)))
        for old_vmi in old_vmi_list:
            logging.info('\t\tUPGRADE LIST VMI: %s %s' % (old_vmi['to'], old_vmi['uuid']))
        for old_vmi in old_vmi_list:
            old_vmi_obj = self.vnc_lib.virtual_machine_interface_read(id=old_vmi['uuid'])
            try:
                logging.info('\t\tSTART: upgrade vmi %s %s' % (old_vmi_obj.name, old_vmi_obj.uuid))
                new_vmi_obj = self.migrate_vmi(si_obj, st_obj, proj_obj, old_vmi_obj, vm_obj)
                logging.info('\t\tDONE: upgrade vmi %s %s' % (new_vmi_obj.name, new_vmi_obj.uuid))
            except NoIdError:
                continue
            except Exception:
                cgitb_error_log()

    def migrate_si(self, si_obj, st_obj):
        proj_obj = self.vnc_lib.project_read(fq_name=si_obj.fq_name[:-1])
        if not proj_obj:
            return
        vm_list = si_obj.get_virtual_machine_back_refs()
        if not vm_list:
            logging.error('\tVM LIST empty')
            return
        if len(vm_list) != 2:
            logging.error('\tVM LIST count %d not correct' % (len(vm_list)))
        for vm in vm_list:
            logging.info('\tUPGRADE LIST VM: %s %s' % (vm['to'], vm['uuid']))
        for vm in vm_list:
            vm_obj = self.vnc_lib.virtual_machine_read(id=vm['uuid'])
            try:
                logging.info('\tSTART: upgrade vm %s (%s)' % (vm_obj.display_name, vm_obj.uuid))
                self.migrate_vm(si_obj, st_obj, proj_obj, vm_obj)
                logging.info('\tDONE: upgrade vm %s (%s)' % (vm_obj.display_name, vm_obj.uuid))
            except Exception:
                cgitb_error_log()

    def migrate_all_si(self):
        si_count = 0
        si_list = self.vnc_lib.service_instances_list()
        for si in si_list['service-instances']:
            si_obj = self.vnc_lib.service_instance_read(fq_name=si['fq_name'])
            st_obj = self.vnc_lib.service_template_read(id=si_obj.get_service_template_refs()[0]['uuid'])
            try:
                si_count += 1
                logging.info('START SI %d: upgrade si %s (%s)' % (si_count, si_obj.fq_name, si_obj.uuid))
                self.migrate_si(si_obj, st_obj)
                logging.info('DONE SI %d: upgrade si %s (%s)' % (si_count, si_obj.fq_name, si_obj.uuid))
            except Exception:
                cgitb_error_log()

def cgitb_error_log():
    string_buf = cStringIO.StringIO()
    cgitb.Hook(file=string_buf, format="text").handle(sys.exc_info())
    logging.info(string_buf.getvalue())

def main():
    logging.basicConfig(filename='upgrade.log', level=logging.INFO)
    cgitb.enable(format='text')
    logging.info('Starting upgrade of services')
    try:
        migrate = MigrateServices()
        migrate.migrate_all_si()
    except Exception:
        cgitb_error_log()

if __name__ == '__main__':
    main()
