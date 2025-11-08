# Singl_buyer V 1.1
# Copyright 2025
#کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
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
    Call
)
from bascenev1 import (
    get_chat_messages as GCM,
    chatmessage as CM
)
import re
import time
import json
import os
from datetime import datetime
#کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
# ba_meta require api 9
# ba_meta export babase.Plugin
class Singl_buyer(Plugin):
    
    def __init__(s):
        s.z = []
        s.last_triggered = {}
        s.cooldown = 2.0
        s.enabled = True
        s.anti_recoil = True  
        
        s.waiting_for_purchase = {}
        s.max_prices = APP.config.get('singl_buyer_max_prices', {})
        s.pending_purchase = None
        s.current_settings_window = None  
        s.current_main_window = None  
        
        s.backup_dir = "ba_data/singl_buyer_backups"
        if not os.path.exists(s.backup_dir):
            os.makedirs(s.backup_dir)
        
        teck(10, s.show_welcome_message)
        
        s.setup_ui()
        teck(5, s.ear)
 #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه   
    def show_welcome_message(s):
        push("Power by Singl | @Amiry_11228 | t.me/SinglMod | V:1.1", color=(0, 0.8, 1))
        gs('dingSmall').play()
    
    def setup_ui(s):
        from bauiv1lib import party
        
        original_init = party.PartyWindow.__init__
        
        def new_init(self, *args, **kwargs):
            result = original_init(self, *args, **kwargs)

            button_color, text_color = s.get_button_colors()
            
            button = bw(
                parent=self._root_widget,
                icon=gt('tokens3'),
                position=(self._width - 520, self._height - 560),
                size=(40, 40),
                color=button_color,
                on_activate_call=Call(s.show_main_panel)
            )
            s.ui_button = button
            
            return result
        
        party.PartyWindow.__init__ = new_init
    
    def get_button_colors(s):
        if not s.enabled:
            return (0.7, 0.1, 0.1), (1, 0.5, 0.5)
        elif s.enabled and s.anti_recoil:
            return (0.6, 0.2, 0.8), (0.9, 0.7, 1)
        else:
            return (0.1, 0.6, 0.1), (0.6, 1, 0.6)
    
    def show_main_panel(s):
        if s.current_main_window:
            s.close_window(s.current_main_window)
            
        w = s.create_window(480, 380, is_main=True)
        s.current_main_window = w
        
        tw(
            parent=w,
            text='SINGL BUYER',
            position=(220, 350),
            h_align='center',
            scale=1.3,
            color=(0, 0.8, 1)
        )
        #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
        tw(
            parent=w,
            text='Auto Buy System',
            position=(220, 325),
            h_align='center',
            scale=0.7,
            color=(0.4, 1, 0.7)
        )
        
        status_color = (0, 0.8, 0) if s.enabled else (0.8, 0, 0)
        status_text = 'ON' if s.enabled else 'OFF'
        
        s.status_button = bw(
            parent=w,
            position=(190, 290),
            size=(100, 35),
            label=status_text,
            color=status_color,
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.toggle_plugin_from_panel, w)
        )
        
        anti_recoil_color = (0.6, 0.2, 0.8) if s.anti_recoil else (0.4, 0.4, 0.4)
        anti_recoil_text = 'ANTI-RECOIL: ON' if s.anti_recoil else 'ANTI-RECOIL: OFF'
        
        s.anti_recoil_button = bw(
            parent=w,
            position=(165, 240),
            size=(150, 35),
            label=anti_recoil_text,
            color=anti_recoil_color,
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.toggle_anti_recoil_from_panel, w)
        )
        
        buttons = [
            ('Item Settings', Call(s.show_item_settings, w), (165, 190)),
            ('Backup & Restore', Call(s.show_backup_restore, w), (165, 140)),
            ('Support', s.open_support, (290, 90)),
            ('Channel', s.open_channel, (40, 90)),
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
        #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
        if not s.enabled:
            status_info = "PLUGIN DISABLED"
            info_color = (1, 0, 0)
        elif s.enabled and s.anti_recoil:
            status_info = "ACTIVE + ANTI-RECOIL"
            info_color = (0.8, 0.4, 1)
        else:
            status_info = "ACTIVE (NORMAL MODE)"
            info_color = (0, 1, 0)
        
        tw(
            parent=w,
            text=status_info,
            position=(105, 40),
            h_align='center',
            scale=0.7,
            color=info_color
        )
        
        tw(
            parent=w,
            text='Power by Singl | @Amiry_11228',
            position=(220, 15),
            h_align='center',
            scale=0.5,
            color=(0.8, 0.8, 0.5)
        )
    
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
            on_activate_call=s.create_backup
        )
        
        bw(
            parent=w,
            position=(260, 300),
            size=(200, 40),
            label='RESTORE FROM BACKUP',
            color=(0.8, 0.5, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=s.show_restore_list
        )
        
        bw(
            parent=w,
            position=(140, 10),
            size=(200, 40),
            label='RESET ALL SETTINGS',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=s.show_reset_confirmation
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
                'timestamp': timestamp,
                'version': '1.0'
            }
            #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
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
                    on_activate_call=Call(s.restore_backup, backup_file)
                )
                
                y_pos -= 45
    
    def restore_backup(s, filename):
        try:
            filepath = os.path.join(s.backup_dir, filename)
            
            with open(filepath, 'r') as f:
                backup_data = json.load(f)
            
            s.max_prices = backup_data.get('max_prices', {})
            APP.config['singl_buyer_max_prices'] = s.max_prices
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
            on_activate_call=Call(s.reset_settings, w)
        )
        
        bw(
            parent=w,
            position=(220, 70),
            size=(120, 35),
            label='CANCEL',
            color=(0.4, 0.4, 0.4),
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.close_window, w)
        )
    
    def reset_settings(s, window):
        s.max_prices = {}
        APP.config['singl_buyer_max_prices'] = s.max_prices
        APP.config.commit()
        
        s.close_window(window)
        push("All settings have been reset", color=(1, 0.5, 0))
        gs('gunCocking').play()
        
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
        #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
        s.update_main_button()
        
        status_text = "ON" if s.anti_recoil else "OFF"
        color = (0.8, 0.4, 1) if s.anti_recoil else (0.7, 0.7, 0.7)
        push(f"Anti-Recoil: {status_text}", color=color)
        gs('dingSmall' if s.anti_recoil else 'error').play()
        
        if hasattr(s, 'current_settings_window') and s.current_settings_window:
            s.refresh_item_settings()
    
    def toggle_plugin(s):
        s.enabled = not s.enabled
        status = "ON" if s.enabled else "OFF"
        color = (0, 1, 0) if s.enabled else (1, 0, 0)
        push(f"Singl_buyer: {status}", color=color)
        gs('dingSmall' if s.enabled else 'error').play()
        
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
            
        w = s.create_window(480, 380)
        s.current_settings_window = w  
        
        tw(
            parent=w,
            text='ITEM SETTINGS',
            position=(220, 350),
            h_align='center',
            scale=1.1,
            color=(0, 0.8, 1)
        )
        
        status_color = (0, 0.8, 0) if s.enabled else (0.8, 0, 0)
        status_text = 'ON' if s.enabled else 'OFF'
        
        s.item_status_button = bw(
            parent=w,
            position=(400, 320),
            size=(60, 25),
            label=status_text,
            color=status_color,
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.toggle_plugin_from_settings, w)
        )
        
        tw(
            parent=w,
            text='status:',
            position=(350, 320),
            h_align='right',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        
        anti_recoil_color = (0.6, 0.2, 0.8) if s.anti_recoil else (0.4, 0.4, 0.4)
        anti_recoil_text = 'ON' if s.anti_recoil else 'OFF'
        
        s.item_anti_recoil_button = bw(
            parent=w,
            position=(400, 290),
            size=(60, 25),
            label=anti_recoil_text,
            color=anti_recoil_color,
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.toggle_anti_recoil_from_settings, w)
        )
        
        tw(
            parent=w,
            text='anti-recoil:',
            position=(350, 290),
            h_align='right',
            scale=0.7,
            color=(0.8, 0.8, 0.8)
        )
        
        scroll = sw(
            parent=w,
            size=(440, 200),
            position=(20, 80)
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
                    on_activate_call=Call(s.delete_item, item, w)
                )
               #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه 
                y_pos -= 40
        
        bw(
            parent=w,
            position=(140, 35),
            size=(200, 30),
            label='ADD NEW ITEM',
            color=(0.2, 0.7, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.show_add_item_dialog, w)
        )
    
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
    
    def create_window(s, width=480, height=380, is_main=False):
        w = cw(
            size=(width, height),
            scale=1.0,
            transition='in_scale',
            color=(0.1, 0, 0.2),
            parent=gsw('overlay_stack')
        )
       
        if is_main:
            cw(w, on_outside_click_call=Call(s.close_window, w))
        else:
            cw(w, on_outside_click_call=Call(s.close_and_return_to_main, w))
            
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
    
    def open_support(s):
        open_url('https://t.me/Amiry_11228')
        push('Opening Support...', color=(0, 1, 1))
    
    def open_channel(s):
        open_url('https://t.me/SinglMod')
        push('Opening Channel...', color=(0, 1, 1))
    
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
            on_activate_call=Call(s.save_item, item_text, price_text, w, parent_window)
        )
        
        bw(
            parent=w,
            position=(210, 50),
            size=(120, 35),
            label='CANCEL',
            color=(0.7, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=Call(s.close_window, w)
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
    
    def ear(s):
        if not s.enabled:
            teck(0.3, s.ear)
            return
            
        z = GCM()
        teck(0.3, s.ear)
        
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
#کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه        
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
                #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
                push(f"Detected: {match}", color=(0, 0.8, 0.8))
                gs('dingSmallHigh').play()
                #کص مادر هرکي اسکي بره و از کد ها استفاده کنه و کپي کنه
