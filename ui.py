import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import os
import subprocess
import threading
import sys
from dotenv import load_dotenv

class TelegramSaverUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Auto Save Chat")
        self.root.geometry("900x700")
        
        # Load environment variables
        load_dotenv('product.env')
        
        self.process = None
        self.running = False
        self.monitor_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Title
        title = ttk.Label(
            main_frame, 
            text="📱 Telegram Auto Save Chat",
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Status Frame
        status_frame = ttk.Labelframe(main_frame, text="สถานะ", padding=15)
        status_frame.pack(fill=X, pady=(0, 10))
        
        status_content = ttk.Frame(status_frame)
        status_content.pack(fill=X)
        
        ttk.Label(status_content, text="สถานะการทำงาน:", font=("Helvetica", 10)).pack(side=LEFT)
        self.status_label = ttk.Label(
            status_content, 
            text="● หยุดทำงาน",
            font=("Helvetica", 10, "bold"),
            foreground="red"
        )
        self.status_label.pack(side=LEFT, padx=(10, 0))
        
        # Stats Frame
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill=X, pady=(10, 0))
        
        # Message counter
        counter_frame = ttk.Frame(stats_frame)
        counter_frame.pack(side=LEFT, fill=X, expand=YES)
        ttk.Label(counter_frame, text="ข้อความที่บันทึก:", font=("Helvetica", 9)).pack(side=LEFT)
        self.message_count = ttk.Label(
            counter_frame, 
            text="0",
            font=("Helvetica", 9, "bold")
        )
        self.message_count.pack(side=LEFT, padx=(5, 0))
        
        # Save location
        location_frame = ttk.Frame(stats_frame)
        location_frame.pack(side=LEFT, fill=X, expand=YES)
        ttk.Label(location_frame, text="โฟลเดอร์:", font=("Helvetica", 9)).pack(side=LEFT)
        self.save_location = ttk.Label(
            location_frame, 
            text="stock/",
            font=("Helvetica", 9, "bold")
        )
        self.save_location.pack(side=LEFT, padx=(5, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(0, 10))
        
        self.start_button = ttk.Button(
            button_frame,
            text="▶ เริ่มบันทึก",
            command=self.start_telegram,
            bootstyle=SUCCESS,
            width=20
        )
        self.start_button.pack(side=LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹ หยุดบันทึก",
            command=self.stop_telegram,
            bootstyle=DANGER,
            state=DISABLED,
            width=20
        )
        self.stop_button.pack(side=LEFT, padx=5)
        
        self.clear_button = ttk.Button(
            button_frame,
            text="🗑 ล้างล็อก",
            command=self.clear_log,
            bootstyle=WARNING,
            width=20
        )
        self.clear_button.pack(side=LEFT, padx=5)
        
        # Log Frame
        log_frame = ttk.Labelframe(main_frame, text="บันทึกการทำงาน", padding=10)
        log_frame.pack(fill=BOTH, expand=YES)
        
        # Scrolled text for logs
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=20
        )
        self.log_text.pack(fill=BOTH, expand=YES)
        
        # Configure tags for colored output
        self.log_text.tag_config("info", foreground="#2E86C1")
        self.log_text.tag_config("success", foreground="#27AE60")
        self.log_text.tag_config("error", foreground="#E74C3C")
        self.log_text.tag_config("warning", foreground="#F39C12")
        
        # Footer
        footer = ttk.Label(
            main_frame,
            text="Auto Save Telegram Chat • v1.0",
            font=("Helvetica", 8)
        )
        footer.pack(pady=(10, 0))
        
        # Initial log message
        self.log_message("โปรแกรมพร้อมใช้งาน กดปุ่ม 'เริ่มบันทึก' เพื่อเริ่มต้น", "info")
        
        # Counter
        self.msg_counter = 0
        
    def log_message(self, message, tag="info"):
        """Add message to log with timestamp and color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] ", "info")
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear log text and delete all saved files"""
        if messagebox.askyesno("ยืนยันการลบ", "ต้องการลบไฟล์บันทึกทั้งหมดในโฟลเดอร์ stock/ หรือไม่?\n\n⚠️ การดำเนินการนี้ไม่สามารถย้อนกลับได้!"):
            try:
                import shutil
                from pathlib import Path
                
                stock_path = Path('stock')
                if stock_path.exists():
                    # Count files before deletion
                    file_count = sum(1 for _ in stock_path.rglob('*') if _.is_file())
                    
                    # Delete the entire stock folder
                    shutil.rmtree(stock_path)
                    
                    # Clear log text
                    self.log_text.delete(1.0, tk.END)
                    
                    # Reset counter
                    self.msg_counter = 0
                    self.message_count.config(text="0")
                    
                    self.log_message(f"🗑️ ลบไฟล์ทั้งหมด ({file_count} ไฟล์) เรียบร้อยแล้ว", "warning")
                else:
                    self.log_text.delete(1.0, tk.END)
                    self.log_message("ไม่พบโฟลเดอร์ stock/ ล้างล็อกเรียบร้อย", "info")
                    
            except Exception as e:
                self.log_message(f"❌ เกิดข้อผิดพลาดในการลบไฟล์: {str(e)}", "error")
        
    def update_status(self, running):
        """Update status label"""
        if running:
            self.status_label.config(text="● กำลังทำงาน", foreground="green")
            self.start_button.config(state=DISABLED)
            self.stop_button.config(state=NORMAL)
        else:
            self.status_label.config(text="● หยุดทำงาน", foreground="red")
            self.start_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
            
    def update_counter(self):
        """Update message counter"""
        self.msg_counter += 1
        self.message_count.config(text=str(self.msg_counter))
        
    def start_telegram(self):
        """Start Telegram client by running run.py"""
        if self.running:
            return
            
        self.running = True
        self.update_status(True)
        self.log_message("กำลังเชื่อมต่อ Telegram...", "info")
        
        # Get Python executable path
        python_exe = sys.executable
        
        # Start run.py as subprocess with hidden window
        try:
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.process = subprocess.Popen(
                [python_exe, 'run.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
            self.monitor_thread.start()
            
            self.log_message("✅ เริ่มต้น run.py สำเร็จ!", "success")
            
        except Exception as e:
            self.log_message(f"❌ Error starting run.py: {str(e)}", "error")
            self.running = False
            self.update_status(False)
        
    def stop_telegram(self):
        """Stop Telegram client by terminating run.py process"""
        if not self.running:
            return
            
        self.running = False
        self.update_status(False)
        self.log_message("กำลังหยุดการทำงาน...", "warning")
        
        # Terminate process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.log_message("⏹ หยุดการทำงานแล้ว", "warning")
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.log_message("⏹ บังคับหยุดการทำงาน", "warning")
            except Exception as e:
                self.log_message(f"❌ Error stopping: {str(e)}", "error")
        
    def monitor_process(self):
        """Monitor the run.py process and watch for new log files"""
        import time
        from pathlib import Path
        
        # Track last modification time of log files
        last_check = time.time()
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # Check for new log entries by monitoring stock folder
                stock_path = Path('stock')
                if stock_path.exists():
                    # Find all log files modified since last check
                    for log_file in stock_path.rglob('*_log.txt'):
                        if log_file.stat().st_mtime > last_check:
                            # Read last line of log file
                            try:
                                with open(log_file, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    if lines:
                                        last_line = lines[-1].strip()
                                        # Parse log line to extract info
                                        if last_line:
                                            self.root.after(0, self.update_counter)
                                            # Show simplified message
                                            chat_name = log_file.parent.parent.name
                                            self.root.after(0, lambda msg=last_line, chat=chat_name: 
                                                self.log_message(f"💾 [{chat}] บันทึกข้อความใหม่", "success"))
                            except Exception:
                                pass
                
                last_check = time.time()
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.log_message(f"❌ Monitor error: {err}", "error"))
                break
        
        # Process ended
        if self.running:
            self.running = False
            self.root.after(0, lambda: self.update_status(False))
            self.root.after(0, lambda: self.log_message("⏹ run.py หยุดทำงาน", "warning"))
            

            
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            if messagebox.askokcancel("ออกจากโปรแกรม", "ต้องการหยุดการทำงานและออกจากโปรแกรมหรือไม่?"):
                self.stop_telegram()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = ttk.Window(themename="cosmo")
    app = TelegramSaverUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
