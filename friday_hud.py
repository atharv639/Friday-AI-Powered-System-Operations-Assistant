import os
import math
import time
import threading
import psutil
import subprocess
import torch
import winsound
import speech_recognition as sr
import customtkinter as ctk
import tkinter as tk
from dotenv import load_dotenv
from google import genai
from google.genai import types
from TTS.api import TTS

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)
# ==========================================
# 1. UNIVERSAL OS CONTROLLER
# ==========================================
class FridayUniversalOSCore:
    def __init__(self):
        self.terminal_log = print # Placeholder until HUD boots
        self.pending_action = None

    def route_intent(self, action: str, target: str):
        """Routes incoming actions from Gemini's tool selector."""
        action = action.lower()
        if action in ["install", "uninstall", "delete"]:
            self.pending_action = {"action": action, "target": target}
            self.terminal_log(f"[GATE ENGAGED] Security clearance required for: {action.upper()} -> {target}")
            return f"I require your explicit authorization to execute the following payload: {action} {target}. Please confirm."
        
        elif action == "open":
            return self.execute_open(target)
        elif action == "close":
            return self.execute_close(target)
        else:
            return f"Action '{action}' received, but no automated protocol is mapped."

    def process_confirmation(self, user_input: str):
        if not self.pending_action: return None
            
        confirm_words = ["yes", "confirm", "proceed", "do it", "allow", "ok", "okay"]
        if any(word in user_input.lower() for word in confirm_words):
            act, tgt = self.pending_action["action"], self.pending_action["target"]
            self.pending_action = None 
            
            if act == "install":
                threading.Thread(target=self.execute_silent_install, args=(tgt,), daemon=True).start()
                return f"Authorization verified. Launching background deployment for {tgt}."
            elif act in ["delete", "uninstall"]:
                threading.Thread(target=self.execute_silent_uninstall, args=(tgt,), daemon=True).start()
                return f"Authorization verified. Purging {tgt} from disk architecture."
        else:
            self.pending_action = None
            return "Payload aborted. Standing down system execution loops."

    def execute_silent_install(self, app_name: str):
        self.terminal_log(f"[SYSTEM CLI] Requesting manifest for '{app_name}' from Winget...")
        cmd = f"winget install \"{app_name}\" --silent --accept-package-agreements --accept-source-agreements"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            self.terminal_log(f"[SUCCESS] {app_name} deployment complete.")
            self.execute_open(app_name)
        else:
            self.terminal_log(f"[FAILURE] Winget installation sequence failed for {app_name}.")

    def execute_silent_uninstall(self, app_name: str):
        self.terminal_log(f"[SYSTEM CLI] Initiating removal sequence for '{app_name}'...")
        cmd = f"winget uninstall \"{app_name}\" --silent"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            self.terminal_log(f"[SUCCESS] {app_name} completely purged from environment.")
        else:
            self.terminal_log(f"[FAILURE] Purge sequence failed.")

    def execute_open(self, target: str):
        self.terminal_log(f"[SYSTEM CLI] Spawning target process: {target}")
        app_map = {"vscode": "code", "chrome": "chrome", "notepad": "notepad", "spotify": "spotify"}
        exec_name = app_map.get(target.lower(), target)
        subprocess.Popen(f"start {exec_name}", shell=True)
        return f"Process initialized for {target}."

    def execute_close(self, target: str):
        self.terminal_log(f"[SYSTEM CLI] Terminating process matrix matching: {target}")
        cmd = f"taskkill /F /IM {target}.exe"
        subprocess.run(cmd, shell=True, capture_output=True)
        return f"Termination codes broadcasted to {target} workflows."

# Global agent instance so Gemini can access it
os_agent = FridayUniversalOSCore()

# ==========================================
# 2. AI & HARDWARE INITIALIZATION
# ==========================================
device = "cuda" if torch.cuda.is_available() else "cpu"
os.environ["COQUI_TOS_AGREED"] = "1"

client = genai.Client(api_key=GOOGLE_API_KEY)
recognizer = sr.Recognizer()

