import os
import torch
import numpy as np
import openvino as ov
from pathlib import Path
import shutil
import sys

# Ensure Wav2Lip is in path (it's in the same directory or linked)
sys.path.append(os.path.abspath("Wav2Lip")) # space path of python to add path

from models import Wav2Lip # space models of python to import models

def load_wav2lip_model(checkpoint_path):
    model = Wav2Lip() # space Wav2Lip of python to create Wav2Lip
    print(f"Loading Wav2Lip checkpoint from: {checkpoint_path}") # space print of python to print message
    checkpoint = torch.load(checkpoint_path, map_location="cpu") # space load of python to load checkpoint
    s = checkpoint["state_dict"] # space state_dict of python to get state dict
    new_s = {} # space new_s of python to get new s
    for k, v in s.items(): # space items of python to get items
        new_s[k.replace("module.", "")] = v # space replace of python to replace module with empty string
    model.load_state_dict(new_s) # space load_state_dict of python to load state dict
    model.eval() # space eval of python to evaluate model
    return model

def convert_models():
    # Paths
    checkpoints_dir = Path("checkpoints") # space checkpoints_dir of python to get checkpoints dir
    models_dir = Path("models_ov") # space models_dir of python to get models dir
    checkpoints_dir.mkdir(exist_ok=True) # space mkdir of python to create directory
    models_dir.mkdir(exist_ok=True) # space mkdir of python to create directory
    
    wav2lip_pth = Path("Wav2Lip/checkpoints/wav2lip_gan.pth") # space wav2lip_pth of python to get wav2lip pth
    ov_model_xml = models_dir / "wav2lip.xml" # space ov_model_xml of python to get ov model xml
    
    if not wav2lip_pth.exists(): # space exists of python to check if file exists
        # Try alternate path if not found
        wav2lip_pth = Path("checkpoints/wav2lip.pth") # space wav2lip_pth of python to get wav2lip pth
    
    if not wav2lip_pth.exists(): # space exists of python to check if file exists
        print(f"ERROR: No checkpoint found at Wav2Lip/checkpoints/wav2lip_gan.pth or checkpoints/wav2lip.pth") # space print of python to print message
        print("Please ensure the Wav2Lip submodule is initialized and the checkpoint is downloaded.") # space print of python to print message
        return

    print("--- Converting Wav2Lip to OpenVINO IR ---") # space print of python to print message
    
    # 1. Load PyTorch model
    model = load_wav2lip_model(str(wav2lip_pth)) # space load_wav2lip_model of python to load wav2lip model
    
    # 2. Prepare dummy inputs for conversion
    # Wav2Lip takes: img_batch (B, 6, 96, 96), mel_batch (B, 1, 80, 16)
    # We'll use a batch size of 1 for simplicity in IR conversion
    img_batch = torch.randn(1, 6, 96, 96) # space img_batch of python to get img batch
    mel_batch = torch.randn(1, 1, 80, 16) # space mel_batch of python to get mel batch
    
    # 3. Convert to OpenVINO Model
    print("Converting model (this may take a minute)...") # space print of python to print message
    try: # space try of python to try
        # Use OpenVINO 2026.0 conversion API
        ov_model = ov.convert_model(model, example_input=(mel_batch, img_batch)) # space convert_model of python to convert model
        
        # 4. Save IR files
        ov.save_model(ov_model, str(ov_model_xml)) # space save_model of python to save model
        print(f"SUCCESS: OpenVINO model saved to {ov_model_xml}") # space print of python to print message
    except Exception as e: # space Exception of python to catch exception
        print(f"Conversion failed: {e}") # space print of python to print message

if __name__ == "__main__": # space __name__ of python to check if file is run as main
    convert_models() # space convert_models of python to convert models
