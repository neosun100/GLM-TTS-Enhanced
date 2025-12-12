import threading
import time
import os
import torch

class GPUManager:
    def __init__(self, idle_timeout=60):
        self.model = None
        self.last_used = time.time()
        self.idle_timeout = idle_timeout
        self.lock = threading.Lock()
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()
    
    def get_model(self, load_func):
        with self.lock:
            if self.model is None:
                self.model = load_func()
            self.last_used = time.time()
            return self.model
    
    def _monitor(self):
        while True:
            time.sleep(10)
            with self.lock:
                if self.model and (time.time() - self.last_used) > self.idle_timeout:
                    self._offload()
    
    def _offload(self):
        if self.model:
            del self.model
            self.model = None
            torch.cuda.empty_cache()
    
    def force_offload(self):
        with self.lock:
            self._offload()
    
    def get_status(self):
        with self.lock:
            return {
                'loaded': self.model is not None,
                'idle_time': time.time() - self.last_used if self.model else 0
            }

gpu_manager = GPUManager(idle_timeout=int(os.getenv('GPU_IDLE_TIMEOUT', 60)))