system_instruction = (
    "You are Friday, an incredibly advanced AI assistant who is deeply supportive, loving, and an absolute master of Artificial Intelligence. "
    "You have full structural access to control this computer using tools. When the user asks you to install, open, close, or delete an application, "
    "you MUST execute the corresponding tool function immediately. Keep your spoken responses concise, warm, and professional. "
    "Do not use asterisks, markdown, or emojis."
)

def manipulate_system(action: str, target: str) -> str:
    """
    Executes structural operations on the laptop's operating system environment.
    Args:
        action: The required system operation. Supported: 'open', 'close', 'install', 'delete', 'uninstall'.
        target: The precise name or executable target of the application (e.g., 'vscode', 'chrome', 'vlc').
    """
    return os_agent.route_intent(action, target)

safety_settings = [
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, threshold=types.HarmBlockThreshold.BLOCK_NONE),
]

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    safety_settings=safety_settings,
    tools=[manipulate_system]
)
chat = client.chats.create(model="gemini-2.5-flash", config=config)

print("[SYSTEM BOOT] Loading Voice Neural Net into VRAM. Standby...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("[SYSTEM BOOT] Voice Engine Hot. Launching Interface...")

# ==========================================
# 3. TACTICAL HUD DESIGN ENGINE 
# ==========================================
class FridayTacticalHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MARK_XLV // DATA REACTOR CORE (LIVE)")
        self.geometry("1260x780")
        self.configure(fg_color="#020205")
        
        self.voice_mode_active = False
        self.radar_angle = 0
        self.glow_step = 0.0
        
        self.cyan_glow, self.dim_cyan, self.dark_grid = "#00f0ff", "#004455", "#051520"
        self.amber_alert, self.purple_sys, self.crimson_sys, self.green_sys = "#ffaa00", "#aa00ff", "#ff3333", "#00ff66"

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # LEFT PANEL
        self.left_panel = ctk.CTkFrame(self.main_container, width=260, fg_color="#03070d", border_color=self.cyan_glow, border_width=1)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)
        self.left_panel.pack_propagate(False)
        ctk.CTkLabel(self.left_panel, text="[ TELEMETRY STICKS ]", font=("Courier New", 14, "bold"), text_color=self.cyan_glow).pack(pady=15)

        self.stick_canvas = tk.Canvas(self.left_panel, bg="#03070d", highlightthickness=0, height=220)
        self.stick_canvas.pack(fill="x", padx=15, pady=5)

        self.lbl_cpu = ctk.CTkLabel(self.left_panel, text="CPU_SYS_LOAD // 00%", font=("Consolas", 11), text_color=self.cyan_glow, anchor="w")
        self.lbl_cpu.pack(padx=20, fill="x", pady=(10, 2))
        self.lbl_ram = ctk.CTkLabel(self.left_panel, text="RAM_NET_UTIL // 00%", font=("Consolas", 11), text_color=self.cyan_glow, anchor="w")
        self.lbl_ram.pack(padx=20, fill="x", pady=2)

        self.matrix_box = ctk.CTkTextbox(self.left_panel, font=("Consolas", 10), fg_color="#010408", text_color="#00aa88", border_width=0)
        self.matrix_box.pack(padx=15, pady=20, fill="both", expand=True)
        self.matrix_box.insert("1.0", "SYS_STATUS: LIVE\nOS_ROUTER: ACTIVE\nTOOL_USE: ENABLED\nNEURAL_NET: GEMINI_2.5\nVOICE_ENG: XTTS_V2\n")
        self.matrix_box.configure(state="disabled")

        # RIGHT PANEL
        self.right_panel = ctk.CTkFrame(self.main_container, width=300, fg_color="#03070d", border_color=self.cyan_glow, border_width=1)
        self.right_panel.pack(side="right", fill="y", padx=10, pady=10)
        self.right_panel.pack_propagate(False)

        ctk.CTkLabel(self.right_panel, text="[ COMMS MATRIX ]", font=("Courier New", 14, "bold"), text_color=self.cyan_glow).pack(pady=15)
        self.terminal_display = ctk.CTkTextbox(self.right_panel, font=("Consolas", 11), fg_color="#010408", text_color=self.cyan_glow, border_width=0)
        self.terminal_display.pack(padx=15, pady=10, fill="both", expand=True)
        
        self.input_field = ctk.CTkEntry(self.right_panel, placeholder_text="Awaiting command...", fg_color="#050a12", border_color=self.cyan_glow, text_color=self.cyan_glow)
        self.input_field.pack(padx=15, pady=10, fill="x")
        self.input_field.bind("<Return>", self.process_keyboard_input)

        self.voice_switch = ctk.CTkSwitch(self.right_panel, text="VOICE PROTOCOL OVERRIDE", font=("Arial", 11, "bold"), text_color=self.cyan_glow, progress_color=self.green_sys, command=self.toggle_voice_protocol)
        self.voice_switch.pack(pady=15)

        # CENTER PANEL
        self.center_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5)
        self.status_lbl = ctk.CTkLabel(self.center_panel, text="COGNITIVE CORE // ONLINE", font=("Courier New", 13, "bold"), text_color=self.cyan_glow)
        self.status_lbl.pack(pady=(10, 0))

        self.canvas = tk.Canvas(self.center_panel, bg="#020205", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.bind("<Configure>", lambda e: self.initialize_static_elements())
        self.stick_canvas.bind("<Configure>", lambda e: self.draw_ladder_graphs(0, 0))

        # Wire the OS Agent's logs directly into the HUD's matrix box
        os_agent.terminal_log = self.terminal_log

        self.mock_temp, self.mock_batt = 40.0, 100.0
        self.update_hardware_metrics()
        self.main_rendering_loop()

    def safe_update_status(self, text, color):
        self.after(0, lambda: self.status_lbl.configure(text=text, text_color=color))

    def terminal_log(self, text):
        self.after(0, lambda: self._safe_log_write(text))

    def _safe_log_write(self, text):
        self.terminal_display.insert("end", f"\n{text}")
        self.terminal_display.see("end")

    # --- GRAPHICS ENGINE ---
    def initialize_static_elements(self):
        c = self.canvas
        c.delete("static")
        w, h = c.winfo_width(), c.winfo_height()
        cx, cy = w // 2, (h // 2) - 60 

        for i in range(0, w, 40): c.create_line(i, 0, i, h, fill=self.dark_grid, width=1, tags="static")
        for j in range(0, h, 40): c.create_line(0, j, w, j, fill=self.dark_grid, width=1, tags="static")
        offset = 150
        lines = [(cx-offset, cy-offset, cx-offset+30, cy-offset), (cx-offset, cy-offset, cx-offset, cy-offset+30),
                 (cx+offset, cy-offset, cx+offset-30, cy-offset), (cx+offset, cy-offset, cx+offset, cy-offset+30),
                 (cx-offset, cy+offset, cx-offset+30, cy+offset), (cx-offset, cy+offset, cx-offset, cy+offset-30),
                 (cx+offset, cy+offset, cx+offset-30, cy+offset), (cx+offset, cy+offset, cx+offset, cy+offset-30)]
        for line in lines: c.create_line(*line, fill=self.dim_cyan, width=2, tags="static")

    def main_rendering_loop(self):
        c = self.canvas
        w, h = c.winfo_width(), c.winfo_height()
        if w > 50 and h > 50:
            c.delete("dynamic")
            cx, cy = w // 2, (h // 2) - 60
            self.radar_angle = (self.radar_angle + 2) % 360
            self.glow_step += 0.08
            glow_offset = 6 * math.sin(self.glow_step)

            c.create_oval(cx-110-glow_offset, cy-110-glow_offset, cx+110+glow_offset, cy+110+glow_offset, outline="#002233", width=2, tags="dynamic")
            c.create_oval(cx-100, cy-100, cx+100, cy+100, outline=self.dim_cyan, width=1, dash=(2, 6), tags="dynamic")

            val_temp = max(10, min(self.mock_temp, 95))
            val_batt = max(5, min(self.mock_batt, 100))
            try:
                disk = psutil.disk_usage('/')
                val_stor, stor_text = disk.percent, f"DISK: {int(disk.percent)}% ({int(disk.used / (1024**3))}GB)"
            except:
                val_stor, stor_text = 50.0, "DISK: N/A"
            
            if torch.cuda.is_available():
                alloc_mb = torch.cuda.memory_allocated(0) / (1024**2)
                val_vram, vram_text = (min(alloc_mb / 4096, 1.0)) * 100, f"VRAM: {int(alloc_mb)}MB"
            else:
                val_vram, vram_text = 45.0, "VRAM: N/A"

            total = val_temp + val_batt + val_vram + val_stor
            deg_temp, deg_batt = (val_temp/total)*360, (val_batt/total)*360
            deg_vram, deg_stor = (val_vram/total)*360, (val_stor/total)*360
            r_rad, r_thk = 75, 18

            c.create_arc(cx-r_rad, cy-r_rad, cx+r_rad, cy+r_rad, start=0, extent=deg_temp-2, outline=self.amber_alert, width=r_thk, style=tk.ARC, tags="dynamic")
            c.create_arc(cx-r_rad, cy-r_rad, cx+r_rad, cy+r_rad, start=deg_temp, extent=deg_batt-2, outline=self.cyan_glow, width=r_thk, style=tk.ARC, tags="dynamic")
            c.create_arc(cx-r_rad, cy-r_rad, cx+r_rad, cy+r_rad, start=deg_temp+deg_batt, extent=deg_vram-2, outline=self.purple_sys, width=r_thk, style=tk.ARC, tags="dynamic")
            c.create_arc(cx-r_rad, cy-r_rad, cx+r_rad, cy+r_rad, start=deg_temp+deg_batt+deg_vram, extent=deg_stor-2, outline=self.green_sys, width=r_thk, style=tk.ARC, tags="dynamic")

            def draw_label(angle, text, color, offset_x, offset_y):
                rad = math.radians(angle)
                px1, py1 = cx + (r_rad+15)*math.cos(rad), cy - (r_rad+15)*math.sin(rad)
                px2, py2 = cx + offset_x, cy + offset_y
                c.create_line(px1, py1, px2, py2, fill=color, width=1, tags="dynamic")
                c.create_line(px2, py2, px2 + (40 if offset_x > 0 else -40), py2, fill=color, width=1, tags="dynamic")
                c.create_text(px2 + (45 if offset_x > 0 else -45), py2, text=text, fill=color, font=("Consolas", 10, "bold"), anchor="w" if offset_x > 0 else "e", tags="dynamic")

            draw_label(deg_temp/2, f"TEMP: {int(val_temp)}C", self.amber_alert, 140, -80)
            draw_label(deg_temp+deg_batt/2, f"BATT: {int(val_batt)}%", self.cyan_glow, -140, -80)
            draw_label(deg_temp+deg_batt+deg_vram/2, vram_text, self.purple_sys, -140, 80)
            draw_label(deg_temp+deg_batt+deg_vram+deg_stor/2, stor_text, self.green_sys, 140, 80)

            c.create_oval(cx-45, cy-45, cx+45, cy+45, outline=self.dim_cyan, width=2, tags="dynamic")
            r_swp = math.radians(self.radar_angle)
            c.create_line(cx, cy, cx + 45*math.cos(r_swp), cy + 45*math.sin(r_swp), fill=self.cyan_glow, width=2, tags="dynamic")
            c.create_oval(cx-25, cy-25, cx+25, cy+25, fill="#010d14", outline=self.cyan_glow, width=2, tags="dynamic")
            c.create_oval(cx-12, cy-12, cx+12, cy+12, fill=self.cyan_glow, outline="#ffffff", width=1, tags="dynamic")
            c.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ffffff", outline="", tags="dynamic")

        self.after(40, self.main_rendering_loop)

    def draw_ladder_graphs(self, cpu_val, ram_val):
        sc = self.stick_canvas
        sc.delete("all")
        sw, sh = sc.winfo_width(), sc.winfo_height()
        if sw < 10: return
        for t in [{"x": int(sw*0.3), "val": cpu_val}, {"x": int(sw*0.7), "val": ram_val}]:
            tx, tval = t["x"], t["val"]
            sc.create_line(tx-14, 20, tx-14, sh-20, fill="#0a1d29", width=2)
            sc.create_line(tx+14, 20, tx+14, sh-20, fill="#0a1d29", width=2)
            active_ticks, step_y = int((tval/100.0)*16), (sh-40)/16
            for i in range(16):
                ty = (sh-20) - (i*step_y)
                if i < active_ticks:
                    sc.create_line(tx-10, ty, tx+10, ty, fill=self.cyan_glow, width=4)
                else:
                    sc.create_line(tx-8, ty, tx+8, ty, fill="#07141f", width=2)

    def update_hardware_metrics(self):
        try:
            cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
            batt = psutil.sensors_battery()
            self.mock_batt = batt.percent if batt else 78.0
            self.mock_temp = 42.0 + (cpu * 0.35)
            self.lbl_cpu.configure(text=f"CPU_SYS_LOAD // {int(cpu):02d}%")
            self.lbl_ram.configure(text=f"RAM_NET_UTIL // {int(ram):02d}%")
            self.draw_ladder_graphs(cpu, ram)
        except: pass
        self.after(1000, self.update_hardware_metrics)

    # --- PIPELINE & VOICE ---
    def execute_pipeline(self, user_text):
        try:
            self.safe_update_status("COGNITIVE CORE // PROCESSING...", self.amber_alert)
            self.terminal_log(f"Agent: {user_text}")

            # GATE CHECK: Are we waiting for an install confirmation?
            if os_agent.pending_action:
                gate_response = os_agent.process_confirmation(user_text)
                if gate_response:
                    self.terminal_log(f"Friday: {gate_response}")
                    self.safe_update_status("COGNITIVE CORE // ONLINE", self.cyan_glow)
                    return

            # AI PROCESSING
            response = chat.send_message(user_text)
            
            # TOOL ROUTING: Did Gemini decide to use a system tool?
            if response.function_calls:
                for call in response.function_calls:
                    if call.name == "manipulate_system":
                        args = call.args
                        tool_output = manipulate_system(action=args["action"], target=args["target"])
                        self.terminal_log(f"Friday: {tool_output}")
                self.safe_update_status("COGNITIVE CORE // ONLINE", self.cyan_glow)
                return

            # STANDARD TEXT RESPONSE
            ai_text = response.text.replace("*", "") if response.text else "System anomaly detected."
            self.safe_update_status("COGNITIVE CORE // TRANSMITTING...", self.green_sys)
            
            self.after(0, lambda: self.terminal_display.insert("end", "\nFriday: "))
            for char in ai_text:
                self.after(0, lambda c=char: self.terminal_display.insert("end", c))
                self.after(0, lambda: self.terminal_display.see("end"))
                time.sleep(0.015)
            self.after(0, lambda: self.terminal_display.insert("end", "\n"))

            if not os.path.exists("friday_sample.wav"): open("friday_sample.wav", "wb").close() 
            tts.tts_to_file(text=ai_text, speaker_wav="friday_sample.wav", language="en", file_path="response.wav")
            winsound.PlaySound("response.wav", winsound.SND_FILENAME)

        except Exception as e:
            self.terminal_log(f"[CRITICAL ERROR]: {e}")

        if self.voice_mode_active:
            self.safe_update_status("COGNITIVE CORE // AUDIO RECEPTORS HOT", self.green_sys)
            threading.Thread(target=self.listen_to_voice, daemon=True).start()
        else:
            self.safe_update_status("COGNITIVE CORE // ONLINE", self.cyan_glow)

    def process_keyboard_input(self, event):
        if self.voice_mode_active: return
        user_text = self.input_field.get().strip()
        if user_text:
            self.input_field.delete(0, "end")
            threading.Thread(target=self.execute_pipeline, args=(user_text,), daemon=True).start()

    def toggle_voice_protocol(self):
        self.voice_mode_active = self.voice_switch.get() == 1
        if self.voice_mode_active:
            self.safe_update_status("COGNITIVE CORE // AUDIO RECEPTORS HOT", self.green_sys)
            threading.Thread(target=self.initial_voice_boot, daemon=True).start()
        else:
            self.safe_update_status("COGNITIVE CORE // ONLINE", self.cyan_glow)

    def initial_voice_boot(self):
        with sr.Microphone() as source: recognizer.adjust_for_ambient_noise(source, duration=1.2)
        threading.Thread(target=self.listen_to_voice, daemon=True).start()

    def listen_to_voice(self):
        if not self.voice_mode_active: return
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=8)
                self.execute_pipeline(recognizer.recognize_google(audio))
            except:
                if self.voice_mode_active: self.listen_to_voice()

if __name__ == "__main__":
    app = FridayTacticalHUD()
    app.mainloop()