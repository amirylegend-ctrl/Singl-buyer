# Singl_buyer V 2.0 + Rejoiner + Plugin Manager + Max Total Price
# Copyright 2025
from babase import Plugin, open_url
from bauiv1 import (
    get_special_widget as gsw,
    containerwidget as cw,
    screenmessage as push,
    buttonwidget as bw,
    textwidget as tw,
    scrollwidget as sw,
    gettexture as gt,
    apptimer as teck,
    getsound as gs,
    app as APP,
    CallPartial,
    CallStrict,
    checkboxwidget
)
from bascenev1 import (
    get_chat_messages as GCM,
    chatmessage as CM,
    connect_to_party as original_connect_to_party,
    get_connection_to_host_info_2,
    disconnect_from_host
)
import re
import time
import json
import os
import glob
from datetime import datetime

# ba_meta require api 9
# ba_meta export babase.Plugin
class Singl_buyer(Plugin):
    
    def __init__(s):
        s.z = []
        s.last_triggered = {}
        s.cooldown = 2.0
        s.enabled = True
        s.anti_recoil = True  
        
        s.listening_speed = 0.3  
        s.performance_mode = "normal" 
        
        s.waiting_for_purchase = {}
        s.max_prices = APP.config.get('singl_buyer_max_prices', {})
        s.max_total_price = APP.config.get('singl_buyer_max_total_price', None)  # اضافه شده
        s.pending_purchase = None
        s.current_settings_window = None  
        s.current_main_window = None  
        s.rejoin_enabled = False
        s.rejoin_address = None
        s.rejoin_port = None
        s.last_rejoin_attempt = 0
        s.rejoin_cooldown = 10
        s.rejoin_attempts = 0
        s.max_rejoin_attempts = 5
        s.rejoin_timer = None
        s.plugin_states = APP.config.get('singl_buyer_plugin_states', {})
        
        s.backup_dir = "ba_data/singl_buyer_backups"
        if not os.path.exists(s.backup_dir):
            os.makedirs(s.backup_dir)
        s.override_connect_to_party()
        
        teck(10, s.show_welcome_message)
        
        s.setup_ui()
        teck(5, s.ear)
        s.start_rejoin_check()

    def show_welcome_message(s):
        push("Power by Singl | @Amiry_11228 | t.me/SinglMusic | V3.0", color=(0, 0.8, 1))
        gs('dingSmall').play()
    
    def get_plugin_files(s):
        plugin_files = []
        possible_paths = [
            "ba_data/python/mods",
            "mods",
            "../mods",
            "../../mods",  
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "BombSquad", "mods"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "mods"),
        ]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(current_dir)
        try:
            user_dir = os.path.expanduser("~")
            possible_paths.extend([
                os.path.join(user_dir, "BombSquad", "mods"),
                os.path.join(user_dir, ".bombsquad", "mods"),
                os.path.join(user_dir, "AppData", "Roaming", "BombSquad", "mods"),
            ])
        except:
            pass
        found_mods_dir = None
        for mod_dir in possible_paths:
            try:
                if os.path.exists(mod_dir):
                    py_files = glob.glob(os.path.join(mod_dir, "*.py"))
                    if py_files:
                        found_mods_dir = mod_dir
                        push(f"Found mods dir: {mod_dir}", color=(0, 1, 0))
                        break
            except Exception as e:
                print(f"Error checking path {mod_dir}: {e}")
                continue
        if found_mods_dir:
            try:
                py_files = glob.glob(os.path.join(found_mods_dir, "*.py"))
                for py_file in py_files:
                    filename = os.path.basename(py_file)
                    if (filename != "__init__.py" and 
                        not filename.startswith(".") and 
                        filename != os.path.basename(__file__)):
                        plugin_files.append(filename)
                s.mods_dir = found_mods_dir
                
            except Exception as e:
                print(f"Error reading mods directory: {e}")
                push(f"Error reading mods: {str(e)}", color=(1, 0, 0))
        else:
            default_dir = "ba_data/python/mods"
            try:
                if os.path.exists(default_dir):
                    py_files = glob.glob(os.path.join(default_dir, "*.py"))
                    for py_file in py_files:
                        filename = os.path.basename(py_file)
                        if filename != "__init__.py" and not filename.startswith(".") and filename != os.path.basename(__file__):
                            plugin_files.append(filename)
                    s.mods_dir = default_dir
                else:
                    os.makedirs(default_dir, exist_ok=True)
                    s.mods_dir = default_dir
                    push("Created default mods directory", color=(0, 1, 0))
            except Exception as e:
                print(f"Error with default mods directory: {e}")
        
        return sorted(plugin_files)

    def toggle_plugin_state(s, plugin_name):
        s.plugin_states[plugin_name] = not s.plugin_states.get(plugin_name, True)
        APP.config['singl_buyer_plugin_states'] = s.plugin_states
        APP.config.commit()
        
        status = "DISABLED" if not s.plugin_states[plugin_name] else "ENABLED"
        color = (1, 0, 0) if not s.plugin_states[plugin_name] else (0, 1, 0)
        push(f"{plugin_name}: {status}", color=color)
        
        if s.plugin_states[plugin_name]:
            gs('dingSmall').play()
        else:
            gs('error').play()

    def delete_plugin(s, plugin_name):
        if not hasattr(s, 'mods_dir') or not s.mods_dir:
            push("Mods directory not found", color=(1, 0, 0))
            return False
            
        plugin_path = os.path.join(s.mods_dir, plugin_name)
        
        try:
            if os.path.exists(plugin_path):
                backup_dir = os.path.join(s.backup_dir, "deleted_plugins")
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                backup_path = os.path.join(backup_dir, f"{plugin_name}.backup")
                with open(plugin_path, 'r', encoding='utf-8', errors='ignore') as source:
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(source.read())
                os.remove(plugin_path)
                if plugin_name in s.plugin_states:
                    del s.plugin_states[plugin_name]
                    APP.config['singl_buyer_plugin_states'] = s.plugin_states
                    APP.config.commit()
                
                push(f"Deleted: {plugin_name}", color=(1, 0.5, 0))
                gs('gunCocking').play()
                return True
            else:
                push(f"Plugin not found: {plugin_name}", color=(1, 0, 0))
                return False
        except Exception as e:
            push(f"Delete failed: {str(e)}", color=(1, 0, 0))
            return False

    def show_plugin_manager(s, current_window=None):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(550, 500)
        
        tw(
            parent=w,
            text='PLUGIN MANAGER',
            position=(275, 470),
            h_align='center',
            scale=1.2,
            color=(0, 0.8, 1)
        )
        mods_path = s.mods_dir if hasattr(s, 'mods_dir') and s.mods_dir else "Not found"
        tw(
            parent=w,
            text=f'Mods Path: {mods_path}',
            position=(275, 450),
            h_align='center',
            scale=0.5,
            color=(0.8, 0.8, 0.8)
        )
        
        scroll = sw(
            parent=w,
            size=(510, 350),
            position=(20, 90)
        )
        
        plugin_files = s.get_plugin_files()
        scroll_height = max(350, len(plugin_files) * 60)
        
        scroll_content = cw(
            parent=scroll,
            size=(490, scroll_height),
            background=False
        )
        
        if not plugin_files:
            tw(
                parent=scroll_content,
                text='No plugins found in mods folder',
                position=(235, 175),
                h_align='center',
                color=(0.7, 0.7, 0.7)
            )
        else:
            y_pos = scroll_height - 40
            for plugin_file in plugin_files:
                plugin_bg = cw(
                    parent=scroll_content,
                    size=(470, 50),
                    position=(10, y_pos),
                    color=(0.25, 0.25, 0.3)
                )
                tw(
                    parent=plugin_bg,
                    text=plugin_file,
                    position=(15, 15),
                    h_align='left',
                    v_align='center',
                    scale=0.8,
                    color=(0.5, 1, 0)
                )
                is_enabled = s.plugin_states.get(plugin_file, True)
                status_color = (0, 0.8, 0) if is_enabled else (0.8, 0, 0)
                status_text = 'ENABLED' if is_enabled else 'DISABLED'
                
                tw(
                    parent=plugin_bg,
                    text=status_text,
                    position=(200, 15),
                    h_align='left',
                    v_align='center',
                    scale=0.7,
                    color=status_color
                )
                toggle_color = (0.8, 0.2, 0.2) if is_enabled else (0.2, 0.8, 0.2)
                toggle_text = 'DISABLE' if is_enabled else 'ENABLE'
                
                bw(
                    parent=plugin_bg,
                    position=(300, 5),
                    size=(70, 40),
                    label=toggle_text,
                    color=toggle_color,
                    textcolor=(1, 1, 1),
                    scale=0.6,
                    on_activate_call=CallPartial(s.toggle_plugin_state, plugin_file)
                )
                bw(
                    parent=plugin_bg,
                    position=(380, 5),
                    size=(70, 40),
                    label='DELETE',
                    color=(0.8, 0.5, 0.2),
                    textcolor=(1, 1, 1),
                    scale=0.6,
                    on_activate_call=CallPartial(s.show_delete_confirmation, plugin_file, w)
                )
                
                y_pos -= 55
        bw(
            parent=w,
            position=(50, 40),
            size=(150, 35),
            label='REFRESH LIST',
            color=(0.3, 0.5, 0.8),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.show_plugin_manager, w)
        )
        
        bw(
            parent=w,
            position=(220, 40),
            size=(150, 35),
            label='ENABLE ALL',
            color=(0.2, 0.7, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.enable_all_plugins, w)
        )
        
        bw(
            parent=w,
            position=(390, 40),
            size=(150, 35),
            label='DISABLE ALL',
            color=(0.7, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.disable_all_plugins, w)
        )

    def show_delete_confirmation(s, plugin_name, current_window):
        w = s.create_window(400, 200)
        
        tw(
            parent=w,
            text='DELETE CONFIRMATION',
            position=(170, 170),
            h_align='center',
            scale=1.0,
            color=(1, 0.5, 0)
        )
        
        tw(
            parent=w,
            text=f'Delete {plugin_name}?',
            position=(170, 140),
            h_align='center',
            scale=0.8,
            color=(1, 0, 0)
        )
        
        bw(
            parent=w,
            position=(80, 70),
            size=(120, 35),
            label='DELETE',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.confirm_delete_plugin, plugin_name, w, current_window)
        )
        
        bw(
            parent=w,
            position=(220, 70),
            size=(120, 35),
            label='CANCEL',
            color=(0.4, 0.4, 0.4),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.close_window, w)
        )

    def confirm_delete_plugin(s, plugin_name, confirm_window, manager_window):
        success = s.delete_plugin(plugin_name)
        s.close_window(confirm_window)
        if success:
            s.show_plugin_manager(manager_window)

    def enable_all_plugins(s, current_window):
        plugin_files = s.get_plugin_files()
        for plugin_file in plugin_files:
            s.plugin_states[plugin_file] = True
        
        APP.config['singl_buyer_plugin_states'] = s.plugin_states
        APP.config.commit()
        
        push("All plugins enabled", color=(0, 1, 0))
        gs('dingSmall').play()
        s.show_plugin_manager(current_window)

    def disable_all_plugins(s, current_window):
        plugin_files = s.get_plugin_files()
        for plugin_file in plugin_files:
            s.plugin_states[plugin_file] = False
        
        APP.config['singl_buyer_plugin_states'] = s.plugin_states
        APP.config.commit()
        
        push("All plugins disabled", color=(1, 0.5, 0))
        gs('error').play()
        s.show_plugin_manager(current_window)

    def override_connect_to_party(s):
        def custom_connect_to_party(address, port=43210, print_progress=False):
            s.store_server_info(address, port)
            return original_connect_to_party(address, port, print_progress)
        import bascenev1 as bs
        bs.connect_to_party = custom_connect_to_party
    
    def start_rejoin_check(s):
        def _check_connection():
            try:
                if (s.rejoin_enabled and s.rejoin_address and s.rejoin_port and 
                    not get_connection_to_host_info_2()):
                    
                    current_time = time.time()
                    if current_time - s.last_rejoin_attempt > s.rejoin_cooldown:
                        
                        if s.rejoin_attempts < s.max_rejoin_attempts:
                            s.attempt_rejoin()
                        else:
                            s.rejoin_enabled = False
                            push("Auto Rejoin disabled - too many attempts", color=(1, 0, 0))
                            s.update_rejoin_ui()
                if hasattr(s, 'rejoin_timer'):
                    s.rejoin_timer = teck(2.0, _check_connection)
                    
            except Exception as e:
                print(f"Rejoin check error: {e}")
                if hasattr(s, 'rejoin_timer'):
                    s.rejoin_timer = teck(2.0, _check_connection)
        
        s.rejoin_timer = teck(2.0, _check_connection)

    def attempt_rejoin(s):
        try:
            s.last_rejoin_attempt = time.time()
            s.rejoin_attempts += 1
            
            push(f"Rejoin attempt {s.rejoin_attempts}/{s.max_rejoin_attempts}", color=(1, 1, 0))
            if get_connection_to_host_info_2():
                disconnect_from_host()
            def do_rejoin():
                try:
                    original_connect_to_party(s.rejoin_address, s.rejoin_port)
                    push(f"Connecting to {s.rejoin_address}:{s.rejoin_port}", color=(0, 1, 0))
                except Exception as e:
                    print(f"Rejoin connection error: {e}")
                    push("Rejoin connection failed", color=(1, 0, 0))
            
            teck(1.0, do_rejoin)
            
        except Exception as e:
            print(f"Rejoin error: {e}")
            push("Rejoin attempt failed", color=(1, 0, 0))

    def manual_rejoin(s):
        if s.rejoin_address and s.rejoin_port:
            s.rejoin_attempts = 0 
            s.attempt_rejoin()
        else:
            push("No server info available", color=(1, 0, 0))

    def store_server_info(s, address, port=43210):
        s.rejoin_address = address
        s.rejoin_port = port
        s.rejoin_attempts = 0 
        push(f"Server info stored: {address}:{port}", color=(0, 1, 0))
        s.update_rejoin_ui()

    def toggle_auto_rejoin(s):
        s.rejoin_enabled = not s.rejoin_enabled
        status = "ON" if s.rejoin_enabled else "OFF"
        color = (0, 1, 0) if s.rejoin_enabled else (1, 0, 0)
        push(f"Auto Rejoin: {status}", color=color)
        
        if s.rejoin_enabled:
            gs('dingSmall').play()
            if not s.rejoin_address or not s.rejoin_port:
                push("Join a server first to enable auto-rejoin", color=(1, 1, 0))
        else:
            gs('error').play()
        
        s.update_rejoin_ui()

    def update_rejoin_ui(s):
        if hasattr(s, 'rejoin_ui_button'):
            try:
                button_color = (0.1, 0.8, 0.1) if s.rejoin_enabled else (0.1, 0.6, 0.1)
                bw(s.rejoin_ui_button, color=button_color)
            except:
                pass
        if hasattr(s, 'rejoin_main_button'):
            try:
                status_color = (0, 0.8, 0) if s.rejoin_enabled else (0.8, 0, 0)
                status_text = 'REJOIN: ON' if s.rejoin_enabled else 'REJOIN: OFF'
                bw(s.rejoin_main_button, label=status_text, color=status_color)
            except:
                pass
        if hasattr(s, 'rejoin_status_button'):
            try:
                status_color = (0, 0.8, 0) if s.rejoin_enabled else (0.8, 0, 0)
                status_text = 'AUTO REJOIN: ON' if s.rejoin_enabled else 'AUTO REJOIN: OFF'
                bw(s.rejoin_status_button, label=status_text, color=status_color)
            except:
                pass

    def show_rejoin_panel(s, current_window=None):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(400, 300)
        
        tw(
            parent=w,
            text='REJOIN SYSTEM',
            position=(170, 270),
            h_align='center',
            scale=1.1,
            color=(0, 0.8, 1)
        )
        status_color = (0, 0.8, 0) if s.rejoin_enabled else (0.8, 0, 0)
        status_text = 'AUTO REJOIN: ON' if s.rejoin_enabled else 'AUTO REJOIN: OFF'
        
        s.rejoin_status_button = bw(
            parent=w,
            position=(120, 220),
            size=(160, 35),
            label=status_text,
            color=status_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.toggle_auto_rejoin_from_panel, w)
        )
        bw(
            parent=w,
            position=(120, 170),
            size=(160, 35),
            label='MANUAL REJOIN',
            color=(0.1, 0.6, 0.1),
            textcolor=(1, 1, 1),
            on_activate_call=CallStrict(s.manual_rejoin)
        )
        server_info = f"Server: {s.rejoin_address}:{s.rejoin_port}" if s.rejoin_address else "No server info - Join a server first"
        tw(
            parent=w,
            text=server_info,
            position=(170, 130),
            h_align='center',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        attempts_info = f"Attempts: {s.rejoin_attempts}/{s.max_rejoin_attempts}"
        tw(
            parent=w,
            text=attempts_info,
            position=(170, 110),
            h_align='center',
            scale=0.6,
            color=(0.7, 0.7, 1)
        )
        connection_status = "Connected" if get_connection_to_host_info_2() else "Disconnected"
        connection_color = (0, 1, 0) if get_connection_to_host_info_2() else (1, 0, 0)
        tw(
            parent=w,
            text=f"Status: {connection_status}",
            position=(170, 90),
            h_align='center',
            scale=0.8,
            color=connection_color
        )
        bw(
            parent=w,
            position=(135, 50),
            size=(160, 60),
            label='ADVANCED SETTINGS',
            color=(0.4, 0.9, 0.6),
            textcolor=(1, 1, 1),
            scale=0.8,
            on_activate_call=CallPartial(s.show_rejoin_settings, w)
        )

    def toggle_auto_rejoin_from_panel(s, current_window):
        s.toggle_auto_rejoin()
        s.show_rejoin_panel(current_window)

    def show_rejoin_settings(s, current_window=None):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(350, 250)
        
        tw(
            parent=w,
            text='REJOIN SETTINGS',
            position=(170, 220),
            h_align='center',
            scale=1.0,
            color=(0, 0.8, 1)
        )
        tw(
            parent=w,
            text=f'Max Attempts: {s.max_rejoin_attempts}',
            position=(30, 180),
            scale=0.8,
            color=(0.8, 0.8, 0.8)
        )
        
        bw(
            parent=w,
            position=(200, 185),
            size=(30, 25),
            label='-',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            scale=0.7,
            on_activate_call=CallPartial(s.adjust_max_attempts, -1, w)
        )
        
        bw(
            parent=w,
            position=(240, 185),
            size=(30, 25),
            label='+',
            color=(0.2, 0.8, 0.2),
            textcolor=(1, 1, 1),
            scale=0.7,
            on_activate_call=CallPartial(s.adjust_max_attempts, 1, w)
        )
        tw(
            parent=w,
            text=f'Cooldown: {s.rejoin_cooldown}s',
            position=(30, 140),
            scale=0.8,
            color=(0.8, 0.8, 0.8)
        )
        
        bw(
            parent=w,
            position=(200, 140),
            size=(30, 25),
            label='-',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            scale=0.7,
            on_activate_call=CallPartial(s.adjust_cooldown, -5, w)
        )
        
        bw(
            parent=w,
            position=(240, 140),
            size=(30, 25),
            label='+',
            color=(0.2, 0.8, 0.2),
            textcolor=(1, 1, 1),
            scale=0.7,
            on_activate_call=CallPartial(s.adjust_cooldown, 5, w)
        )
        bw(
            parent=w,
            position=(100, 80),
            size=(150,50),
            label='RESET STATISTICS',
            color=(1, 0.1, 0.2),
            textcolor=(1, 1, 1),
            scale=1,
            on_activate_call=CallPartial(s.reset_rejoin_stats, w)
        )

    def adjust_max_attempts(s, change, current_window):
        s.max_rejoin_attempts = max(1, min(20, s.max_rejoin_attempts + change))
        s.show_rejoin_settings(current_window)

    def adjust_cooldown(s, change, current_window):
        s.rejoin_cooldown = max(5, min(60, s.rejoin_cooldown + change))
        s.show_rejoin_settings(current_window)

    def reset_rejoin_stats(s, current_window):
        s.rejoin_attempts = 0
        push("Rejoin statistics reset", color=(0, 1, 0))
        s.show_rejoin_settings(current_window)

    def setup_ui(s):
        from bauiv1lib import party
        
        original_init = party.PartyWindow.__init__
        
        def new_init(self, *args, **kwargs):
            result = original_init(self, *args, **kwargs)

            button_color, text_color = s.get_button_colors()
            button = bw(
                parent=self._root_widget,
                icon=gt('tokens3'),
                position=(self._width - 500, self._height - 70),
                size=(40, 40),
                color=button_color,
                on_activate_call=CallStrict(s.show_main_panel)
            )
            s.ui_button = button
            rejoin_button = bw(
                parent=self._root_widget,
                icon=gt('replayIcon'),
                position=(self._width - 500, self._height - 120),
                size=(40, 40),
                color=(0.1, 0.6, 0.1),
                on_activate_call=CallStrict(s.manual_rejoin)
            )
            s.rejoin_ui_button = rejoin_button
            
            return result
        
        party.PartyWindow.__init__ = new_init

    def get_button_colors(s):
        if not s.enabled:
            return (0.7, 0.1, 0.1), (1, 0.5, 0.5)
        elif s.performance_mode == "best":
            return (1.0, 0.5, 0.0), (1.0, 0.8, 0.0)
        elif s.enabled and s.anti_recoil:
            return (0.6, 0.2, 0.8), (0.9, 0.7, 1)
        else:
            return (0.1, 0.6, 0.1), (0.6, 1, 0.6)

    def create_window(s, width=480, height=380, is_main=False):
        w = cw(
            size=(width, height),
            scale=1.0,
            transition='in_scale',
            color=(0.1, 0, 0.2),
            parent=gsw('overlay_stack')
        )
       
        if is_main:
            cw(w, on_outside_click_call=CallPartial(s.close_window, w))
        else:
            cw(w, on_outside_click_call=CallPartial(s.close_and_return_to_main, w))
            
        return w

    def close_and_return_to_main(s, window):
        s.close_window(window)
        s.show_main_panel()

    def close_window(s, window):
        cw(window, transition='out_scale')
        
        if hasattr(s, 'current_settings_window') and s.current_settings_window == window:
            s.current_settings_window = None
        
        if hasattr(s, 'current_main_window') and s.current_main_window == window:
            s.current_main_window = None

    def show_main_panel(s):
        if s.current_main_window:
            s.close_window(s.current_main_window)
            
        w = s.create_window(500, 450, is_main=True)
        s.current_main_window = w
        
        tw(
            parent=w,
            text='SINGL MOD',
            position=(235, 420),
            h_align='center',
            scale=1.3,
            color=(0, 0.8, 1)
        )
        
        tw(
            parent=w,
            text='Auto Buy System + Rejoin System + Plugin Manager',
            position=(250, 395),
            h_align='center',
            scale=0.7,
            color=(0.4, 1, 0.7)
        )
        
        status_color = (0, 0.8, 0) if s.enabled else (0.8, 0, 0)
        status_text = 'ON' if s.enabled else 'OFF'
        
        s.status_button = bw(
            parent=w,
            position=(345, 350),
            size=(150, 35),
            label=status_text,
            color=status_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.toggle_plugin_from_panel, w)
        )
        
        anti_recoil_color = (0.6, 0.2, 0.8) if s.anti_recoil else (0.4, 0.4, 0.4)
        anti_recoil_text = 'ANTI-RECOIL: ON' if s.anti_recoil else 'ANTI-RECOIL: OFF'
        
        s.anti_recoil_button = bw(
            parent=w,
            position=(10, 350),
            size=(150, 35),
            label=anti_recoil_text,
            color=anti_recoil_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.toggle_anti_recoil_from_panel, w)
        )
        rejoin_status_color = (0, 0.8, 0) if s.rejoin_enabled else (0.8, 0, 0)
        rejoin_status_text = 'REJOIN: ON' if s.rejoin_enabled else 'REJOIN: OFF'
        
        s.rejoin_main_button = bw(
            parent=w,
            position=(200, 350),
            size=(100, 35),
            label=rejoin_status_text,
            color=rejoin_status_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.show_rejoin_panel, w)
        )

        normal_color = (0.3, 0.6, 1.0) if s.performance_mode == "normal" else (0.4, 0.4, 0.4)
        performance_color = (1.0, 0.8, 0.0) if s.performance_mode == "best" else (0.4, 0.4, 0.4)

        s.normal_button = bw(
            parent=w,
            position=(100, 300),
            size=(130, 35),
            label='NORMAL MODE',
            color=normal_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.set_normal_mode_from_panel, w)
        )

        s.performance_button = bw(
            parent=w,
            position=(250, 300),
            size=(130, 35),
            label='BEST PERFORMANCE',
            color=performance_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.set_best_performance_from_panel, w)
        )
        buttons = [
            ('Item Settings', CallPartial(s.show_item_settings, w), (165, 250)),
            ('Plugin Manager', CallPartial(s.show_plugin_manager, w), (165, 200)), 
            ('Backup & Restore', CallPartial(s.show_backup_restore, w), (165, 150)),
            ('Support', CallStrict(s.open_support), (320, 90)),
            ('Channel', CallStrict(s.open_channel), (30, 90)),
        ]
        
        for label, callback, pos in buttons:
            bw(
                parent=w,
                position=pos,
                size=(150, 35),
                label=label,
                on_activate_call=callback
            )
        
        tw(
            parent=w,
            text=f'Items Configured: {len(s.max_prices)}',
            position=(100, 60),
            h_align='center',
            scale=0.8,
            color=(0.4, 0.7, 1)
        )

        tw(
            parent=w,
            text=f'Plugins Found: {len(s.get_plugin_files())}',
            position=(100, 40),
            h_align='center',
            scale=0.8,
            color=(0.7, 0.4, 1)
        )
        
        # نمایش حداکثر قیمت کل
        max_total_price_text = f"Max Total Price: {s.max_total_price if s.max_total_price is not None else 'Not Set'}"
        tw(
            parent=w,
            text=max_total_price_text,
            position=(100, 20),
            h_align='center',
            scale=0.8,
            color=(1, 0.8, 0.2) if s.max_total_price is not None else (0.7, 0.7, 0.7)
        )
        
        status_info = []
        if not s.enabled:
            status_info.append("PLUGIN DISABLED")
        elif s.performance_mode == "best":
            status_info.append("BEST PERFORMANCE")
        elif s.enabled and s.anti_recoil:
            status_info.append("ACTIVE + ANTI-RECOIL")
        else:
            status_info.append("ACTIVE (NORMAL)")
        
        if s.rejoin_enabled:
            status_info.append("+ REJOIN ACTIVE")
        
        if s.max_total_price is not None:
            status_info.append(f"+ MAX TOTAL: {s.max_total_price}")
        
        status_text = " | ".join(status_info)
        info_color = (0.8, 0.4, 1) if s.anti_recoil else (0, 1, 0)
        
        tw(
            parent=w,
            text=status_text,
            position=(105, 0),
            h_align='center',
            scale=0.6,
            color=info_color
        )
        
        tw(
            parent=w,
            text='Power by Singl | @Amiry_11228',
            position=(250, -20),
            h_align='center',
            scale=0.5,
            color=(0.8, 0.8, 0.5)
        )
    
    def set_normal_mode_from_panel(s, current_window):
        if s.performance_mode != "normal":
            s.set_normal_mode()
            s.refresh_main_panel(current_window)
    
    def set_best_performance_from_panel(s, current_window):
        if s.performance_mode != "best":
            s.show_performance_confirmation(current_window)

    def show_performance_confirmation(s, current_window):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(450, 250)
        
        tw(
            parent=w,
            text='WARNING: BEST PERFORMANCE MODE',
            position=(205, 210),
            h_align='center',
            scale=0.8,
            color=(1.0, 0.6, 0.0)
        )
        
        tw(
            parent=w,
            text='This mode will set listening speed to 0.0001 seconds',
            position=(200, 180),
            h_align='center',
            scale=0.7,
            color=(1, 1, 1)
        )
        
        tw(
            parent=w,
            text='Your phone may get very hot and FPS may drop!',
            position=(200, 160),
            h_align='center',
            scale=0.7,
            color=(1, 0.8, 0.8)
        )
        
        tw(
            parent=w,
            text='Are you sure?',
            position=(200, 140),
            h_align='center',
            scale=0.8,
            color=(1, 1, 0.5)
        )
        
        bw(
            parent=w,
            position=(100, 80),
            size=(100, 40),
            label='YES',
            color=(0.2, 0.8, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.set_best_performance, w)
        )
        
        bw(
            parent=w,
            position=(250, 80),
            size=(100, 40),
            label='NO',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.close_window, w)
        )

    def set_best_performance(s, window=None):
        s.performance_mode = "best"
        s.listening_speed = 0.0001
        
        if window:
            s.close_window(window)
            s.close_all_panels()
        
        push("BEST PERFORMANCE MODE ACTIVATED!", color=(1.0, 0.6, 0.0))
        gs('orchestraHit').play()
        
        s.update_main_button()
        s.announce_status("Best Performance Mode Activated!")
    
    def set_normal_mode(s):
        s.performance_mode = "normal"
        s.listening_speed = 0.3
        
        push("NORMAL MODE ACTIVATED", color=(0, 1, 0))
        gs('dingSmall').play()
        
        s.update_main_button()
        s.announce_status("Normal Mode Activated")
    
    def close_all_panels(s):
        if s.current_main_window:
            s.close_window(s.current_main_window)
            s.current_main_window = None
        
        if s.current_settings_window:
            s.close_window(s.current_settings_window)
            s.current_settings_window = None
    
    def toggle_plugin_from_panel(s, current_window):
        s.toggle_plugin()
        s.refresh_main_panel(current_window)
    
    def toggle_anti_recoil_from_panel(s, current_window):
        s.toggle_anti_recoil()
        s.refresh_main_panel(current_window)
    
    def refresh_main_panel(s, current_window):
        if current_window:
            s.close_window(current_window)
        s.show_main_panel()
    
    def toggle_anti_recoil(s):
        s.anti_recoil = not s.anti_recoil
        
        anti_recoil_color = (0.6, 0.2, 0.8) if s.anti_recoil else (0.4, 0.4, 0.4)
        anti_recoil_text = 'ANTI-RECOIL: ON' if s.anti_recoil else 'ANTI-RECOIL: OFF'
        
        if hasattr(s, 'anti_recoil_button'):
            try:
                bw(s.anti_recoil_button, label=anti_recoil_text, color=anti_recoil_color)
            except:
                pass
        
        s.update_main_button()
        
        status_text = "ON" if s.anti_recoil else "OFF"
        color = (0.8, 0.4, 1) if s.anti_recoil else (0.7, 0.7, 0.7)
        push(f"Anti-Recoil: {status_text}", color=color)
        gs('dingSmall' if s.anti_recoil else 'error').play()

        if s.anti_recoil:
            s.announce_status("Anti-Recoil ON!")
        else:
            s.announce_status("Anti-Recoil OFF /: ")
        
        if hasattr(s, 'current_settings_window') and s.current_settings_window:
            s.refresh_item_settings()
    
    def toggle_plugin(s):
        s.enabled = not s.enabled
        status = "ON" if s.enabled else "OFF"
        color = (0, 1, 0) if s.enabled else (1, 0, 0)
        push(f"Singl_buyer: {status}", color=color)
        gs('dingSmall' if s.enabled else 'error').play()

        if s.enabled:
            s.announce_status("Singl Buyer ON (:")
        else:
            s.announce_status("Singl Buyer OFF ):")
        
        s.update_main_button()
        
        if hasattr(s, 'status_button'):
            try:
                status_color = (0, 0.8, 0) if s.enabled else (0.8, 0, 0)
                bw(s.status_button, label=status, color=status_color)
            except:
                pass
        
        if hasattr(s, 'item_status_button'):
            try:
                status_color = (0, 0.8, 0) if s.enabled else (0.8, 0, 0)
                bw(s.item_status_button, label=status, color=status_color)
            except:
                pass
        
        if hasattr(s, 'item_anti_recoil_button'):
            try:
                anti_recoil_color = (0.6, 0.2, 0.8) if s.anti_recoil else (0.4, 0.4, 0.4)
                anti_recoil_text = 'ON' if s.anti_recoil else 'OFF'
                bw(s.item_anti_recoil_button, label=anti_recoil_text, color=anti_recoil_color)
            except:
                pass
        
        if hasattr(s, 'current_settings_window') and s.current_settings_window:
            s.refresh_item_settings()
    
    def announce_status(s, message):
        try:
            CM(f"Singl Buyer: {message}")
        except:
            pass
    
    def update_main_button(s):
        if hasattr(s, 'ui_button'):
            try:
                button_color, text_color = s.get_button_colors()
                bw(s.ui_button, color=button_color, textcolor=text_color)
            except:
                pass
    
    def show_item_settings(s, current_window=None):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(500, 380)  # افزایش عرض برای اضافه کردن دکمه جدید
        s.current_settings_window = w  
        
        tw(
            parent=w,
            text='ITEM SETTINGS',
            position=(220, 350),
            h_align='center',
            scale=1.1,
            color=(0, 0.8, 1)
        )
        
        # ردیف اول: وضعیت پلاگین
        status_color = (0, 0.8, 0) if s.enabled else (0.8, 0, 0)
        status_text = 'ON' if s.enabled else 'OFF'
        
        s.item_status_button = bw(
            parent=w,
            position=(400, 320),
            size=(60, 25),
            label=status_text,
            color=status_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.toggle_plugin_from_settings, w)
        )
        
        tw(
            parent=w,
            text='status:',
            position=(350, 320),
            h_align='right',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        
        # ردیف دوم: ضد لگد
        anti_recoil_color = (0.6, 0.2, 0.8) if s.anti_recoil else (0.4, 0.4, 0.4)
        anti_recoil_text = 'ON' if s.anti_recoil else 'OFF'
        
        s.item_anti_recoil_button = bw(
            parent=w,
            position=(400, 290),
            size=(60, 25),
            label=anti_recoil_text,
            color=anti_recoil_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.toggle_anti_recoil_from_settings, w)
        )
        
        tw(
            parent=w,
            text='anti-recoil:',
            position=(350, 290),
            h_align='right',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        
        # ردیف سوم: حداکثر قیمت کل (اضافه شده)
        max_total_price_color = (1, 0.8, 0.2) if s.max_total_price is not None else (0.4, 0.4, 0.4)
        max_total_price_text = str(s.max_total_price) if s.max_total_price is not None else 'Not Set'
        
        s.item_max_total_price_button = bw(
            parent=w,
            position=(400, 260),
            size=(60, 25),
            label=max_total_price_text,
            color=max_total_price_color,
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.show_max_total_price_dialog, w)
        )
        
        tw(
            parent=w,
            text='max total price:',
            position=(350, 260),
            h_align='right',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        
        scroll = sw(
            parent=w,
            size=(440, 200),
            position=(20, 50)  # موقعیت پایین‌تر به خاطر اضافه شدن ردیف جدید
        )
        
        item_count = len(s.max_prices)
        scroll_height = max(200, item_count * 45)
        
        scroll_content = cw(
            parent=scroll,
            size=(420, scroll_height),
            background=False
        )
        
        if not s.max_prices:
            tw(
                parent=scroll_content,
                text='No items configured yet',
                position=(210, 100),
                h_align='center',
                color=(0.7, 0.7, 0.7)
            )
            tw(
                parent=scroll_content,
                text='Click "ADD NEW ITEM" to get started',
                position=(210, 80),
                h_align='center',
                scale=0.6,
                color=(0.6, 0.6, 0.6)
            )
        else:
            y_pos = scroll_height - 35
            for item, max_price in s.max_prices.items():
                item_bg = cw(
                    parent=scroll_content,
                    size=(400, 35),
                    position=(10, y_pos),
                    color=(0.25, 0.25, 0.3)
                )
                
                tw(
                    parent=item_bg,
                    text=item,
                    position=(15, 5),
                    h_align='left',
                    v_align='center',
                    scale=0.8,
                    color=(0.5, 1, 0)
                )
                
                tw(
                    parent=item_bg,
                    text=f'Max: {max_price}',
                    position=(180, 5),
                    h_align='left',
                    v_align='center',
                    scale=0.7,
                    color=(0.8, 1, 0.5)
                )
                
                bw(
                    parent=item_bg,
                    position=(320, 2),
                    size=(100, 50),
                    label='DELETE',
                    color=(0.8, 0.2, 0.2),
                    textcolor=(1, 1, 1),
                    scale=0.6,
                    on_activate_call=CallPartial(s.delete_item, item, w)
                )
                
                y_pos -= 40
        
        # دکمه‌های پایین
        bw(
            parent=w,
            position=(50, 15),
            size=(150, 30),
            label='ADD NEW ITEM',
            color=(0.2, 0.7, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.show_add_item_dialog, w)
        )
        
        bw(
            parent=w,
            position=(220, 15),
            size=(150, 30),
            label='SET MAX TOTAL PRICE',
            color=(1, 0.8, 0.2),
            textcolor=(0, 0, 0),
            on_activate_call=CallPartial(s.show_max_total_price_dialog, w)
        )
    
    # متد جدید برای نمایش پنل تنظیم حداکثر قیمت کل
    def show_max_total_price_dialog(s, current_window=None):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(400, 200)
        
        tw(
            parent=w,
            text='SET MAX TOTAL PRICE',
            position=(200, 170),
            h_align='center',
            scale=1.1,
            color=(0, 0.8, 1)
        )
        
        tw(
            parent=w,
            text='Enter max total price for any purchase:',
            position=(200, 140),
            h_align='center',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        
        # فیلد ورودی عدد
        price_text = tw(
            parent=w,
            text=str(s.max_total_price) if s.max_total_price is not None else '',
            position=(200, 110),
            size=(300, 25),
            editable=True,
            color=(1, 1, 1),
            max_chars=10,
            h_align='center'
        )
        
        bw(
            parent=w,
            position=(100, 60),
            size=(120, 35),
            label='SAVE',
            color=(0.2, 0.7, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.save_max_total_price, price_text, w)
        )
        
        bw(
            parent=w,
            position=(220, 60),
            size=(120, 35),
            label='CLEAR',
            color=(0.7, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.clear_max_total_price, w)
        )
    
    def save_max_total_price(s, price_text, window):
        try:
            price_str = tw(query=price_text).strip()
            if not price_str:
                s.max_total_price = None
            else:
                price = int(price_str)
                if price <= 0:
                    raise ValueError("Price must be positive")
                s.max_total_price = price

            APP.config['singl_buyer_max_total_price'] = s.max_total_price
            APP.config.commit()

            push(f"Max total price set to: {s.max_total_price}", color=(0,1,0))
            gs('cashRegister').play()

            s.close_window(window)
            s.show_item_settings()  # برگشت به صفحه آیتم ستینگ

        except Exception as e:
            push(f"Invalid price: {e}", color=(1,0,0))
    
    def clear_max_total_price(s, window):
        s.max_total_price = None
        APP.config['singl_buyer_max_total_price'] = s.max_total_price
        APP.config.commit()

        push("Max total price cleared", color=(0,1,0))
        gs('gunCocking').play()

        s.close_window(window)
        s.show_item_settings()
    
    def toggle_plugin_from_settings(s, current_window):
        s.toggle_plugin()
        s.refresh_item_settings(current_window)
    
    def toggle_anti_recoil_from_settings(s, current_window):
        s.toggle_anti_recoil()
        s.refresh_item_settings(current_window)
    
    def refresh_item_settings(s, current_window=None):
        if current_window:
            s.close_window(current_window)
        s.show_item_settings()
    
    def show_add_item_dialog(s, parent_window=None):
        w = s.create_window(400, 250)
        
        tw(
            parent=w,
            text='ADD NEW ITEM',
            position=(200, 220),
            h_align='center',
            scale=1.1,
            color=(0, 0.8, 1)
        )
        
        tw(
            parent=w,
            text='Item Name:',
            position=(50, 180),
            color=(0.8, 0.8, 0.8),
            scale=0.8
        )
        item_text = tw(
            parent=w,
            text='',
            position=(50, 155),
            size=(300, 25),
            editable=True,
            color=(1, 1, 1),
            max_chars=20
        )
        
        tw(
            parent=w,
            text='Max Price per item:',
            position=(50, 125),
            color=(0.8, 0.8, 0.8),
            scale=0.8
        )
        price_text = tw(
            parent=w,
            text='',
            position=(50, 100),
            size=(300, 25),
            editable=True,
            color=(1, 1, 1),
            max_chars=6
        )
        
        bw(
            parent=w,
            position=(70, 50),
            size=(120, 35),
            label='SAVE',
            color=(0.2, 0.7, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.save_item, item_text, price_text, w, parent_window)
        )
        
        bw(
            parent=w,
            position=(210, 50),
            size=(120, 35),
            label='CANCEL',
            color=(0.7, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.close_window, w)
        )
    
    def save_item(s, item_text, price_text, window, parent_window=None):
        item_name = tw(query=item_text).strip()
        try:
            max_price = int(tw(query=price_text))
            if max_price <= 0:
                raise ValueError("Price must be positive")
        except:
            push('Invalid price! Enter a positive number.', color=(1,0,0))
            return
        
        if not item_name:
            push('Item name required!', color=(1,0,0))
            return
        
        s.max_prices[item_name] = max_price
        APP.config['singl_buyer_max_prices'] = s.max_prices
        APP.config.commit()
        
        push(f'Added: {item_name} - max {max_price}', color=(0,1,0))
        gs('cashRegister').play()
        
        s.close_window(window)
        if parent_window:
            s.show_item_settings(parent_window)
        else:
            s.show_item_settings()
    
    def delete_item(s, item, parent_window=None):
        if item in s.max_prices:
            del s.max_prices[item]
            APP.config['singl_buyer_max_prices'] = s.max_prices
            APP.config.commit()
            push(f'Deleted: {item}', color=(0,1,0))
            gs('gunCocking').play()
            
            if parent_window:
                s.show_item_settings(parent_window)
            else:
                s.show_item_settings()
    
    def show_backup_restore(s, current_window=None):
        if current_window:
            s.close_window(current_window)
            
        w = s.create_window(480, 380)
        
        tw(
            parent=w,
            text='BACKUP & RESTORE',
            position=(220, 350),
            h_align='center',
            scale=1.1,
            color=(0, 0.4, 1)
        )
        
        bw(
            parent=w,
            position=(10, 300),
            size=(200, 40),
            label='CREATE BACKUP',
            color=(0.2, 0.5, 0.8),
            textcolor=(1, 1, 1),
            on_activate_call=CallStrict(s.create_backup)
        )
        
        bw(
            parent=w,
            position=(260, 300),
            size=(200, 40),
            label='RESTORE FROM BACKUP',
            color=(0.8, 0.5, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallStrict(s.show_restore_list)
        )
        
        bw(
            parent=w,
            position=(140, 10),
            size=(200, 40),
            label='RESET ALL SETTINGS',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallStrict(s.show_reset_confirmation)
        )
        
        tw(
            parent=w,
            text='Available Backups:',
            position=(80, 260),
            h_align='center',
            scale=0.8,
            color=(0.8, 0.8, 0.8)
        )
        
        scroll = sw(
            parent=w,
            size=(440, 120),
            position=(20, 140)
        )
        
        backup_files = s.get_backup_files()
        scroll_height = max(120, len(backup_files) * 30)
        
        scroll_content = cw(
            parent=scroll,
            size=(420, scroll_height),
            background=False
        )
        
        if not backup_files:
            tw(
                parent=scroll_content,
                text='No backup files found',
                position=(210, 60),
                h_align='center',
                color=(0.7, 0.7, 0.7)
            )
        else:
            y_pos = scroll_height - 20
            for backup_file in backup_files:
                file_bg = cw(
                    parent=scroll_content,
                    size=(400, 25),
                    position=(10, y_pos),
                    color=(0.2, 0.2, 0.25)
                )
                
                tw(
                    parent=file_bg,
                    text=backup_file,
                    position=(10, 0),
                    h_align='left',
                    v_align='center',
                    scale=0.7,
                    color=(0.8, 0.8, 1)
                )
                
                y_pos -= 30
    
    def create_backup(s):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"singl_buyer_backup_{timestamp}.json"
            filepath = os.path.join(s.backup_dir, filename)
            
            backup_data = {
                'max_prices': s.max_prices,
                'max_total_price': s.max_total_price,  # اضافه شده
                'timestamp': timestamp,
                'version': '1.0'
            }
            
            with open(filepath, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            push(f"Backup created: {filename}", color=(0, 1, 0))
            gs('cashRegister').play()
            
            s.show_backup_restore()
            
        except Exception as e:
            push(f"Backup failed: {str(e)}", color=(1, 0, 0))
    
    def get_backup_files(s):
        try:
            files = []
            for file in os.listdir(s.backup_dir):
                if file.endswith('.json'):
                    files.append(file)
            return sorted(files, reverse=True)
        except:
            return []
    
    def show_restore_list(s):
        w = s.create_window(480, 380)
        
        tw(
            parent=w,
            text='SELECT BACKUP TO RESTORE',
            position=(220, 350),
            h_align='center',
            scale=1.1,
            color=(0, 0.8, 1)
        )
        
        scroll = sw(
            parent=w,
            size=(440, 280),
            position=(20, 60)
        )
        
        backup_files = s.get_backup_files()
        scroll_height = max(280, len(backup_files) * 50)
        
        scroll_content = cw(
            parent=scroll,
            size=(420, scroll_height),
            background=False
        )
        
        if not backup_files:
            tw(
                parent=scroll_content,
                text='No backup files found',
                position=(210, 140),
                h_align='center',
                color=(0.7, 0.7, 0.7)
            )
        else:
            y_pos = scroll_height - 35
            for backup_file in backup_files:
                file_bg = cw(
                    parent=scroll_content,
                    size=(400, 40),
                    position=(10, y_pos),
                    color=(0.25, 0.25, 0.3)
                )
                
                tw(
                    parent=file_bg,
                    text=backup_file,
                    position=(-3, 4),
                    h_align='left',
                    v_align='center',
                    scale=0.7,
                    color=(0.8, 1, 0.8)
                )
                
                bw(
                    parent=file_bg,
                    position=(350, 5),
                    size=(100, 50),
                    label='RESTORE',
                    color=(0.2, 0.7, 0.2),
                    textcolor=(1, 1, 1),
                    scale=0.6,
                    on_activate_call=CallPartial(s.restore_backup, backup_file)
                )
                
                y_pos -= 45
    
    def restore_backup(s, filename):
        try:
            filepath = os.path.join(s.backup_dir, filename)
            
            with open(filepath, 'r') as f:
                backup_data = json.load(f)
            
            s.max_prices = backup_data.get('max_prices', {})
            s.max_total_price = backup_data.get('max_total_price', None)  # اضافه شده
            
            APP.config['singl_buyer_max_prices'] = s.max_prices
            APP.config['singl_buyer_max_total_price'] = s.max_total_price
            APP.config.commit()
            
            push(f"Settings restored from: {filename}", color=(0, 1, 0))
            gs('cashRegister').play()
            
            s.show_main_panel()
            
        except Exception as e:
            push(f"Restore failed: {str(e)}", color=(1, 0, 0))
    
    def show_reset_confirmation(s):
        w = s.create_window(400, 200)
        
        tw(
            parent=w,
            text='RESET CONFIRMATION',
            position=(180, 170),
            h_align='center',
            scale=1.0,
            color=(1, 0.5, 0)
        )
        
        tw(
            parent=w,
            text='Are you sure you want to reset all settings?',
            position=(180, 140),
            h_align='center',
            scale=0.7,
            color=(1, 1, 1)
        )
        
        tw(
            parent=w,
            text='This action cannot be undone!',
            position=(180, 120),
            h_align='center',
            scale=0.6,
            color=(1, 0.8, 0.8)
        )

        tw(
            parent=w,
            text='Back ups are not deleted*',
            position=(180, 10),
            h_align='center',
            scale=0.8,
            color=(0, 0.8, 0.8)
        )

        tw(
            parent=w,
            text='بک آپ ها حذف نمي شوند*',
            position=(180, 30),
            h_align='center',
            scale=0.8,
            color=(0, 0.8, 0.8)
        )
        
        bw(
            parent=w,
            position=(80, 70),
            size=(120, 35),
            label='RESET',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.reset_settings, w)
        )
        
        bw(
            parent=w,
            position=(220, 70),
            size=(120, 35),
            label='CANCEL',
            color=(0.4, 0.4, 0.4),
            textcolor=(1, 1, 1),
            on_activate_call=CallPartial(s.close_window, w)
        )
    
    def reset_settings(s, window):
        s.max_prices = {}
        s.max_total_price = None  # اضافه شده
        
        APP.config['singl_buyer_max_prices'] = s.max_prices
        APP.config['singl_buyer_max_total_price'] = s.max_total_price
        APP.config.commit()
        
        s.close_window(window)
        push("All settings have been reset", color=(1, 0.5, 0))
        gs('gunCocking').play()
        
        s.show_main_panel()
    
    def open_support(s):
        open_url('https://t.me/Amiry_11228')
        push('Opening Support...', color=(0, 1, 1))
    
    def open_channel(s):
        open_url('https://t.me/SinglMod')
        push('Opening Channel...', color=(0, 1, 1))
    
    def ear(s):
        if not s.enabled:
            teck(s.listening_speed, s.ear)
            return
            
        z = GCM()
        teck(s.listening_speed, s.ear)
        
        if z == s.z: 
            return
            
        s.z = z
        v = z[-1]
        
        parts = v.split(': ', 1)
        if len(parts) < 2:
            return
            
        f, m = parts

        current_time = time.time()

        purchase_patterns = [
            r'💳Buy < (\d+) (.+?) > for ([\d,]+) coins\? Ok=1',
            r'Buy < (\d+) (.+?) > for ([\d,]+) coins\? Ok=1',
            r'💳Buy (\d+) (.+?) for ([\d,]+) coins\? Ok=1',
            r'Buy (\d+) (.+?) for ([\d,]+) coins\? Ok=1'
        ]

        purchase_detected = False
        purchase_data = None
        
        for pattern in purchase_patterns:
            match = re.search(pattern, m)
            if match:
                n_str, item_full, price_str = match.groups()
                n = int(n_str)

                price = int(price_str.replace(',', ''))
                price_per_item = price / n
                
                item_base = item_full.split(' (')[0].strip()
                purchase_data = (n, item_base, price, price_per_item)
                purchase_detected = True
                break
     
        if purchase_detected and s.pending_purchase:
            n, item_base, price, price_per_item = purchase_data
            
            # بررسی حداکثر قیمت کل (اضافه شده)
            if s.max_total_price is not None and price > s.max_total_price:
                push(f"قیمت کل بیشتر از حداکثر مجاز است: {price} > {s.max_total_price}", color=(1, 1, 0))
                gs('error').play()
                if s.anti_recoil:
                    CM('Cancel | Singl_buyer')
                s.pending_purchase = False
                return
            
            item_found = False
            should_buy = False
            max_price_value = 0
            
            for configured_item, max_price in s.max_prices.items():
                if configured_item.lower() in item_base.lower():
                    item_found = True
                    max_price_value = max_price
                    if price_per_item <= max_price:
                        should_buy = True
                    break
            
            if item_found:
                if should_buy:
                    CM('1')
                    push(f"Auto-buy: {item_base} at {int(price_per_item)} each", color=(0,1,0))
                    gs('cashRegister').play()
                else:
                    if s.anti_recoil:
                        CM('Cancel | Singl_buyer')
                        push(f"Cancelled: {item_base} at {int(price_per_item)} > {max_price_value}", color=(1,0.5,0))
                        gs('error').play()
                    else:
                        push(f"Too expensive: {item_base} at {int(price_per_item)} > {max_price_value}", color=(1,0.5,0))
            else:
                push(f"No price set for: {item_base}", color=(1,0.5,0))
            
            s.pending_purchase = False
        
        pattern = r's\d+'
        matches = re.findall(pattern, m, re.IGNORECASE)
        
        if matches:
            for match in matches:
                response_text = f"b {match.lower()}"
                
                if match in s.last_triggered:
                    time_since_last = current_time - s.last_triggered[match]
                    if time_since_last < s.cooldown:
                        continue
                
                s.last_triggered[match] = current_time
                
                CM(response_text)
                s.pending_purchase = True
                
                push(f"Detected: {match}", color=(0, 0.8, 0.8))
                gs('dingSmallHigh').play()