import os
import time
import json
import logging
import asyncio
import requests  # to download iso image
from clint.textui import progress  # show progress bar while downloading image
from aiohttp import web  # web-server for ks-file
import virtualbox


from virtualbox.library import AccessMode, DeviceType, StorageControllerType, \
    StorageBus, StorageControllerType, DeviceType, MediumVariant, LockType, \
    USBControllerType, IKeyboard

vbox = virtualbox.VirtualBox()


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path='static',
                          name='static')


def by_name(name):
    return [m for m in vbox.machines if m.name == name]


def create_medium(machine, controller_port, controller_name, 
        location, format, access_mode, device_type, size_gb=0, **kwargs):
    '''
    create medium and attach it to the controller
    '''
    access_mode = getattr(AccessMode, access_mode)
    device_type = getattr(DeviceType, device_type)

    location = os.path.abspath(os.path.join('distros', location))
    medium = vbox.create_medium(format, location, access_mode, device_type)
    if size_gb:
        progress = medium.create_base_storage(
            size_gb*1024*1024*1024, [MediumVariant.standard])
        progress.wait_for_completion()
    om = vbox.open_medium(location, device_type, access_mode, False)
    machine.attach_device(controller_name, controller_port, 0, device_type, om)


def create_storage_controller(machine, name, storage_type, storage_bus, 
        medium, **kwargs):
    '''
    create storage controller
    '''
    storage_bus = getattr(StorageBus, storage_bus)
    controller = machine.add_storage_controller(name, storage_bus)
    storage_type = getattr(StorageControllerType, storage_type)
    controller.controller_type = storage_type
    if storage_bus == StorageBus.sata:
        controller.port_count = len(medium)
    return controller


def create_usb_controller(machine, name, controller_type):
    controller_type = getattr(USBControllerType, controller_type)
    machine.add_usb_controller(name, controller_type)


def create_shared_folder(machine, host_path, name=None, writable=False, 
        automount=False):
    host_path = os.path.abspath(host_path)
    if not name:
        name = os.path.basename(host_path)
    machine.create_shared_folder(name, host_path, writable, automount)


def create(name, settings_file, flags, groups, os_type_id, 
        memory_mb, storage_controller, usb_controller, shared_folder,
        cpu_count, **kwargs):
    if len(by_name(name)) > 0:
        print('{} already created. skip creation!'.format(name))
        return
    print('creating {}'.format(name))
    machine = vbox.create_machine(
        settings_file=settings_file,
        name=name, 
        groups=groups,
        flags=flags, 
        os_type_id=os_type_id)
    for controller in storage_controller:
        create_storage_controller(machine=machine, **controller)
    for controller in usb_controller:
        create_usb_controller(machine=machine, **controller)
    for folder in shared_folder:
        create_shared_folder(machine=machine, **folder)
    machine.vram_size = 32
    machine.memory_size = memory_mb
    machine.cpu_count = cpu_count
    # for the storage setup we need to register the device and create a session
    vbox.register_machine(machine)
    with machine.create_session() as session:
        for controller in storage_controller:
            port = 0
            for m in controller['medium']:
                if 'location' in m:
                    create_medium(
                        machine=session.machine, 
                        controller_port=port, 
                        controller_name=controller['name'], 
                        **m)
                    port += 1
        session.machine.save_settings()


def start_webserver(loop, **kwargs):
    app = web.Application()
    setup_static_routes(app)
    handler = app.make_handler()
    host, port = '0.0.0.0', 8000
    coroutine = loop.create_server(handler, host, port)
    print('start webserver at {}:{}'.format(host, port))
    server = loop.run_until_complete(coroutine)
    return server, handler, app

def install(name, **kwargs):
    machine = by_name(name)[0]
    session = virtualbox.Session()
    progress = machine.launch_vm_process(session)
    progress.wait_for_completion()
    console = session.console
    # we assume the live system on the disk has been booted after 10 seconds...
    time.sleep(10)
    console.keyboard.put_keys(['\n', 'F6', 'ESC']+['BKSP']*10+\
        [x for x in 'ks=http://10.0.2.2:8000/static/xenial.ks']+['\n'])


def check_iso_download(server, location):
    link = '{}/{}'.format(server, location)
    dest = os.path.join('distros', location)
    if os.path.exists(dest):
        return
    with open(dest, "wb") as f:
        response = requests.get(link, stream=True)
        total_length = int(response.headers.get('content-length'))
        for chunk in progress.bar(
            response.iter_content(chunk_size=1024), 
            expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()

    
def check_iso_exists(storage_controller, **kwargs):
    for ctrl in storage_controller:
        for medium in ctrl['medium']:
            if 'server' in medium:
                check_iso_download(medium['server'], medium['location'])

                
def create_folder(storage_controller, **kwargs):
    for ctrl in storage_controller:
        for medium in ctrl['medium']:
            if 'server' in medium:
                continue
            if 'device_type' in medium and medium['device_type'] == 'dvd':
                continue
            location = os.path.normpath(medium['location'])
            location = os.path.split(location)[0]
            if os.path.isdir(location):
                continue
            os.makedirs(location)
            

async def setup_async(loop, config):
    create(**config)
    install(**config)

            
def main():
    loop = asyncio.get_event_loop()
    for config_file in os.listdir('config'):
        print('use config file: {}'.format(config_file))
        config = json.load(open(os.path.join('config', config_file)))
        check_iso_exists(**config)
        server, handler, app = start_webserver(loop)
        loop.run_until_complete(setup_async(loop, config))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("CTRL+C detected, exiting")
        finally:
            loop.run_until_complete(app.shutdown())
            loop.run_until_complete(handler.shutdown(5.0))
            loop.run_until_complete(app.cleanup())
    loop.close()
    

if __name__ == '__main__':
    main()